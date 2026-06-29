"""
Base adapter for all publishing platforms.

Flow: fill content → auto-publish → verify → keep browser open for user check
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, List

from ..config import MAX_RETRIES, RETRY_DELAY
from ..session import load_or_login, save_session

logger = logging.getLogger("cross_poster.adapter")


class BaseAdapter(ABC):
    """Base class for platform-specific publishing adapters."""

    platform: str = ""
    login_url: str = ""
    editor_url: str = ""

    def __init__(self):
        self.context = None
        self.playwright = None

    @abstractmethod
    async def create_article(self, page, title: str, body: str, tags: List[str]) -> bool:
        """Fill in the article content in the editor."""
        ...

    @abstractmethod
    async def publish(self, page) -> bool:
        """Click publish/submit button."""
        ...

    @abstractmethod
    async def verify(self, page) -> Optional[str]:
        """Verify article was published, return its URL."""
        ...

    async def run(self, title: str, body: str, tags: Optional[List[str]] = None) -> Optional[str]:
        tags = tags or []

        for attempt in range(MAX_RETRIES):
            try:
                self.context, self.playwright = await load_or_login(
                    self.platform, self.login_url, headless=False
                )

                page = await self.context.new_page()

                # Navigate to editor
                logger.info(f"[{self.platform}] Navigating to editor: {self.editor_url}")
                await page.goto(self.editor_url, wait_until="domcontentloaded", timeout=60000)
                await self._human_delay(1, 3)

                # Create article
                logger.info(f"[{self.platform}] Creating article: {title[:50]}...")
                success = await self.create_article(page, title, body, tags)
                if not success:
                    raise Exception("Failed to create article content")

                await self._human_delay(2, 3)

                # Publish
                logger.info(f"[{self.platform}] Publishing...")
                published = await self.publish(page)
                if not published:
                    await self._human_delay(3, 5)
                    published = await self.publish(page)

                if not published:
                    raise Exception("Publish action failed")

                await self._human_delay(3, 5)

                # Verify
                article_url = await self.verify(page)
                if article_url:
                    logger.info(f"[{self.platform}] Published successfully: {article_url}")
                    return article_url
                else:
                    logger.warning(f"[{self.platform}] Published but couldn't verify URL")

                return article_url or f"{self.platform} published, no URL"

            except Exception as e:
                logger.error(f"[{self.platform}] Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"[{self.platform}] Retrying in {RETRY_DELAY // 60} min...")
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    return None
            finally:
                try:
                    if self.context:
                        await save_session(self.context, self.platform)
                        # Keep browser open 60s for user to verify result
                        print(f"\n  [{self.platform}] 发布完成！浏览器保持打开60秒供验证")
                        print(f"  检查文章是否发布成功，然后告诉我结果", flush=True)
                        await asyncio.sleep(60)
                        await self.context.close()
                    if self.playwright:
                        await self.playwright.stop()
                except Exception:
                    pass

    async def _human_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        import random
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def _type_human_focused(self, page, text: str):
        import random
        for char in text:
            await page.keyboard.type(char, delay=random.randint(30, 120))
