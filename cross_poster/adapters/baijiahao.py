"""
Bai Jia Hao (百家号) adapter: publish articles to Baidu's content platform.

百家号 is the most restrictive platform:
- Requires real-name verified Baidu account
- Strict anti-bot detection (WAF + captcha)
- Complex submission flow with image uploads
- Content review process (not instant publish)
- Rich text editor with custom components

Strategy: semi-automated (open browser + fill content, manual final steps if needed)
"""

import logging
from typing import Optional, List

from .base import BaseAdapter

logger = logging.getLogger("cross_poster.baijiahao")


class BaijiahaoAdapter(BaseAdapter):
    platform = "baijiahao"
    login_url = "https://baijiahao.baidu.com/"
    editor_url = "https://baijiahao.baidu.com/write"

    async def create_article(self, page, title: str, body: str, tags: List[str]) -> bool:
        """Fill Baijiahao editor."""
        try:
            await self._human_delay(3, 5)

            # Wait for the editor to fully load
            await page.wait_for_selector('[contenteditable="true"], .editor-content, #ueditor', timeout=60000)
            await self._human_delay(2, 3)

            # Fill title
            title_field = page.locator(
                'input[placeholder*="标题"], .article-title-input, '
                'div[placeholder*="标题"], [contenteditable="true"]'
            ).first

            if await title_field.is_visible(timeout=15000):
                await title_field.click()
                await self._human_delay(0.5, 1)

                # Type title character by character (百家号 detects paste)
                for char in title:
                    await page.keyboard.type(char, delay=50)
                await self._human_delay(1, 2)

            # Press Tab to body
            await page.keyboard.press("Tab")
            await self._human_delay(1, 2)

            # Type body paragraph by paragraph
            paragraphs = body.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # Skip markdown formatting characters for rich text
                if para.startswith("## "):
                    para = para[3:]
                elif para.startswith("# "):
                    para = para[2:]
                elif para.startswith("- "):
                    lines = para.split("\n")
                    for line in lines:
                        line = line.strip()
                        if line.startswith("- "):
                            line = line[2:]
                        if line:
                            for char in line:
                                await page.keyboard.type(char, delay=30)
                            await page.keyboard.press("Shift+Enter")
                    await page.keyboard.press("Enter")
                    continue
                elif para.startswith("---"):
                    continue

                # Type the paragraph with human-like speed
                for char in para[:2000]:
                    await page.keyboard.type(char, delay=30)
                await page.keyboard.press("Enter")
                await self._human_delay(0.3, 0.8)

            logger.info("[百家号] Content filled")
            return True

        except Exception as e:
            logger.error(f"[百家号] Failed to create article: {e}")
            return False

    async def publish(self, page) -> bool:
        """Submit for review."""
        try:
            # 百家号 has a "Submit for Review" button (提交审核)
            publish_btn = page.locator(
                'button:has-text("提交审核"), button:has-text("发布"), '
                'button:has-text("发表"), .publish-btn'
            ).first

            if await publish_btn.is_visible(timeout=15000):
                await self._human_delay(1, 2)
                await publish_btn.click()
                await self._human_delay(3, 5)

                # 百家号 often shows a confirmation popup
                confirm_btn = page.locator(
                    'button:has-text("确认"), button:has-text("确定"), '
                    'button:has-text("提交")'
                ).first
                if await confirm_btn.is_visible(timeout=10000):
                    await confirm_btn.click()
                    await self._human_delay(2, 3)

                logger.info("[百家号] Article submitted for review")
                return True

            # If no publish button found, maybe still loading or has captcha
            logger.warning("[百家号] No publish button - possible captcha or page issue")
            return False

        except Exception as e:
            logger.warning(f"[百家号] Publish: {e}")
            return False

    async def verify(self, page) -> Optional[str]:
        """Get submission status."""
        try:
            await self._human_delay(3, 5)

            url = page.url

            # 百家号 doesn't immediately show the article URL
            # Article goes through review first
            if "baijiahao.baidu.com" in url:
                # Check for success message
                success = page.locator('text=提交成功, text=审核中, text=发布成功').first
                if await success.is_visible(timeout=5000):
                    logger.info("[百家号] Article submitted to review queue")

                # Try to get the article ID from URL
                import re
                match = re.search(r"article/(\d+)", url)
                if match:
                    return f"https://baijiahao.baidu.com/article/{match.group(1)}"

                return url

            return None

        except Exception as e:
            logger.warning(f"[百家号] Verify: {e}")
            return None
