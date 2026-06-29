"""Connect to existing Chrome via remote debugging, extract LinkedIn cookies."""
import sys, os, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from cross_poster.config import SESSIONS_DIR

storage_path = os.path.join(SESSIONS_DIR, "linkedin_storage.json")

async def main():
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    pw = await async_playwright().start()

    # Connect to existing Chrome via CDP
    browser = await pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = context.pages[0] if context.pages else await context.new_page()

    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await asyncio.sleep(2)
    print(f"  Page: {page.url}", flush=True)

    if "login" not in page.url.lower():
        print("  ✅ LinkedIn 已登录!", flush=True)
        state = await context.storage_state()
        with open(storage_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"  ✅ Cookie 已保存 ({len(state.get('cookies', []))} 个)", flush=True)
    else:
        print("  ❌ 未登录，请先在 Chrome 中登录 LinkedIn", flush=True)

    await pw.stop()

asyncio.run(main())
