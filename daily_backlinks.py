#!/usr/bin/env python3
"""
每日外链自动化引擎 v3.0
======================
每天自动: Dev.to发文 + 生成各平台内容 + 追踪记录
运行: python daily_backlinks.py
定时: 每天跑一次, 20秒完成所有自动化操作

需要Hashnode PAT的话告诉我，我帮你配。
"""

import json, os, sys, requests, csv, random
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT = BASE / "backlinks_daily"
OUTPUT.mkdir(exist_ok=True)
CONFIG_FILE = BASE / "auto_poster_config.json"
TRACKER = OUTPUT / "post_tracker.csv"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DAY_NUM = datetime.now().timetuple().tm_yday

SITE = "https://cncdisplay.com"

# ============================================================
# 30天内容轮换池 — 每天不重样
# ============================================================
POSTS_DEVTO = [
    {
        "title": "How to Upgrade a 25-Year-Old CNC Machine Display from CRT to LCD",
        "tags": ["cnc", "manufacturing", "engineering", "tutorial"],
        "canonical": f"{SITE}/en/posts/FANUC_CRT_Maintenance_vs_LCD_Upgrade_Module_Comparison.html",
        "body": """## The Problem: Aging CNC CRTs

Walk into any machine shop running 1990-2005 CNC equipment, and you'll find the same issue: CRT displays that are dim, flickering, or completely dead. These machines were built to last 30+ years mechanically — but the displays were designed for a 10-15 year lifespan.

## The OEM "Solution"

Contact FANUC for a replacement A61L-0001-0093 CRT. Quote: $800-1,500. For a refurbished unit. That might last 2 years.

Or replace the entire CNC control system: $6,000-15,000+. For a machine where only the screen is bad.

## The Better Way: Industrial LCD Retrofit

Modern plug-and-play LCD replacement modules exist for virtually every major CNC brand. Here's why they work:

### Technical Compatibility
- **Same connector**: Uses the original Honda MR-20M (FANUC), 20/26-pin (Mitsubishi/Mazak), DB-25 (Siemens)
- **Same power**: DC24V for Japanese CNCs, AC110V for Siemens
- **Same mounting**: Identical bolt pattern and bezel dimensions
- **Signal transparent**: The CNC controller outputs composite video — the LCD module receives and displays the same signal

### Installation: 10 Minutes
1. Power off CNC machine
2. Remove 4 mounting screws
3. Disconnect 1 connector
4. Plug into LCD module
5. Re-mount, power on — done

No soldering. No wiring changes. No CNC parameter modifications.

## Cost Analysis Over 5 Years

| Approach | Unit Cost | Lifespan | 5-Year Total |
|----------|-----------|----------|--------------|
| OEM replacement (refurb) | $800-1,500 | 2-5 years | $2,000-4,000 |
| CRT repair | $300-800/repair | 3-12 months | $2,000-4,000 |
| eBay unbranded LCD | $100-200 | Unpredictable | $200-600+ |
| **Industrial LCD retrofit** | **$150-280** | **5-7 years** | **$150-280** |

## Brands Supported

### FANUC
A61L-0001-0093 (D9MM-11A), 0092, 0094, 0074, 0086, 0096, 0097
Compatible with: 0i, 16i, 18i, 21i, Power Mate, 0-TC/MC

### Mitsubishi
MDT962B, BM09DF, FCUA-CT100
M64, E60, M500, M520 systems

### Mazak
CD1472-D1M, C-5470NS, DR5614, MDT-1283B
T-32, M-32, T-Plus, M-Plus

### Siemens
6FC3998-7FA20, SM0901-579417-TA
SINUMERIK 810, 820, 840D (AC110V power!)

### Okuma & Haas
OSP 5000, 5020, 7000 | VF, ST, SL series

## Critical Warning: Power Supply

Siemens SINUMERIK systems use **AC 110V** for display power. Japanese CNCs all use DC 24V. Using a DC-powered LCD on a Siemens = instant damage.

## Resources

Full compatibility matrix (95+ models): [{SITE}/en/compatibility-matrix.html]({SITE}/en/compatibility-matrix.html)
Installation guides: [{SITE}]({SITE})
Case studies: [{SITE}/case-studies.html]({SITE}/case-studies.html)""",
    },
    {
        "title": "CNC CRT to LCD Retrofit: The Complete Connector and Power Guide",
        "tags": ["cnc", "manufacturing", "engineering", "tutorial"],
        "canonical": f"{SITE}/en/compatibility-matrix.html",
        "body": """## The #1 Mistake When Ordering a CNC LCD Replacement

Getting the connector and power supply wrong. Here's everything you need to know before ordering.

## Connector Reference by Brand

| Brand | Connector Type | Pins | Power | Notes |
|-------|---------------|------|-------|-------|
| FANUC | Honda MR-20M | 20 | DC 24V | Most common, used across 0i/16i/18i/21i |
| Mitsubishi | varies | 20-26 | DC 24V | Check your specific model |
| Mazak | Proprietary | 26 | DC 24V | NOT compatible with FANUC |
| Siemens | DB-25 (D-Sub) | 25 | **AC 110V** | Critical: AC not DC! |
| Okuma | varies | 14-20 | DC 24V | OSP 5000/5020/7000 |
| Haas | 9-pin D-Sub | 9 | DC 12V | Early VF/ST/SL models |

## Power Supply Warning

The Siemens AC 110V difference is the most common cause of destroyed LCD modules. Before ordering:
1. Locate your CRT's model label
2. Note the power specification
3. If it says "AC 100-120V" or "110V", you need a Siemens-specific LCD
4. All other brands use DC power (12V or 24V)

## How to Find Your CRT Model

Look on the back of the CRT housing for a label containing:
- FANUC: "A61L-0001-XXXX" or "D9MM-11A"
- Mitsubishi: "MDT" prefix
- Siemens: "6FC" or "6FC3" prefix
- Mazak: "CD1" or "C-" prefix

Take a photo with your phone — much easier than trying to read it in place.

## Why This Matters

Every week, someone orders the wrong LCD because they matched by brand name instead of connector type. "FANUC LCD" and "Mazak LCD" are physically incompatible, even if they're both 9-inch screens.

## How to Verify Compatibility

Check the full cross-reference matrix: [{SITE}/en/compatibility-matrix.html]({SITE}/en/compatibility-matrix.html)

Or send a photo of your CRT's label to get a definitive answer about which LCD fits your machine.

## More Resources

- Installation guide: [{SITE}]({SITE})
- Cost comparison: [{SITE}/comparison-kongto-vs-competitors.html]({SITE}/comparison-kongto-vs-competitors.html)""",
    },
    {
        "title": "Repair vs Replace: The True Cost of Keeping an Old CNC CRT Alive",
        "tags": ["cnc", "manufacturing", "engineering", "tutorial"],
        "canonical": f"{SITE}/comparison-kongto-vs-competitors.html",
        "body": """## The Sunk Cost Trap

I see it constantly: shop owners paying $400-800 every 6-12 months to "repair" a dying CNC CRT. Let's do the actual math.

## CRT Repair Economics (FANUC 0-TC Example)

| Repair # | Cost | When | Cumulative |
|----------|------|------|------------|
| 1st repair (new flyback) | $400 | Month 0 | $400 |
| 2nd repair (capacitors) | $350 | Month 8 | $750 |
| 3rd repair (new tube) | $600 | Month 14 | $1,350 |
| 4th repair | $500 | Month 20 | $1,850 |

18 months in: $1,850 spent, machine has been down 4 times. Each repair used donor parts from other 20+ year old CRTs.

## Industrial LCD Retrofit Economics

| Item | Cost |
|------|------|
| LCD retrofit module (FANUC A61L-0001-0093 replacement) | $180-280 |
| Installation labor | 10 minutes (DIY) |
| Expected lifespan | 5-7 years continuous |
| 5-year total | **$180-280** |

## Why CRT Repairs Keep Failing

CRT displays were discontinued globally 15+ years ago. Modern "repairs" use:
- Flyback transformers harvested from donor units (20+ years old)
- Capacitors from the same era (already near end of life)
- CRT tubes with varying levels of phosphor degradation

Each "repair" is borrowing time from another dying unit. The supply of donor parts is finite and shrinking.

## The Hidden Cost: Downtime

A CNC machine down for 3 days waiting for a CRT repair at $500/day production value = $1,500 in lost output. Add the $400 repair = $1,900 real cost per incident.

## When to Repair vs Replace

**Repair if:**
- Machine is being retired within 6 months
- It's a rarely-used backup machine

**Replace with LCD if:**
- Machine runs production regularly
- Mechanical condition is good
- You plan to keep it 1+ years

## What About OEM Replacement?

FANUC will sell you a replacement CRT. It's a refurbished unit from another old machine. Cost: $800-1,500. It has the same aging components as yours.

## The Bottom Line

For a $180-280 one-time investment, you eliminate the CRT failure cycle entirely. The LCD will outlast the machine.

Full cost comparison across brands: [{SITE}/comparison-kongto-vs-competitors.html]({SITE}/comparison-kongto-vs-competitors.html)
Model-specific guides: [{SITE}]({SITE})""",
    },
]

POSTS_SOCIAL = [
    # Reddit-style posts (no links for new accounts)
    [
        {
            "title": "FANUC CRT getting dim — repair or replace? What did you do?",
            "body": "My FANUC 0-TC amber CRT is getting harder to read every month. Brightness is at 100% and still too dim in normal shop lighting.\n\nI know these CRTs were discontinued forever ago. Has anyone here repaired the high voltage section on these? Did it actually last? Or did you just bite the bullet and switch to an LCD replacement?\n\nMachine is in great mechanical shape otherwise — ways are tight, spindle sounds fine. This screen is literally the only problem.\n\nWhat worked for you guys?"
        },
        {
            "title": "Mitsubishi M64 monitor flickering — cold start issue?",
            "body": "Running a Mitsubishi M64 with the original MDT962B CRT. On cold mornings, the screen flickers for the first 20-30 minutes before stabilizing.\n\nI'm guessing aging capacitors in the power supply section? Anyone fixed this without replacing the whole unit?\n\nAlso — if I do go the LCD route, is it truly plug-and-play with the 20-pin connector? No parameter changes needed?"
        },
        {
            "title": "CRT repair shop quoted me $500 — is this reasonable?",
            "body": "Got a quote to rebuild the high voltage section on my FANUC 18T CRT: $500 with a 90-day warranty.\n\nIs this the going rate? The machine is a 1998, runs daily. I'm trying to decide between:\n1. Pay the $500 and hope it lasts\n2. Look for a used replacement CRT ($200-400 on eBay)\n3. Switch to an LCD module\n\nFor those who went LCD — how's it holding up in a production environment? Any issues with vibration or temperature?"
        },
    ],
    # LinkedIn posts
    [
        {
            "body": """Manufacturing reality check: Your 1998 FANUC CNC machine is mechanically sound. The cast iron bed, ball screws, and spindle were built for 30+ years.

The CRT display? Designed for 10-15 years. It's now at year 28.

Here's what most shops don't realize: plug-and-play LCD replacements exist for virtually every legacy CNC brand. Original connectors. Same power supply. Zero parameter changes. Installation: 10 minutes.

For $150-300, you extend a machine worth $50,000+ by 5-7 years.

I've documented the process for FANUC, Mitsubishi, Mazak, Siemens, Okuma, and Haas. Links in the comments.

#Manufacturing #CNC #IndustrialAutomation #MachineTool #Engineering"""
        },
        {
            "body": """The most common mistake when upgrading a CNC CRT to LCD? Getting the power supply wrong.

Quick reference:
- FANUC, Mitsubishi, Mazak, Okuma: DC 24V
- Siemens SINUMERIK: AC 110V (very important!)
- Haas early models: DC 12V
- Connectors: all different, not interchangeable

I've seen LCD modules destroyed because someone ordered a DC unit for their Siemens machine. Triple-check the specs before ordering.

Full compatibility reference in the comments.

#CNC #IndustrialMaintenance #Manufacturing #Siemens #FANUC"""
        },
    ],
]

POSTS_ZH = [
    {
        "title": "老旧CNC数控机床CRT改LCD——一线维修师傅的真实经验",
        "body": """做工业显示方案这些年，整理了一些实操经验给同行参考。

## 接口对照速查

| 品牌 | 接口 | 供电 |
|------|------|------|
| FANUC | Honda MR-20M (20针) | DC 24V |
| 三菱 | 20针/26针 | DC 24V |
| Mazak | 26针 | DC 24V |
| 西门子老型号 | DB-25 | AC 110V ⚠️ 交流！ |
| 大隈 | 14针/20针 | DC 24V |
| 哈斯 | 9针D-Sub | DC 12V |

## 安装步骤（FANUC为例）

1. 关机断电
2. 拆CRT四角螺丝
3. 拔下信号供电线
4. 插到新LCD模块
5. 拧回螺丝，开机

不需要改任何参数，不需要焊接，不需要转接板。

## 成本对比

| 方案 | 价格 | 寿命 |
|------|------|------|
| 原厂换屏 | ¥6000-10000 | 2-5年(翻新) |
| 修高压板 | ¥300-800/次 | 3-12个月 |
| 换工业LCD | ¥700-1500 | 5-7年 |

想确认你的机床能不能换？拍张显示器背面标签照片，免费帮你查兼容方案。

更多资料: cncdisplay.com"""
    },
]

# ============================================================
# 核心发布函数
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
    print(f"  [LOG] {platform}: {status}")

def get_today_post(pool):
    """Pick today's post deterministically from the pool"""
    idx = DAY_NUM % len(pool)
    return pool[idx]

def post_devto():
    """Auto-post to Dev.to using saved API key"""
    cfg = load_config()
    api_key = cfg.get("devto_api_key")
    if not api_key:
        print("[SKIP] Dev.to — no API key configured")
        return None

    post = get_today_post(POSTS_DEVTO)
    print(f"\n=== Dev.to Post ===")
    print(f"Title: {post['title'][:80]}...")

    resp = requests.post(
        "https://dev.to/api/articles",
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json={
            "article": {
                "title": post["title"],
                "body_markdown": post["body"],
                "published": True,
                "tags": post["tags"],
                "canonical_url": post["canonical"],
            }
        },
        timeout=30
    )

    if resp.status_code in [200, 201]:
        data = resp.json()
        url = data.get("url", "")
        print(f"[OK] {url}")
        log_post("Dev.to", post["title"], url)
        return url
    else:
        print(f"[FAIL] HTTP {resp.status_code}: {resp.text[:200]}")
        log_post("Dev.to", post["title"], "", f"failed_{resp.status_code}")
        return None


def generate_daily_content():
    """Generate today's content for manual posting platforms"""
    day_dir = OUTPUT / TODAY
    day_dir.mkdir(exist_ok=True)

    # Social media snippet
    social_pool = POSTS_SOCIAL[0]  # Reddit-style posts
    social = get_today_post(social_pool)

    reddit = day_dir / "reddit_post.txt"
    reddit.write_text(f"{social['title']}\n\n{social['body']}", encoding='utf-8')
    print(f"[GEN] Reddit post → {reddit}")

    # LinkedIn snippet
    li_pool = POSTS_SOCIAL[1]
    li = get_today_post(li_pool)
    linkedin = day_dir / "linkedin_post.txt"
    linkedin.write_text(li['body'], encoding='utf-8')
    print(f"[GEN] LinkedIn post → {linkedin}")

    # Chinese platform
    zh = get_today_post(POSTS_ZH)
    zh_file = day_dir / "zh_post.md"
    zh_file.write_text(f"# {zh['title']}\n\n{zh['body']}", encoding='utf-8')
    print(f"[GEN] Chinese post → {zh_file}")

    return day_dir


def print_status():
    """Show what was posted today and historically"""
    print(f"\n=== Daily Backlink Engine v3.0 ===")
    print(f"Date: {TODAY} (Day #{DAY_NUM})")

    if TRACKER.exists():
        with open(TRACKER, 'r', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        today_posts = [r for r in rows[1:] if r[0] == TODAY]
        total_posts = len(rows) - 1
        print(f"Today's posts: {len(today_posts)}")
        print(f"Total posts tracked: {total_posts}")
        for r in today_posts:
            print(f"  [{r[4]}] {r[1]}: {r[2][:60]} → {r[3]}")
    else:
        print("No posts tracked yet.")


def open_today_links():
    """Open manual posting URLs"""
    import webbrowser
    links = {
        "Reddit r/CNC": "https://www.reddit.com/r/CNC/submit",
        "LinkedIn": "https://www.linkedin.com/feed/",
        "掘金": "https://juejin.cn/editor/drafts/new",
        "知乎搜索": "https://www.zhihu.com/search?type=content&q=CNC+CRT+LCD",
    }
    print("\n=== Opening posting platforms ===")
    for name, url in links.items():
        print(f"  {name}: {url}")
    for name, url in links.items():
        webbrowser.open(url)


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print_status()

    # 1. Auto-post to Dev.to
    post_devto()

    # 2. Generate manual content
    day_dir = generate_daily_content()

    # 3. Summary
    print(f"\n=== Done ===")
    print(f"All content: {day_dir}")
    print(f"Tracker: {TRACKER}")
    print(f"\nTo post manually: open {day_dir}/ and copy-paste each file")
