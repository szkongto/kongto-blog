#!/usr/bin/env python3
"""
Hashnode 半自动发文
==================
打开浏览器 → 你登录一次 → 自动填充内容 → 自动发布
首次60秒，之后cookie有效期内全自动。

运行: python post_hashnode.py
加入每日自动化: 已默认 headless 模式（需先跑一次登录）
"""

import sys, time
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DAY_NUM = datetime.now().timetuple().tm_yday
USER_DATA = BASE / "browser_profile_hashnode"

ARTICLES = [
    {
        "title": "CNC CRT to LCD Retrofit: The Complete Industrial Display Upgrade Guide",
        "body": """Industrial CNC machines from the 1990s and early 2000s share a common weak point: failing CRT displays. Here's the complete technical guide.

## Why CRT Displays Fail

CRT production ended globally 15+ years ago. Aging symptoms include dimming (phosphor degradation), flickering (capacitor aging), burn-in (permanent ghosting), and complete failure (flyback transformer or HV section). Each repair uses donor parts from other 20+ year old units — borrowing time that's running out.

## The LCD Retrofit Solution

Modern industrial LCD modules are designed as direct drop-in replacements. They use the original video connector, original power supply, and original mounting holes. Installation takes 10 minutes with a single screwdriver.

## Multi-Brand Connector Reference

- **FANUC**: Honda MR-20M (20-pin), DC 24V — A61L-0001 series, D9MM-11A
- **Mitsubishi**: 20-pin or 26-pin, DC 24V — MDT962B, BM09DF, FCUA-CT100
- **Mazak**: 26-pin, DC 24V — CD1472-D1M, C-5470NS, DR5614
- **Siemens**: DB-25 (25-pin), AC 110V — 6FC3998-7FA20, SM0901
- **Okuma**: 14-pin or 20-pin, DC 24V — OSP 5000/5020
- **Haas**: 9-pin D-Sub, DC 12V — VF/ST/SL series

## The Siemens AC110V Warning

Most Japanese CNCs use DC 24V. Siemens SINUMERIK systems use AC 110V. A DC-powered LCD plugged into a Siemens machine is instantly destroyed. Always verify the power specification on the CRT label.

## Cost Comparison (5-Year)

- Repeated CRT repairs: $2,000-4,000 total
- OEM replacement: $6,000-15,000
- Industrial LCD retrofit: $150-280 total

## Resources

Full installation guides and compatibility matrix (95+ models): https://cncdisplay.com""",
    },
    {
        "title": "CNC CRT Connector Types: The Essential Reference for Machine Retrofits",
        "body": """If you maintain legacy CNC equipment, you've probably encountered this: the CRT is dying, but you're not sure which replacement to order. The connector type and power specification are the most critical — and most commonly overlooked — details.

## Complete Brand-by-Brand Reference

### FANUC
- **Connector**: Honda MR-20M, 20-pin
- **Power**: DC 24V
- **Models**: A61L-0001-0074 through 0097, D9MM-11A
- **Systems**: 0i, 16i, 18i, 21i, Power Mate, 0-TC/MC

### Mitsubishi
- **Connector**: 20-pin or 26-pin (model dependent)
- **Power**: DC 24V
- **Models**: MDT962B, BM09DF, FCUA-CT100
- **Systems**: M64, E60, M500, M520

### Mazak
- **Connector**: 26-pin (NOT interchangeable with FANUC!)
- **Power**: DC 24V
- **Models**: CD1472-D1M, C-5470NS, DR5614, MDT-1283B
- **Systems**: T-32, M-32, T-Plus, M-Plus

### Siemens SINUMERIK
- **Connector**: DB-25 (25-pin D-Sub)
- **Power**: AC 110V (CRITICAL — not DC!)
- **Models**: 6FC3998-7FA20, SM0901-579417-TA
- **Systems**: 810, 820, 840D

### Okuma
- **Connector**: 14-pin or 20-pin
- **Power**: DC 24V
- **Systems**: OSP 5000, 5020, 7000

### Haas
- **Connector**: 9-pin D-Sub
- **Power**: DC 12V
- **Systems**: VF, ST, SL (early models)

## How to Verify Your Connector

1. Power off the CNC machine
2. Remove the CRT from its housing
3. Photograph the connector and the model label on the CRT back
4. Compare with the reference above
5. When in doubt, send the photo to a specialist for confirmation

## Common Mistake: Brand ≠ Compatibility

A "FANUC replacement LCD" and a "Mazak replacement LCD" are physically and electrically incompatible — even if both are 9-inch screens. Always match by exact model number and connector type, not brand name alone.

Full compatibility matrix: https://cncdisplay.com/en/compatibility-matrix.html""",
    },
]


def post_hashnode():
    from playwright.sync_api import sync_playwright

    article = ARTICLES[DAY_NUM % len(ARTICLES)]
    USER_DATA.mkdir(exist_ok=True)

    print(f"\n[Hashnode] {article['title'][:70]}...")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(USER_DATA),
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = ctx.new_page()

        # Try to go directly to new post page
        page.goto("https://hashnode.com/new", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Check if redirected (not logged in)
        if "/new" not in page.url:
            print("  [AUTH] Please log in (GitHub OAuth is fastest)")
            print("  Waiting up to 90 seconds...")
            # Go to login page
            page.goto("https://hashnode.com/onboard", wait_until="domcontentloaded", timeout=30000)
            # Wait for redirect to new post page after login
            try:
                page.wait_for_url("**/new**", timeout=90000)
                print("  [AUTH] Login detected!")
            except:
                print("  [AUTH] Login timeout. You can manually navigate to https://hashnode.com/new")
                input("  Press Enter after you're on the new post editor page...")
            time.sleep(2)

        print("  [FILL] Adding content...")

        # Hashnode uses a rich text editor. Use keyboard shortcut approach.
        # First tab to get past any onboarding modals
        time.sleep(3)
        page.keyboard.press("Escape")
        time.sleep(1)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Try to click the title area and type
        try:
            # Click in the general editor area
            page.mouse.click(400, 200)
            time.sleep(1)

            # Type the title
            page.keyboard.type(article["title"], delay=5)
            print("  [OK] Title typed")

            # Press Enter to go to body
            page.keyboard.press("Enter")
            time.sleep(0.5)
            page.keyboard.press("Enter")
            time.sleep(0.5)

            # Type the body
            page.keyboard.type(article["body"], delay=2)
            print("  [OK] Body typed")

            # Publish
            time.sleep(2)
            # Ctrl+Enter often publishes on platforms
            page.keyboard.press("Control+Enter")
            time.sleep(3)

            url = page.url
            print(f"  [DONE] {url}")
            ctx.close()
            return url

        except Exception as e:
            # Save screenshot for debugging
            page.screenshot(path=str(BASE / "hashnode_error.png"))
            print(f"  [ERROR] {e}, screenshot saved")
            ctx.close()
            return None


if __name__ == '__main__':
    url = post_hashnode()
    if url:
        print(f"\n[DONE] {url}")
        import csv
        tracker = BASE / "backlinks_daily" / "post_tracker.csv"
        with open(tracker, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([TODAY, "Hashnode", ARTICLES[DAY_NUM % len(ARTICLES)]["title"][:120], url, "published"])
    else:
        print("\n[FAILED] Check hashnode_error.png")
