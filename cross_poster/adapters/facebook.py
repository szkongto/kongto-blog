"""
Facebook adapter: auto-publish articles to Facebook Notes or Page.

Two approaches:
1. Facebook Notes (personal): facebook.com/notes/
2. Facebook Page (business): /your-page/notes/

Note: Facebook's interface changes frequently. This adapter targets
the Notes section. For Page publishing, a Graph API token is more reliable.
"""

import logging
from typing import Optional, List

from .base import BaseAdapter

logger = logging.getLogger("cross_poster.facebook")


class FacebookAdapter(BaseAdapter):
    platform = "facebook"
    login_url = "https://www.facebook.com/"
    editor_url = "https://www.facebook.com/notes/"

    async def create_article(self, page, title: str, body: str, tags: List[str]) -> bool:
        """Create a Facebook Note."""
        try:
            await self._human_delay(2, 3)

            # Look for "Create Note" or "Write a note" button
            create_btn = page.locator(
                'a:has-text("Create Note"), a:has-text("Write Note"), '
                'a[href*="/notes/"], button:has-text("Create Note")'
            ).first

            if await create_btn.is_visible(timeout=15000):
                await create_btn.click()
                await self._human_delay(2, 3)
            else:
                # Maybe we're already on the notes page
                logger.info("[Facebook] Looking for note editor...")

            # Look for title input
            title_field = page.locator('[contenteditable="true"]').first
            if await title_field.is_visible(timeout=10000):
                await title_field.click()
                await self._type_human_focused(page, title)
                await self._human_delay(0.5, 1)

            # Press Tab or Enter to go to body
            await page.keyboard.press("Tab")
            await self._human_delay(0.5, 1)

            # Type body paragraph by paragraph
            for para in body.split("\n\n"):
                para = para.strip()
                if not para:
                    continue
                if para.startswith("#") or para.startswith("-"):
                    para = para.lstrip("#- ").strip()
                if para:
                    await self._type_human_focused(page, para[:1000])
                    await page.keyboard.press("Enter")
                    await page.keyboard.press("Enter")
                await self._human_delay(0.2, 0.4)

            logger.info("[Facebook] Content filled")
            return True

        except Exception as e:
            logger.error(f"[Facebook] Failed to create article: {e}")
            return False

    async def publish(self, page) -> bool:
        """Click Publish/Post button."""
        try:
            # Look for Publish/Post/Share button
            publish_btn = page.locator(
                'button:has-text("Publish"), button:has-text("Post"), '
                'button:has-text("Share Now"), button:has-text("Share")'
            ).first

            if await publish_btn.is_visible(timeout=10000):
                await publish_btn.click()
                await self._human_delay(3, 5)
                return True

            logger.warning("[Facebook] No publish button found")
            return False

        except Exception as e:
            logger.warning(f"[Facebook] Publish: {e}")
            return False

    async def verify(self, page) -> Optional[str]:
        """Get published note URL."""
        try:
            await self._human_delay(3, 5)
            current_url = page.url

            if "facebook.com" in current_url and "notes" in current_url:
                return current_url

            # Check for posted note link
            note_link = page.locator('a[href*="/notes/"]').first
            if await note_link.is_visible(timeout=5000):
                href = await note_link.get_attribute("href")
                if href:
                    return f"https://www.facebook.com{href}" if href.startswith("/") else href

            return current_url if "facebook.com" in current_url else None

        except Exception as e:
            logger.warning(f"[Facebook] Verify: {e}")
            return None
