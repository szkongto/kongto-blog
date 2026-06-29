"""
Session manager: persistent browser context + cookie storage per platform.

Each platform gets:
  - `sessions/{platform}_storage.json` — Playwright storage_state (cookies + localStorage)
  - `browser_profile_{platform}/` — persistent browser user data dir

First run: opens browser for manual login → saves state
Subsequent runs: loads saved state → verifies → reuses if valid
"""

import json
import os
import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, BrowserContext

from .config import SESSIONS_DIR, VIEWPORT, USER_AGENTS

logger = logging.getLogger("cross_poster.session")

# Platform-specific user data dirs (relative to sessions dir)
PROFILE_DIRS = {}


def _storage_path(platform: str) -> str:
    """Path to saved storage_state JSON."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return os.path.join(SESSIONS_DIR, f"{platform}_storage.json")


def _profile_dir(platform: str) -> str:
    """Path to persistent browser profile dir."""
    d = os.path.join(SESSIONS_DIR, f"browser_profile_{platform}")
    os.makedirs(d, exist_ok=True)
    return d


def _has_saved_session(platform: str) -> bool:
    """Check if a saved session file exists."""
    return os.path.exists(_storage_path(platform))


async def load_or_login(platform: str, login_url: str, headless: bool = False) -> BrowserContext:
    """
    Load saved session or guide user through manual login.

    Args:
        platform: Platform name (used for storage key)
        login_url: URL to navigate to for login
        headless: Whether to run browser headless

    Returns:
        Playwright BrowserContext with authenticated session
    """
    storage_path = _storage_path(platform)
    profile = _profile_dir(platform)

    pw = await async_playwright().start()
    context = await pw.chromium.launch_persistent_context(
        profile,
        headless=headless,
        viewport=VIEWPORT,
        user_agent=random.choice(USER_AGENTS) if USER_AGENTS else None,
        locale="zh-CN" if login_url in [
            "https://www.zhihu.com/signin",
            "https://baijiahao.baidu.com/",
            "https://passport.csdn.net/login",
        ] else "en-US",
        timeout=60000,
    )

    # Try loading saved storage state
    if _has_saved_session(platform):
        try:
            with open(storage_path, "r") as f:
                state = json.load(f)
            await context.add_cookies(state.get("cookies", []))
            # Also set localStorage if available
            if state.get("origins"):
                page = await context.new_page()
                for origin in state["origins"]:
                    await page.goto(origin.get("origin", "about:blank"), wait_until="domcontentloaded")
                    for item in origin.get("localStorage", []):
                        try:
                            await page.evaluate(
                                "window.localStorage.setItem(arguments[0], arguments[1])",
                                item.get("name", ""), item.get("value", ""),
                            )
                        except Exception:
                            pass
                await page.close()
            logger.info(f"[{platform}] Loaded saved session")
        except Exception as e:
            logger.warning(f"[{platform}] Failed to load session: {e}")

    # Verify session
    page = await context.new_page()
    try:
        await page.goto(login_url, wait_until="domcontentloaded", timeout=30000)

        # Quick check: if we're on the login page, we need manual login
        current_url = page.url
        if _is_login_page(current_url, login_url, platform):
            logger.info(f"[{platform}] Session expired or no session - manual login needed")
            print(f"\n  [{platform}] 浏览器已打开，请在浏览器中扫码/登录")
            print(f"  登录完成后，回到这里按 Enter 继续...\n")
            # Use input() in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: input("  → 按 Enter 继续... "))
            logger.info(f"[{platform}] Manual login completed")
        else:
            logger.info(f"[{platform}] Session valid, already logged in")
    except Exception as e:
        logger.warning(f"[{platform}] Session check failed: {e}")
    finally:
        await page.close()

    return context, pw


async def save_session(context: BrowserContext, platform: str):
    """Save current browser context state."""
    storage_path = _storage_path(platform)
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)

    state = await context.storage_state()
    with open(storage_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    logger.info(f"[{platform}] Session saved to {storage_path}")


def _is_login_page(current_url: str, login_url: str, platform: str) -> bool:
    """Determine if the current page is still the login page."""
    # Platform-specific login page indicators
    login_indicators = {
        "zhihu": ["signin", "login"],
        "baijiahao": ["login", "passport"],
        "csdn": ["login", "passport"],
        "medium": ["signin", "m/signin"],
        "linkedin": ["login", "checkpoint"],
        "facebook": ["login", "checkpoint"],
    }

    indicators = login_indicators.get(platform, ["login", "signin"])
    return any(ind in current_url.lower() for ind in indicators)


import random  # noqa: E402 (needed for user-agent selection)
