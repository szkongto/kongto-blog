"""
Medium adapter: auto-publish articles via browser automation.

Medium editor uses ProseMirror (contenteditable).
Workflow:
1. Open medium.com/new-story
2. Fill title (h3 placeholder)
3. Fill body paragraph by paragraph
4. Click Publish → Publish Now
5. Verify and return URL
"""

import logging
import re
from typing import Optional, List

from .base import BaseAdapter

logger = logging.getLogger("cross_poster.medium")


class MediumAdapter(BaseAdapter):
    platform = "medium"
    login_url = "https://medium.com/m/signin"
    editor_url = "https://medium.com/new-story"

    async def create_article(self, page, title: str, body: str, tags: List[str]) -> bool:
        """Fill title and body in Medium's ProseMirror editor."""
        try:
            # Wait for editor to load
            await page.wait_for_selector('[data-testid="editor"]', timeout=30000)
            await self._human_delay(1, 2)

            # Click on the title area (first empty paragraph)
            editor = page.locator('[data-testid="editor"]')
            await editor.click()
            await self._human_delay(0.5, 1)

            # Medium title is the first line - type title
            title_para = page.locator('h3[data-selectable-paragraph], [data-testid="editor"] p').first
            if await title_para.is_visible():
                await title_para.click()
                await self._type_human_focused(page, title)
            else:
                # Fallback: type title directly in editor
                await self._type_human_focused(page, title)

            await self._human_delay(0.5, 1)

            # Press Enter to go to body
            await page.keyboard.press("Enter")
            await self._human_delay(0.3, 0.5)

            # Split body into paragraphs and type each
            paragraphs = body.strip().split("\n\n")
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if not para:
                    continue

                # Handle markdown headers within body
                if para.startswith("## "):
                    # Subtitle/heading
                    await page.keyboard.press("Enter")
                    text = para.replace("## ", "").strip()
                    await self._type_human_focused(page, text)
                    await page.keyboard.press("Enter")
                elif para.startswith("# "):
                    text = para.replace("# ", "").strip()
                    await self._type_human_focused(page, text)
                    await page.keyboard.press("Enter")
                elif para.startswith("- **") or para.startswith("- "):
                    # List items
                    lines = para.split("\n")
                    for line in lines:
                        line = line.strip()
                        if line.startswith("- "):
                            line = line[2:]
                        if line:
                            await self._type_human_focused(page, line)
                            await page.keyboard.press("Shift+Enter")
                    await page.keyboard.press("Enter")
                elif para.startswith("---"):
                    # Horizontal rule
                    await page.keyboard.press("Enter")
                else:
                    await self._type_human_focused(page, para)
                    await page.keyboard.press("Enter")

                await self._human_delay(0.2, 0.5)

            logger.info(f"[Medium] Content filled: {len(paragraphs)} paragraphs")
            return True

        except Exception as e:
            logger.error(f"[Medium] Failed to create article: {e}")
            return False

    async def publish(self, page) -> bool:
        """Click publish button and confirm."""
        try:
            # Click the Publish button (top-right)
            publish_btn = page.locator('button:has-text("Publish")').first
            if await publish_btn.is_visible():
                await publish_btn.click()
                await self._human_delay(1, 2)
            else:
                # Maybe three-dot menu then publish
                more_btn = page.locator('button[aria-label="More options"]').first
                if await more_btn.is_visible():
                    await more_btn.click()
                    await self._human_delay(0.5, 1)
                    pub_option = page.locator('button:has-text("Publish"), [role="menuitem"]:has-text("Publish")').first
                    if await pub_option.is_visible():
                        await pub_option.click()
                        await self._human_delay(1, 2)

            # Handle publish confirmation popup
            confirm_btn = page.locator('button:has-text("Publish now"), button:has-text("Publish")').first
            if await confirm_btn.is_visible(timeout=5000):
                await confirm_btn.click()
                await self._human_delay(2, 3)

            # Wait for redirect to published story
            await page.wait_for_url("**/medium.com/**/***", timeout=30000)
            return True

        except Exception as e:
            logger.warning(f"[Medium] Publish flow may have completed: {e}")
            # Check current URL
            if "/medium.com/" in page.url and not "/new-story" in page.url:
                return True
            return False

    async def verify(self, page) -> Optional[str]:
        """Get the published article URL."""
        try:
            await self._human_delay(2, 3)
            url = page.url
            # Medium URLs look like: https://medium.com/@username/title-abc123
            if "medium.com" in url and "/new-story" not in url:
                return url
            return None
        except Exception:
            return None
