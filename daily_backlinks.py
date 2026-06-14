#!/usr/bin/env python3
"""
每日外链自动化引擎 v4.0 — 全自动多平台
=========================================
全自动: Dev.to(DA92) + Telegra.ph(DA86) + Rentry.co(DA60)
生成内容: LinkedIn(DA98) + Reddit(DA91) + 中文平台

运行: python daily_backlinks.py
定时: Windows Task Scheduler 每天一次
"""

import json, os, sys, requests, csv, random
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT = BASE / "backlinks_daily"
OUTPUT.mkdir(exist_ok=True)
CONFIG_FILE = BASE / "auto_poster_config.json"
TRACKER = OUTPUT / "post_tracker.csv"
SITE = "https://cncdisplay.com"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DAY_NUM = datetime.now().timetuple().tm_yday

# ============================================================
# 配置
# ============================================================
def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    return {}

def init_tracker():
    if not TRACKER.exists():
        with open(TRACKER, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['date', 'platform', 'title', 'url', 'status'])

def log_post(platform, title, url, status="published"):
    init_tracker()
    with open(TRACKER, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([TODAY, platform, title[:120], url, status])

def pick(pool):
    return pool[DAY_NUM % len(pool)]

# ============================================================
# 30天内容轮换池
# ============================================================
ARTICLES = [
    {
        "title": "CNC CRT to LCD Upgrade: The Complete Connector and Power Guide",
        "devto_tags": ["cnc", "manufacturing", "engineering", "tutorial"],
        "canonical": f"{SITE}/en/compatibility-matrix.html",
        "body_devto": """## The #1 Mistake When Ordering a CNC LCD Replacement

Getting the connector and power supply wrong. Here's everything you need to know.

## Connector Reference by Brand

| Brand | Connector Type | Pins | Power |
|-------|---------------|------|-------|
| FANUC | Honda MR-20M | 20 | DC 24V |
| Mitsubishi | varies | 20-26 | DC 24V |
| Mazak | Proprietary | 26 | DC 24V |
| Siemens | DB-25 | 25 | **AC 110V** |
| Okuma | varies | 14-20 | DC 24V |
| Haas | 9-pin D-Sub | 9 | DC 12V |

## The Siemens AC110V Warning

Siemens SINUMERIK systems use AC 110V. Japanese CNCs use DC 24V. Using a DC LCD on Siemens = destroyed module. Triple-check before ordering.

## How to Find Your CRT Model

Look on the back of the CRT housing for the label. Common prefixes:
- FANUC: "A61L-0001-XXXX" or "D9MM-11A"
- Mitsubishi: "MDT" prefix
- Siemens: "6FC" prefix
- Mazak: "CD1" or "C-" prefix

Take a photo — easier than reading it in place.

## Why This Matters

Every week someone orders the wrong LCD by matching brand name instead of connector type. "FANUC LCD" and "Mazak LCD" are physically incompatible even at the same size.

Full compatibility matrix (95+ models): [{SITE}/en/compatibility-matrix.html]({SITE}/en/compatibility-matrix.html)
Installation guides: [{SITE}]({SITE})""",
    },
    {
        "title": "Repair vs Replace: The Real Cost of Keeping an Old CNC CRT Alive",
        "devto_tags": ["cnc", "manufacturing", "engineering", "tutorial"],
        "canonical": f"{SITE}/comparison-kongto-vs-competitors.html",
        "body_devto": """## The Sunk Cost Trap

Shop owners paying $400-800 every 6-12 months to "repair" a dying CNC CRT. Let's do the actual math.

## CRT Repair Economics (FANUC 0-TC Example)

| Repair | Cost | When | Cumulative |
|--------|------|------|------------|
| 1st (new flyback) | $400 | Month 0 | $400 |
| 2nd (capacitors) | $350 | Month 8 | $750 |
| 3rd (new tube) | $600 | Month 14 | $1,350 |
| 4th repair | $500 | Month 20 | $1,850 |

18 months: $1,850 spent, 4 times downtime. Each repair used donor parts from 20+ year old CRTs.

## LCD Retrofit Economics

| Item | Cost |
|------|------|
| LCD module (FANUC A61L-0001-0093) | $180-280 |
| Installation | 10 min (DIY) |
| Lifespan | 5-7 years continuous |
| 5-Year Total | **$180-280** |

## Why CRT Repairs Keep Failing

CRT displays were discontinued 15+ years ago. "Repairs" use flyback transformers and capacitors harvested from donor units — all 20+ years old themselves. Each repair borrows time from another dying unit. The donor pool is shrinking fast.

## The Hidden Cost: Machine Downtime

A CNC down 3 days waiting for CRT repair at $500/day production value = $1,500 lost output + $400 repair = $1,900 real cost per incident.

## When to Repair vs Replace

**Repair only if:** Machine retiring within 6 months, or rarely-used backup.
**Replace with LCD if:** Runs production regularly, mechanical condition good, keeping 1+ years.

## OEM Replacement Reality

FANUC sells a "replacement CRT." It's a refurb from another old machine. Cost: $800-1,500. Same aging components as yours.

For $180-280, eliminate the CRT failure cycle permanently.

Cost comparison: [{SITE}/comparison-kongto-vs-competitors.html]({SITE}/comparison-kongto-vs-competitors.html)
Model guides: [{SITE}]({SITE})""",
    },
    {
        "title": "How to Identify Your CNC CRT Model Before Ordering a Replacement LCD",
        "devto_tags": ["cnc", "manufacturing", "engineering", "tutorial"],
        "canonical": f"{SITE}/en/compatibility-matrix.html",
        "body_devto": """## First Step: Find Your CRT Model Number

Before ordering any replacement, you need to identify exactly what CRT is in your machine. Here's how.

## Where to Look

The model label is on the **back** of the CRT housing. You'll need:
- A flashlight (shop lighting is rarely good enough)
- Your phone camera (take a photo — it's easier than squinting)
- Possibly a mirror if the label faces the wall

## Reading the Label

### FANUC
Label format: `A61L-0001-XXXX` or `D9MM-11A`
- A61L-0001-**0093** = 9" amber monochrome, Honda MR-20M
- A61L-0001-**0092** = 9" amber, similar to 0093
- A61L-0001-**0074** = 14" color
- A61L-0001-**0096** = 14" color
- D9MM-11A = same as A61L-0001-0093

### Mitsubishi
Label prefix: `MDT` or `BM` or `FCUA`
- MDT962B = 9" monochrome, M64/E60
- BM09DF = 9", E60 system
- FCUA-CT100 = 9", M500/M520

### Siemens
Label prefix: `6FC` or `SM`
- 6FC3998-7FA20 = 12.1" mono, SINUMERIK 810/820
- SM0901-579417-TA = same compatibility

### Mazak
Label prefix: `CD1` or `C-` or `DR`
- CD1472-D1M = 10.4" color, T-32/M-32
- C-5470NS = 10.4" color, M-32/M-Plus
- DR5614 = 10.4" color, T-32/T-Plus

## Can't Read the Label?

Alternative identification methods:
1. **Screen size**: Measure the visible diagonal of the CRT
2. **Connector type**: Count the pins on the connector
3. **Machine model**: Your CNC model narrows down compatible CRTs
4. **Send a photo**: A clear photo of the CRT and connector to a specialist

## Next Step: Check Compatibility

Once you have your model number, verify compatible replacements here:
[{SITE}/en/compatibility-matrix.html]({SITE}/en/compatibility-matrix.html)

Or send a photo and get a definitive answer about replacement options: [{SITE}]({SITE})""",
    },
]

SOCIAL_TODAY = [
    {
        "title": "FANUC CRT getting dim — repair or replace?",
        "body": "My FANUC 0-TC amber CRT is getting harder to read every month. At 100% brightness and still too dim.\n\nThese CRTs were discontinued 15+ years ago. Anyone here repaired the HV section? Did it last? Or just went LCD?\n\nMachine is mechanically solid — ways tight, spindle good. This screen is the only issue."
    },
    {
        "title": "Mitsubishi M64 monitor flickering on cold start",
        "body": "Mitsubishi M64 with MDT962B CRT. Cold mornings = flickering for 20-30 min before stabilizing.\n\nAging caps in the power section? Anyone fixed this?\n\nIf I go LCD route — is it really plug-and-play with the 20-pin connector? No parameter changes?"
    },
    {
        "title": "CRT repair shop quoted $500 — reasonable?",
        "body": "Quote to rebuild HV section on FANUC 18T CRT: $500, 90-day warranty.\n\n1998 machine, runs daily. Deciding:\n1. Pay $500, hope it lasts\n2. Used CRT on eBay ($200-400)\n3. LCD module\n\nWho went LCD in production? Vibration/temperature issues?"
    },
]

LINKEDIN_TODAY = [
    "Manufacturing fact: Your 1998 FANUC is mechanically bulletproof. The CRT? Designed for 10-15 years. It's now at year 28.\n\nPlug-and-play LCD replacements exist for every major CNC brand. Original connectors. Same power. 10 minute install.\n\n$150-300 extends a $50K+ machine by 5-7 years.\n\nI have guides for FANUC, Mitsubishi, Mazak, Siemens, Okuma, Haas at cncdisplay.com\n\n#Manufacturing #CNC #IndustrialAutomation",
    "Most common CNC LCD retrofit mistake: getting power wrong.\n\nFANUC/Mitsubishi/Mazak/Okuma: DC 24V\nSiemens SINUMERIK: AC 110V (critical!)\nHaas early: DC 12V\n\nI've seen LCD modules destroyed by DC-on-AC mistakes.\n\nCompatibility reference: cncdisplay.com\n\n#CNC #Manufacturing #Engineering",
    "Why repair a 28-year-old CRT when an LCD replacement costs less than 2 repairs?\n\nCRT repair: $400-800/incident, 3-12 month lifespan\nLCD retrofit: $150-280 once, 5-7 years\n\nThe math isn't close.\n\nGuides at cncdisplay.com\n\n#Manufacturing #ROI #CNC",
]

ZH_TODAY = [
    {"title": "老旧CNC数控机床CRT改LCD——接口对照速查表", "body": "做工业显示方案这些年整理的接口对照，同行参考：\n\n| 品牌 | 接口 | 供电 |\n|------|------|------|\n| FANUC | Honda MR-20M (20针) | DC 24V |\n| 三菱 | 20针/26针 | DC 24V |\n| Mazak | 26针 | DC 24V |\n| 西门子 | DB-25 | AC 110V ⚠️ |\n| 大隈 | 14针/20针 | DC 24V |\n| 哈斯 | 9针D-Sub | DC 12V |\n\n安装：拆4颗螺丝→拔1根线→插新LCD→拧螺丝→开机。不用改参数。\n\n想确认你的机床能不能换？更多资料: cncdisplay.com"},
    {"title": "CNC显示器维修还是换LCD？算一笔真实的账", "body": "以FANUC 0-TC为例：\n\n| 方案 | 单次花费 | 寿命 | 5年总成本 |\n|------|---------|------|-----------|\n| 修CRT | ¥300-800 | 3-12个月 | ¥2000-4000 |\n| 原厂换屏 | ¥6000-10000 | 2-5年(翻新) | ¥10000+ |\n| 工业LCD | ¥700-1500 | 5-7年 | ¥700-1500 |\n\nCRT停产超过15年。维修用的高压包、电容都是拆机件，本身也快坏了。反复修=反复停机。\n\n不确定型号能不能换？拍显示器标签照片免费查: cncdisplay.com"},
    {"title": "西门子CNC显示器升级——一个容易忽略的重要区别", "body": "处理西门子SINUMERIK 810/820显示器升级时，必须清楚：\n\n日本CNC（FANUC/三菱/Mazak）: DC 24V供电\n西门子老型号: AC 110V供电 ⚠️\n\n给西门子买LCD替代品必须标注支持AC110V。用错了直流LCD——直接烧毁。\n\n另外西门子用DB-25接口，和日本CNC的20/26针完全不同。\n\n型号参考:\n- 6FC3998-7FA20 — 12.1寸，SINUMERIK 810/820\n- SM0901 (NFP 579417 TA) — 同上兼容\n\n更多资料: cncdisplay.com"},
]

# ============================================================
# 全自动发文平台
# ============================================================

def post_devto():
    """Dev.to API - DA 92, Dofollow"""
    cfg = load_config()
    api_key = cfg.get("devto_api_key")
    if not api_key:
        print("[SKIP] Dev.to - no API key")
        return None

    article = pick(ARTICLES)
    print(f"\n[Dev.to] {article['title'][:70]}...")

    resp = requests.post(
        "https://dev.to/api/articles",
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json={"article": {
            "title": article["title"],
            "body_markdown": article["body_devto"],
            "published": True,
            "tags": article["devto_tags"],
            "canonical_url": article["canonical"],
        }},
        timeout=30
    )

    if resp.status_code in [200, 201]:
        url = resp.json().get("url", "")
        print(f"  [OK] {url}")
        log_post("Dev.to", article["title"], url)
        return url
    print(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:150]}")
    return None


def post_telegraph():
    """Telegra.ph API - DA 86, Dofollow, no user auth needed"""
    cfg = load_config()
    token = cfg.get("telegraph_token")
    if not token:
        print("[SKIP] Telegra.ph - no token")
        return None

    article = pick(ARTICLES)
    # Generate simplified content for Telegraph
    telegraph_title = article["title"]
    paragraphs = []
    for line in article["body_devto"].split("\n"):
        line = line.strip()
        if not line or line.startswith("---"):
            continue
        # Convert markdown headers
        if line.startswith("## "):
            paragraphs.append({"tag": "h2", "children": [line[3:]]})
        elif line.startswith("### "):
            paragraphs.append({"tag": "h3", "children": [line[4:]]})
        elif line.startswith("|"):
            continue  # Skip tables (Telegraph doesn't support well)
        elif line.startswith("[") and "](" in line:
            # Convert markdown links
            paragraphs.append({"tag": "p", "children": [line]})
        elif line.startswith("- "):
            paragraphs.append({"tag": "p", "children": [line]})
        else:
            paragraphs.append({"tag": "p", "children": [line]})

    print(f"\n[Telegra.ph] {telegraph_title[:70]}...")

    resp = requests.post(
        "https://api.telegra.ph/createPage",
        json={
            "access_token": token,
            "title": telegraph_title,
            "author_name": "Kongto Technology",
            "author_url": SITE,
            "content": paragraphs[:50],  # Limit content length
        },
        timeout=15
    )

    if resp.status_code == 200 and resp.json().get("ok"):
        url = resp.json()["result"]["url"]
        print(f"  [OK] {url}")
        log_post("Telegra.ph", telegraph_title, url)
        return url
    print(f"  [FAIL] {resp.text[:150]}")
    return None


def post_rentry():
    """Rentry.co - DA ~60, Dofollow, no auth needed"""
    article = pick(ARTICLES)
    slug = f"cnc-display-{TODAY.replace('-', '')}"
    text = f"""# {article['title']}

## Quick Reference

**Connector Types by Brand:**
- FANUC: Honda MR-20M (20-pin), DC24V
- Mitsubishi: 20/26-pin, DC24V
- Mazak: 26-pin, DC24V
- Siemens: DB-25, AC110V
- Okuma: 14/20-pin, DC24V
- Haas: 9-pin D-Sub, DC12V

**FANUC Common Models:**
A61L-0001-0093 (D9MM-11A) = 9" amber, most common

**Installation:** 4 screws, 1 connector, 10 minutes. No parameter changes.

**Full guides:** {SITE}
**Compatibility matrix:** {SITE}/en/compatibility-matrix.html
**Case studies:** {SITE}/case-studies.html

---
*Kongto Technology — Industrial CNC display solutions since 2013*
"""

    print(f"\n[Rentry.co] {article['title'][:70]}...")

    try:
        resp = requests.post(
            "https://rentry.co/api/new",
            data={"url": slug, "edit_code": f"cnc{DAY_NUM:04d}", "text": text},
            timeout=15
        )
        if resp.status_code == 200 and '"status": "200"' in resp.text:
            url = f"https://rentry.co/{slug}"
            print(f"  [OK] {url}")
            log_post("Rentry.co", article["title"], url)
            return url
        # If slug taken, try with random suffix
        resp = requests.post(
            "https://rentry.co/api/new",
            data={"edit_code": f"cnc{DAY_NUM:04d}", "text": text},
            timeout=15
        )
        if resp.status_code == 200:
            import re
            m = re.search(r'"url_short":\s*"([^"]+)"', resp.text)
            if m:
                url = f"https://rentry.co/{m.group(1)}"
                print(f"  [OK] {url}")
                log_post("Rentry.co", article["title"], url)
                return url
        print(f"  [FAIL] {resp.text[:150]}")
    except Exception as e:
        print(f"  [FAIL] {e}")
    return None


# ============================================================
# 生成手动平台内容
# ============================================================
def gen_manual_content():
    day_dir = OUTPUT / TODAY
    day_dir.mkdir(exist_ok=True)

    # Reddit
    social = pick(SOCIAL_TODAY)
    f = day_dir / "reddit_post.txt"
    f.write_text(f"TITLE: {social['title']}\n\n{social['body']}", encoding='utf-8')

    # LinkedIn
    li = pick(LINKEDIN_TODAY)
    f = day_dir / "linkedin_post.txt"
    f.write_text(li, encoding='utf-8')

    # Chinese
    zh = pick(ZH_TODAY)
    f = day_dir / "zh_post.md"
    f.write_text(f"# {zh['title']}\n\n{zh['body']}", encoding='utf-8')

    print(f"\n[GEN] Manual content → {day_dir}")
    print(f"  reddit_post.txt | linkedin_post.txt | zh_post.md")
    return day_dir


# ============================================================
# 状态报告
# ============================================================
def print_status():
    print(f"=== CNCdisplay Daily Backlink Engine v4.0 ===")
    print(f"Date: {TODAY}")

    if TRACKER.exists():
        with open(TRACKER, 'r', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        today = [r for r in rows[1:] if r[0] == TODAY]
        total = len(rows) - 1
        print(f"Today: {len(today)} posts | Total tracked: {total}")
        for r in today:
            print(f"  [{r[4]}] {r[1]}: {r[2][:60]}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print_status()

    # === AUTO-POST (no user action needed) ===
    results = {}
    r = post_devto()
    if r: results["Dev.to"] = r
    r = post_telegraph()
    if r: results["Telegra.ph"] = r
    r = post_rentry()
    if r: results["Rentry.co"] = r

    # === GENERATE MANUAL ===
    day_dir = gen_manual_content()

    # === SUMMARY ===
    print(f"\n{'='*50}")
    print(f"DONE: {len(results)} auto-published + manual content generated")
    for k, v in results.items():
        print(f"  [{k}] {v}")
    print(f"  [Manual] {day_dir}")
    print(f"{'='*50}")
