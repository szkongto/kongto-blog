#!/usr/bin/env python3
"""
First-time login helper - runs in foreground.
Opens browser → you login → I touch flag → cookies saved
"""
import sys, os, json, asyncio, time
# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from cross_poster.config import SESSIONS_DIR, VIEWPORT, PLATFORMS

platform = sys.argv[1] if len(sys.argv) > 1 else "csdn"
info = PLATFORMS[platform]
storage_path = os.path.join(SESSIONS_DIR, f"{platform}_storage.json")
profile_dir = os.path.join(SESSIONS_DIR, f"browser_profile_{platform}")
flag_file = os.path.join(SESSIONS_DIR, f".login_done_{platform}")

# Remove old flag
if os.path.exists(flag_file):
    os.remove(flag_file)

async def main():
    print("Starting browser...", flush=True)
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.makedirs(profile_dir, exist_ok=True)

    pw = await async_playwright().start()
    context = await pw.chromium.launch_persistent_context(
        profile_dir,
        headless=False,
        viewport=VIEWPORT,
        locale="zh-CN",
    )
    page = await context.new_page()
    await page.goto(info["login_url"], wait_until="domcontentloaded")

    print(f"\n{'='*60}")
    print(f"  [{info['name']}] 浏览器已打开")
    print(f"  请在浏览器中扫码/密码登录")
    print(f"  登录完成后，在聊天里告诉我 '登录好了'")
    print(f"{'='*60}\n")
    print(f"  等待信号文件... (touch {flag_file} to continue)", flush=True)

    # Wait for flag file
    while not os.path.exists(flag_file):
        await asyncio.sleep(1)

    print("\n  检测到登录完成信号，保存 Cookie...", flush=True)
    await asyncio.sleep(2)  # Extra wait for cookies to settle

    state = await context.storage_state()
    with open(storage_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"  Cookie 已保存到 {storage_path}", flush=True)
    print(f"  共 {len(state.get('cookies', []))} 个 Cookie", flush=True)

    # Verify by going to editor
    await page.goto(info["editor_url"], wait_until="domcontentloaded")
    await asyncio.sleep(2)
    print(f"  编辑器页面: {page.url}", flush=True)

    await context.close()
    await pw.stop()

if __name__ == "__main__":
    asyncio.run(main())
