"""
LinkedIn adapter: auto-publish long-form articles via browser.

LinkedIn article editor:
- URL: linkedin.com/post/new/
- Title field at top
- Body is a rich text editor (ProseMirror-like)
- Has image cover selection
- Click "Publish" button in top toolbar
"""

import logging
from typing import Optional, List

from .base import BaseAdapter

logger = logging.getLogger("cross_poster.linkedin")


class LinkedInAdapter(BaseAdapter):
    platform = "linkedin"
    login_url = "https://www.linkedin.com/login"
    editor_url = "https://www.linkedin.com/post/new/"

    async def create_article(self, page, title: str, body: str, tags: List[str]) -> bool:
        """Fill title and body in LinkedIn's article editor."""
        try:
            await self._human_delay(2, 3)

            # Wait for editor to load
            await page.wait_for_selector('[data-article-editor="title"]', timeout=30000)
            await self._human_delay(1, 2)

            # Fill title
            title_field = page.locator('[data-article-editor="title"]')
            if await title_field.is_visible():
                await title_field.click()
                await self._type_human_focused(page, title)
                await self._human_delay(0.5, 1)

            # Fill body - click into the body editor area
            body_editor = page.locator('[data-article-editor="editor"]')
            if await body_editor.is_visible():
                await body_editor.click()
                await self._human_delay(0.5, 1)

                paragraphs = body.strip().split("\n\n")
                for i, para in enumerate(paragraphs):
                    para = para.strip()
                    if not para:
                        continue

                    # Handle markdown headers
                    if para.startswith("## "):
                        text = para.replace("## ", "").strip()
                        await self._type_human_focused(page, text)
                        await page.keyboard.press("Enter")
                        await page.keyboard.press("Enter")
                    elif para.startswith("# "):
                        text = para.replace("# ", "").strip()
                        await self._type_human_focused(page, text)
                        await page.keyboard.press("Enter")
                    elif para.startswith("- "):
                        lines = para.split("\n")
                        for line in lines:
                            line = line.strip()
                            if line.startswith("- "):
                                line = line[2:]
                            if line:
                                await self._type_human_focused(page, f"• {line}")
                                await page.keyboard.press("Shift+Enter")
                        await page.keyboard.press("Enter")
                    elif para.startswith("---"):
                        continue
                    else:
                        await self._type_human_focused(page, para)
                        await page.keyboard.press("Enter")

                    await self._human_delay(0.2, 0.5)
            else:
                # Fallback: try clicking main content area
                await page.click('[contenteditable="true"]')
                await self._human_delay(0.5, 1)
                for para in body.split("\n\n"):
                    para = para.strip()
                    if para:
                        await self._type_human_focused(page, para[:500])
                        await page.keyboard.press("Enter")
                    await self._human_delay(0.2, 0.3)

            # Add hashtags at the end
            if tags:
                for tag in tags[:3]:
                    await self._type_human_focused(page, f" #{tag}")
                await page.keyboard.press("Enter")

            logger.info(f"[LinkedIn] Content filled")
            return True

        except Exception as e:
            logger.error(f"[LinkedIn] Failed to create article: {e}")
            return False

    async def publish(self, page) -> bool:
        """Click Publish button."""
        try:
            # Try main Publish button in toolbar
            publish_btn = page.locator('button:has-text("Publish"), button:has-text("Post")').first
            if await publish_btn.is_visible(timeout=10000):
                await publish_btn.click()
                await self._human_delay(2, 3)
                return True

            # Try "Next" button then publish
            next_btn = page.locator('button:has-text("Next")').first
            if await next_btn.is_visible(timeout=5000):
                await next_btn.click()
                await self._human_delay(1, 2)
                pub_btn = page.locator('button:has-text("Publish")').first
                if await pub_btn.is_visible(timeout=5000):
                    await pub_btn.click()
                    await self._human_delay(2, 3)
                    return True

            return False

        except Exception as e:
            logger.warning(f"[LinkedIn] Publish flow: {e}")
            return False

    async def verify(self, page) -> Optional[str]:
        """Get published article URL."""
        try:
            await self._human_delay(3, 5)

            # After publishing, LinkedIn redirects to the article or profile
            url = page.url
            if "linkedin.com" in url:
                if "/pulse/" in url or "/posts/" in url:
                    return url
                # Check for "View article" link
                view_link = page.locator('a:has-text("View article")').first
                if await view_link.is_visible(timeout=5000):
                    href = await view_link.get_attribute("href")
                    if href:
                        full_url = href if href.startswith("http") else f"https://www.linkedin.com{href}"
                        return full_url

            return url if "linkedin.com" in url else None

        except Exception as e:
            logger.warning(f"[LinkedIn] Verify: {e}")
            return None
