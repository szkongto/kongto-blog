"""
CSDN adapter: publish articles via browser.

CSDN editor structure (confirmed by diagnosis):
  - Title: textarea#txtTitle (placeholder: 请输入文章标题)
  - Body: iframe (WYSIWYG rich text editor)
  - Tags: input#el_mcm-id-xxxx (placeholder: 按Enter添加自定义标签)
  - Summary: textarea#txtSammary
  - Publish: <button>发布文章
  - Save draft: <button>保存草稿
"""

import logging
import re
import asyncio
from typing import Optional, List

from .base import BaseAdapter

logger = logging.getLogger("cross_poster.csdn")


class CSDNAdapter(BaseAdapter):
    platform = "csdn"
    login_url = "https://passport.csdn.net/login"
    editor_url = "https://mp.csdn.net/mp_blog/creation/editor"

    async def create_article(self, page, title: str, body: str, tags: List[str]) -> bool:
        """Fill CSDN editor."""
        try:
            await self._human_delay(2, 3)

            # Wait for editor to fully load
            await page.wait_for_selector("#txtTitle", timeout=30000)
            await self._human_delay(2, 3)

            # ==== 1. Fill Title ====
            title_field = page.locator("#txtTitle")
            if await title_field.is_visible():
                await title_field.click()
                await self._human_delay(0.3, 0.5)
                await title_field.fill(title)
                logger.info(f"[CSDN] Title filled: {title[:50]}...")
            await self._human_delay(0.5, 1)

            # ==== 2. Fill Body (inside iframe) ====
            body_filled = await self._fill_body_via_iframe(page, body)
            if not body_filled:
                logger.warning("[CSDN] Body fill via iframe failed, trying fallback")
                body_filled = await self._fill_body_fallback(page, body)

            if not body_filled:
                logger.error("[CSDN] Could not fill body content")
                return False

            await self._human_delay(1, 2)

            # ==== 3. Set tags ====
            await self._set_tags(page, tags)

            logger.info("[CSDN] Content filled successfully")
            return True

        except Exception as e:
            logger.error(f"[CSDN] Failed to create article: {e}")
            return False

    async def _fill_body_via_iframe(self, page, body: str) -> bool:
        """Fill body content in the WYSIWYG editor iframe."""
        try:
            # Find the editor iframe - get it via evaluate to get the real contentWindow
            iframe_element = page.locator("iframe").first
            if not await iframe_element.is_visible(timeout=5000):
                return False

            # Click inside the iframe body to focus it
            await iframe_element.click()
            await self._human_delay(1, 2)

            # Use evaluate to directly set innerHTML of the editor body
            # This is more reliable than typing character by character
            import html as html_mod
            escaped_body = html_mod.escape(body.replace("\n\n", "</p><p>").replace("\n", "<br>"))
            html_content = f"<p>{escaped_body}</p>"

            html_body = body.replace("\n\n", "<p></p>").replace("\n", "<br>")
            result = await page.evaluate(
                """(content) => {
                    const iframe = document.querySelector('iframe');
                    if (!iframe) return false;
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    const editor = doc.querySelector('[contenteditable="true"], body, .ql-editor, .ProseMirror');
                    if (!editor) return false;
                    editor.innerHTML = content;
                    // Trigger change events so editor detects content
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                    editor.dispatchEvent(new Event('change', { bubbles: true }));
                    editor.dispatchEvent(new Event('keyup', { bubbles: true }));
                    return true;
                }""",
                html_body
            )
            if result:
                logger.info("[CSDN] Body filled via iframe JS injection")
                return True
            return False

            logger.info("[CSDN] Body filled via iframe JS injection")
            return True

        except Exception as e:
            logger.warning(f"[CSDN] Iframe body fill error: {e}")
            return False

    async def _type_into_frame(self, frame, text: str):
        """Type text paragraph by paragraph into an iframe."""
        import random
        paragraphs = text.split("\n\n")
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue

            if para.startswith("## "):
                para = para.replace("## ", "").strip()
            elif para.startswith("# "):
                para = para.replace("# ", "").strip()
            elif para.startswith("- "):
                lines = para.split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("- "):
                        line = line[2:]
                    if line:
                        await frame.keyboard.type(line, delay=random.randint(30, 60))
                        await frame.keyboard.press("Shift+Enter")
                await frame.keyboard.press("Enter")
                continue
            elif para.startswith("---"):
                continue

            if para:
                await frame.keyboard.type(para[:3000], delay=random.randint(20, 50))
                await frame.keyboard.press("Enter")

            await asyncio.sleep(random.uniform(0.2, 0.5))

    async def _fill_body_fallback(self, page, body: str) -> bool:
        """Fallback: try typing into visible contenteditable or textarea."""
        try:
            import random

            # Try the page-level contenteditable
            editor = page.locator('[contenteditable="true"]').last
            if await editor.is_visible(timeout=3000):
                await editor.click()
                for para in body.split("\n\n"):
                    para = para.strip()
                    if para and not para.startswith("---"):
                        clean = re.sub(r"^#{1,2}\s+", "", para)
                        clean = re.sub(r"^- ", "", clean, flags=re.MULTILINE)
                        for char in clean[:3000]:
                            await page.keyboard.type(char, delay=random.randint(20, 50))
                        await page.keyboard.press("Enter")
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                return True

            return False

        except Exception as e:
            logger.warning(f"[CSDN] Fallback body fill error: {e}")
            return False

    async def _set_tags(self, page, tags: List[str]):
        """Set CSDN tags."""
        try:
            tag_input = page.locator('input[placeholder*="标签"], input[placeholder*="Enter"]').first
            if await tag_input.is_visible(timeout=3000):
                for tag in tags[:3]:
                    await tag_input.click()
                    await tag_input.fill(tag)
                    await self._human_delay(0.3, 0.5)
                    await page.keyboard.press("Enter")
                    await self._human_delay(0.3, 0.5)
        except Exception:
            pass

    async def publish(self, page) -> bool:
        """Click publish button. Button text: 发布博客 (NOT 定时发布)."""
        try:
            await self._human_delay(2, 3)

            # Scroll into view if needed
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._human_delay(1, 2)

            # Find button with exact text "发布博客"
            all_btns = page.locator('button, .el_mcm-button, [class*="btn"]')
            count = await all_btns.count()
            for i in range(count):
                text = (await all_btns.nth(i).text_content() or "").strip()
                if text == "发布博客" or text == "发布博客":
                    await all_btns.nth(i).click()
                    await self._human_delay(5, 8)
                    logger.info("[CSDN] Clicked: 发布博客")
                    return True

            # Fallback: last primary button
            primary = page.locator('.el_mcm-button--primary')
            pc = await primary.count()
            if pc > 0:
                await primary.nth(pc - 1).click()
                await self._human_delay(5, 8)
                return True

            logger.warning("[CSDN] No publish button found")
            return False

        except Exception as e:
            logger.warning(f"[CSDN] Publish error: {e}")
            return False

    async def verify(self, page) -> Optional[str]:
        """Get published article URL."""
        try:
            await self._human_delay(3, 5)
            url = page.url

            if "blog.csdn.net" in url and "/article/details/" in url:
                return url

            article_link = page.locator('a[href*="/article/details/"]').first
            if await article_link.is_visible(timeout=5000):
                href = await article_link.get_attribute("href")
                if href:
                    return href if href.startswith("http") else f"https:{href}"

            return url if "blog.csdn.net" in url else None

        except Exception as e:
            logger.warning(f"[CSDN] Verify error: {e}")
            return None
