"""
Zhihu adapter: publish articles to Zhuanlan (知乎专栏).

知乎编辑器:
- URL: zhuanlan.zhihu.com/write
- Title: div[contenteditable] or input with placeholder="标题"
- Body: Rich text editor (contenteditable div)
- Publish: button with text "发布"
"""

import logging
from typing import Optional, List

from .base import BaseAdapter

logger = logging.getLogger("cross_poster.zhihu")


class ZhihuAdapter(BaseAdapter):
    platform = "zhihu"
    login_url = "https://www.zhihu.com/signin"
    editor_url = "https://zhuanlan.zhihu.com/write"

    async def create_article(self, page, title: str, body: str, tags: List[str]) -> bool:
        """Fill Zhihu editor."""
        try:
            await self._human_delay(3, 4)

            # Wait for editor to load
            await page.wait_for_selector('[contenteditable="true"]', timeout=30000)
            await self._human_delay(2, 3)

            # ==== Fill Title ====
            title_field = page.locator(
                '.WriteIndex-titleInput, '
                'div[placeholder*="标题"], '
                'input[placeholder*="标题"]'
            ).first

            if not await title_field.is_visible(timeout=5000):
                # Fallback: first contenteditable
                title_field = page.locator('[contenteditable="true"]').first

            if await title_field.is_visible():
                await title_field.click()
                await self._human_delay(0.3, 0.5)
                await title_field.fill(title)
                logger.info(f"[Zhihu] Title filled: {title[:50]}...")

            await self._human_delay(1, 2)

            # ==== Fill Body ====
            body_filled = await self._fill_body(page, body)
            if not body_filled:
                logger.error("[Zhihu] Could not fill body content")
                return False

            logger.info("[Zhihu] Content filled")
            return True

        except Exception as e:
            logger.error(f"[Zhihu] Failed to create article: {e}")
            return False

    async def _fill_body(self, page, body: str) -> bool:
        """Fill body content via JS injection for speed."""
        try:
            # Get all contenteditable divs
            editors = page.locator('[contenteditable="true"]')
            count = await editors.count()

            if count == 0:
                return False

            # Body is typically the LAST contenteditable (after title)
            body_idx = count - 1 if count > 1 else 0
            body_field = editors.nth(body_idx)

            if not await body_field.is_visible():
                return False

            # Click to focus
            await body_field.click()
            await self._human_delay(0.5, 1)

            # Close any cover image popup that might be blocking
            try:
                close_btn = page.locator('button[class*="close"], [class*="modal"] button, [aria-label*="关闭"]').first
                if await close_btn.is_visible(timeout=3000):
                    await close_btn.click()
                    await self._human_delay(0.5, 1)
            except Exception:
                pass

            # Use JS to inject content - faster than typing
            paragraphs = body.split("\n\n")
            html_parts = []
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if para.startswith("## "):
                    html_parts.append(f"<h2>{para[3:]}</h2>")
                elif para.startswith("# "):
                    html_parts.append(f"<h1>{para[2:]}</h1>")
                elif para.startswith("- "):
                    html_parts.append(f"<p>{para}</p>")
                elif para.startswith("---"):
                    html_parts.append("<hr>")
                else:
                    # Escape HTML in paragraph
                    safe = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                    html_parts.append(f"<p>{safe}</p>")

            html_content = "".join(html_parts)

            # Use clipboard API to paste content (works with Draft.js editors)
            try:
                # Copy content to clipboard via JS
                await page.evaluate(
                    """(text) => {
                        const ta = document.createElement('textarea');
                        ta.value = text;
                        document.body.appendChild(ta);
                        ta.select();
                        document.execCommand('copy');
                        document.body.removeChild(ta);
                    }""",
                    body
                )
                await self._human_delay(0.3, 0.5)

                # Focus the editor
                await body_field.click()
                await self._human_delay(0.5, 1)

                # Select all and paste
                await page.keyboard.press("Control+A")
                await self._human_delay(0.3, 0.5)
                await page.keyboard.press("Control+V")
                await self._human_delay(1, 2)

                # Check if content was detected
                text_len = await page.evaluate("""() => {
                    const eds = document.querySelectorAll('[contenteditable="true"]');
                    if (!eds.length) return 0;
                    return eds[eds.length - 1].textContent.replace(/\\s/g, '').length;
                }""")

                if text_len > 50:
                    logger.info(f"[Zhihu] Body filled via paste ({text_len} chars)")
                    return True
                else:
                    logger.warning(f"[Zhihu] Paste only got {text_len} chars, trying typing")
            except Exception as e:
                logger.warning(f"[Zhihu] Paste approach failed: {e}")

            # Fallback: type first paragraph to activate editor
            try:
                await body_field.click()
                await self._human_delay(0.3, 0.5)
                first_para = body.split("\n\n")[0].strip()[:200]
                for char in first_para:
                    await page.keyboard.type(char, delay=10)
                await page.keyboard.press("Enter")
                logger.info("[Zhihu] Body filled via typing (fallback)")
                return True
            except Exception:
                return False

        except Exception as e:
            logger.warning(f"[Zhihu] Body fill error: {e}")
            return False

    async def publish(self, page) -> bool:
        """Click publish button. 右下蓝色按钮."""
        try:
            await self._human_delay(2, 3)

            # Debug: find all buttons
            btn_info = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('button')).map(b => ({
                    text: b.textContent.trim().slice(0,10),
                    visible: b.offsetParent !== null,
                    rect: b.getBoundingClientRect ?
                        `${Math.round(b.getBoundingClientRect().x)},${Math.round(b.getBoundingClientRect().y)}` : ''
                }));
            }""")
            for b in btn_info:
                logger.info(f"[Zhihu] Button: '{b['text']}' visible={b['visible']} pos={b['rect']}")

            # Strategy: find bottom-right blue button with text "发布"
            # Click the button by its position or selector
            publish_btn = page.locator('button').filter(has_text="发布").last
            if not await publish_btn.is_visible(timeout=5000):
                # Try full text match
                all_btns = page.locator('button')
                count = await all_btns.count()
                for i in range(count):
                    text = (await all_btns.nth(i).text_content() or "").strip()
                    if text == "发布":
                        publish_btn = all_btns.nth(i)
                        break

            if await publish_btn.is_visible(timeout=5000):
                await publish_btn.click()
                logger.info("[Zhihu] Clicked 发布 button")
                await self._human_delay(3, 5)

                # Handle confirmation popup (选择话题/专栏/确认发布)
                # Zhihu shows: 选择话题发布 → click 发布 or 确定
                for popup_btn_text in ["发布", "确定", "确认", "发布到专栏"]:
                    try:
                        popup_btn = page.locator('button').filter(has_text=popup_btn_text).last
                        if await popup_btn.is_visible(timeout=3000):
                            await popup_btn.click()
                            logger.info(f"[Zhihu] Clicked popup: {popup_btn_text}")
                            await self._human_delay(2, 3)
                    except Exception:
                        pass

                return True

            logger.warning("[Zhihu] No publish button found")
            return False

        except Exception as e:
            logger.warning(f"[Zhihu] Publish error: {e}")
            return False

    async def verify(self, page) -> Optional[str]:
        """Get published article URL."""
        try:
            await self._human_delay(3, 5)
            url = page.url

            if "zhuanlan.zhihu.com" in url and "/p/" in url:
                return url

            article_link = page.locator('a[href*="/zhuanlan.zhihu.com/p/"], a[href*="/p/"]').first
            if await article_link.is_visible(timeout=5000):
                href = await article_link.get_attribute("href")
                if href:
                    return href if href.startswith("http") else f"https:{href}"

            return url if "zhuanlan.zhihu.com" in url else None

        except Exception as e:
            logger.warning(f"[Zhihu] Verify error: {e}")
            return None
