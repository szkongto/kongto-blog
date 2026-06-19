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

DEVTO_USED = OUTPUT / "devto_canonicals.json"

def load_devto_used():
    """Load set of canonical URLs already used on Dev.to."""
    if DEVTO_USED.exists():
        return set(json.loads(DEVTO_USED.read_text(encoding='utf-8')))
    return set()

def save_devto_used(canonical):
    """Record a canonical URL as used on Dev.to."""
    used = load_devto_used()
    used.add(canonical)
    DEVTO_USED.write_text(json.dumps(sorted(used), indent=2), encoding='utf-8')

def pick_devto(articles):
    """Pick an article for Dev.to, avoiding used canonical URLs."""
    used = load_devto_used()

    for a in articles:
        if a["canonical"] not in used:
            return a

    # All used — pick oldest (first in list) and rotate
    print("  [INFO] All canonicals used, recycling oldest")
    return articles[0]

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
        "devto_tags": ["cnc", "manufacturing", "engineering", "economics"],
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
| LCD module | $180-280 |
| Installation | 10 min (DIY) |
| Lifespan | 5-7 years continuous |
| 5-Year Total | **$180-280** |

## Why CRT Repairs Keep Failing

CRT displays were discontinued 15+ years ago. "Repairs" use flyback transformers and capacitors harvested from donor units — all 20+ years old themselves.

## The Hidden Cost: Machine Downtime

A CNC down 3 days waiting for CRT repair at $500/day production value = $1,500 lost output + $400 repair = $1,900 real cost per incident.

For $180-280, eliminate the CRT failure cycle permanently.

Cost comparison: [{SITE}/comparison-kongto-vs-competitors.html]({SITE}/comparison-kongto-vs-competitors.html)
Model guides: [{SITE}]({SITE})""",
    },
    {
        "title": "How to Identify Your CNC CRT Model Before Ordering a Replacement LCD",
        "devto_tags": ["cnc", "manufacturing", "engineering", "tutorial"],
        "canonical": f"{SITE}/brands/FANUC.html",
        "body_devto": """## First Step: Find Your CRT Model Number

Before ordering any replacement, you need to identify exactly what CRT is in your machine.

## Where to Look

The model label is on the **back** of the CRT housing. You'll need:
- A flashlight (shop lighting is rarely good enough)
- Your phone camera (take a photo — it's easier than squinting)
- Possibly a mirror if the label faces the wall

## Reading the Label by Brand

### FANUC
Label format: `A61L-0001-XXXX` or `D9MM-11A`
- A61L-0001-**0093** = 9" amber monochrome, Honda MR-20M
- A61L-0001-**0092** = 9" amber, similar to 0093
- A61L-0001-**0074** = 14" color
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

FANUC brand guides: [{SITE}/brands/FANUC.html]({SITE}/brands/FANUC.html)
Full compatibility matrix: [{SITE}/en/compatibility-matrix.html]({SITE}/en/compatibility-matrix.html)""",
    },
    {
        "title": "Mitsubishi CNC CRT to LCD Upgrade: MDT962B and BM09DF Replacement Guide",
        "devto_tags": ["cnc", "manufacturing", "engineering", "mitsubishi"],
        "canonical": f"{SITE}/brands/Mitsubishi.html",
        "body_devto": """## Mitsubishi M64/E60/M500: Complete Display Upgrade

Mitsubishi CNC controls from the 1990s use 9" monochrome CRTs that are now failing. Here's the direct replacement guide.

## Compatible Models

| CRT Model | System | Connector | Power |
|-----------|--------|-----------|-------|
| MDT962B | M64 | 20-pin | DC 24V |
| BM09DF | E60 | 20-pin | DC 24V |
| FCUA-CT100 | M500/M520 | 26-pin | DC 24V |

## Symptoms of Failure

- Screen goes dark after 5-10 minutes of operation
- Flickering when the spindle motor starts
- Dim display even at maximum brightness
- Horizontal lines across the screen
- CRT takes 30+ minutes to stabilize on cold mornings

## The Replacement Process

1. Power off, verify with multimeter
2. Remove 4 mounting bolts from CRT bezel
3. Disconnect the 20-pin or 26-pin connector
4. Connect same cable to replacement LCD
5. Mount LCD with original hardware
6. Power on — no parameters needed

The Mitsubishi M64 CRT power supply delivers clean DC 24V, so LCD compatibility is straightforward — no AC voltage concerns like Siemens systems.

## Pro Tip: Connector Count

Count your pins BEFORE ordering. Mitsubishi used both 20-pin and 26-pin variants. They are NOT interchangeable even within the same machine series.

Full Mitsubishi upgrade guide: [{SITE}/brands/Mitsubishi.html]({SITE}/brands/Mitsubishi.html)
Compatibility matrix: [{SITE}]({SITE})""",
    },
    {
        "title": "Siemens SINUMERIK CRT Replacement: The Critical AC110V Difference",
        "devto_tags": ["cnc", "manufacturing", "engineering", "siemens"],
        "canonical": f"{SITE}/brands/Siemens.html",
        "body_devto": """## Siemens ≠ Japanese CNC: The Power Supply Difference

If you maintain a Siemens SINUMERIK 810, 820, or 840D, there's one thing you absolutely must know before ordering a replacement display:

**Siemens uses AC 110V. Japanese CNCs use DC 24V.**

## Compatible Siemens Models

| CRT Model | System | Connector | Power |
|-----------|--------|-----------|-------|
| 6FC3998-7FA20 | SINUMERIK 810/820 | DB-25 (25-pin) | **AC 110V** |
| SM0901-579417-TA | SINUMERIK 810/820 | DB-25 | **AC 110V** |

## The DB-25 Connector

Siemens uses a DB-25 D-Sub connector — completely different from the Honda MR-20M used by FANUC or the 20/26-pin connectors on Mitsubishi. A "universal" LCD won't work here.

## Real-World Failure

In 2023, a machine shop ordered a $180 LCD module, connected it to their Siemens 840D, and powered up. The DC-rated module received AC 110V. Result: instant component destruction. The module's power section was designed for DC 24V, not the 110V AC the Siemens CRT supply delivers.

They lost $180 in hardware and 2 days of production waiting for the correct AC-rated replacement.

## The Correct Approach

When ordering a Siemens LCD replacement:
1. Verify the module explicitly supports AC 110V input
2. Confirm DB-25 connector compatibility
3. Check the exact SINUMERIK control version (810, 820, 840D)

Full Siemens guide: [{SITE}/brands/Siemens.html]({SITE}/brands/Siemens.html)
All brands: [{SITE}]({SITE})""",
    },
    {
        "title": "Mazak CNC CRT Replacement: CD1472-D1M and C-5470NS LCD Upgrade Guide",
        "devto_tags": ["cnc", "manufacturing", "engineering", "mazak"],
        "canonical": f"{SITE}/brands/MAZAK.html",
        "body_devto": """## Mazak T-32/M-32: 26-Pin Proprietary Display

Mazak CRTs use a proprietary 26-pin connector that is physically incompatible with FANUC (20-pin) and Mitsubishi (20/26-pin) modules. Here's what works.

## Compatible Mazak CRT Models

| CRT Model | System | Size | Type |
|-----------|--------|------|------|
| CD1472-D1M | T-32/M-32 | 10.4" | Color TFT CRT |
| C-5470NS | M-32/M-Plus | 10.4" | Color TFT CRT |
| DR5614 | T-32/T-Plus | 10.4" | Color TFT CRT |
| MDT-1283B | M-32/M-Plus | 10.4" | Color TFT CRT |

## The Mazak Difference

Unlike FANUC and Mitsubishi controls that use 9" amber monochrome CRTs, Mazak machines shipped with 10.4" color TFT displays. This means:
- Higher resolution factory display
- Different connector pinout (26-pin proprietary)
- Same DC 24V power as Japanese CNCs

## Installation Notes

The Mazak 26-pin connector plugs directly into compatible LCD replacements. No adapter boards, no signal converters, no rewiring needed. Direct swap.

## Warning: Brand Confusion

Some suppliers list "FANUC/Mazak compatible" displays. These are physically incompatible. Mazak uses a 26-pin connector. FANUC uses the 20-pin Honda MR-20M. They do not mate.

Full Mazak guides: [{SITE}/brands/MAZAK.html]({SITE}/brands/MAZAK.html)
Compatibility check: [{SITE}]({SITE})""",
    },
    {
        "title": "Okuma OSP CNC Display Upgrade: 14-Pin and 20-Pin LCD Replacement",
        "devto_tags": ["cnc", "manufacturing", "engineering", "okuma"],
        "canonical": f"{SITE}/brands/OKUMA.html",
        "body_devto": """## Okuma OSP 5000/5020/7000 Display Retrofit

Okuma CNCs use different connectors depending on the OSP control generation. Here's the complete reference.

## Connector Types by OSP Generation

| Control | CRT Size | Connector | Power |
|---------|----------|-----------|-------|
| OSP 5000 | 9" mono | 14-pin | DC 24V |
| OSP 5020 | 9" mono | 14-pin | DC 24V |
| OSP 7000 | 9" mono | 20-pin | DC 24V |

## 14-Pin vs 20-Pin

The OSP 5000/5020 uses a 14-pin connector — fewer pins than FANUC (20-pin) or Mitsubishi (20/26-pin). The OSP 7000 switched to 20-pin. They are NOT cross-compatible.

## Okuma-Specific Failure Patterns

Okuma CRTs tend to fail differently from FANUC:
- **OSP 5000**: High-voltage section failures (flyback transformer)
- **OSP 5020**: Capacitor aging in the deflection circuit
- **OSP 7000**: Screen burn-in from static parameter displays

## What Works

LCD replacements for Okuma use the original 14-pin or 20-pin connector, draw DC 24V power from the same cable, and mount with the original screw pattern. No external power supplies needed.

Full Okuma guides: [{SITE}/brands/OKUMA.html]({SITE}/brands/OKUMA.html)
All brands: [{SITE}]({SITE})""",
    },
    {
        "title": "Haas CNC CRT to LCD: 9-Pin D-Sub Display Replacement for VF/ST/SL Series",
        "devto_tags": ["cnc", "manufacturing", "engineering", "haas"],
        "canonical": f"{SITE}/brands/HAAS.html",
        "body_devto": """## Haas VF/ST/SL: Early Models Need DC 12V LCD

Early Haas machines use a unique 9-pin D-Sub connector with DC 12V power — different from every other major CNC brand.

## Compatible Haas Models

| Series | Connector | Power | Notes |
|--------|-----------|-------|-------|
| VF (early) | 9-pin D-Sub | DC 12V | Not 24V! |
| ST (early) | 9-pin D-Sub | DC 12V | Same as VF |
| SL (early) | 9-pin D-Sub | DC 12V | Same as VF |

## The DC 12V Difference

Most industrial CNCs use DC 24V for display power. Haas used DC 12V on early machines. A DC 24V LCD module connected to a Haas will NOT receive enough voltage to operate reliably — dim, flickering, or no display at all.

## Visual Identification

The 9-pin D-Sub is easily recognized:
- Trapezoid-shaped metal shell
- 9 pins in a 5+4 staggered arrangement
- Same physical shape as old PC serial ports (but different pinout!)

## Installation

Direct plug-and-play with compatible 9-pin D-Sub + DC 12V LCD modules. Same 4-screw mounting pattern. No control parameter changes needed.

Full Haas guides: [{SITE}/brands/HAAS.html]({SITE}/brands/HAAS.html)
Cross-brand compatibility: [{SITE}]({SITE})""",
    },
    {
        "title": "FANUC A61L-0001-0093: The Most Common CNC CRT and Its Direct LCD Replacement",
        "devto_tags": ["cnc", "manufacturing", "engineering", "fanuc"],
        "canonical": f"{SITE}/case-studies.html",
        "body_devto": """## The Workhorse CRT That's Everywhere

The FANUC A61L-0001-0093 (also labeled D9MM-11A) is the single most common CNC display in the world. Found on FANUC 0-TC, 0-MC, 18-T, 21-T, and Power Mate controls.

## Why It Fails

Every A61L-0001-0093 was manufactured between 1988-2003. The youngest unit is 20+ years old. The typical CRT is at year 25-30.

Failure points:
1. **Phosphor burn-in**: Permanent ghosting from static parameter screens
2. **Flyback transformer**: HV section failure = no display
3. **Capacitors**: Flickering, unstable brightness
4. **Tube wear**: Max brightness = still too dim to read

## The LCD Replacement

The replacement LCD module for A61L-0001-0093:
- Uses the original Honda MR-20M connector
- Draws DC 24V from the original cable
- Fits the original mounting points
- 10-minute installation

## Real Shop Results

Case study: 12-machine FANUC fleet upgrade
- Before: 3-5 CRT failures/year, 2+ days downtime each
- After: Zero LCD failures in 18 months
- Total cost: Under $3,000 (12 LCD modules)
- Previous annual repair spend: $5,600+

D9MM-11A and A61L-0001-0093 are electrically identical — the same replacement works for both.

Full case studies: [{SITE}/case-studies.html]({SITE}/case-studies.html)
FANUC guides: [{SITE}/brands/FANUC.html]({SITE}/brands/FANUC.html)""",
    },
    {
        "title": "5 Signs Your CNC CRT Is About to Die — And What to Do About It",
        "devto_tags": ["cnc", "manufacturing", "maintenance", "engineering"],
        "canonical": f"{SITE}/en/",
        "body_devto": """## Don't Wait for Complete Failure

CRT displays rarely fail without warning. Here are the 5 signs that tell you it's time to plan a replacement — before the machine goes dark mid-production.

## Sign 1: Brightness at Maximum, Still Too Dim

The phosphor coating inside the CRT tube degrades over time. When you're at 100% brightness and the characters are still hard to read under shop lighting, the tube is end-of-life. No repair restores phosphor — only a tube replacement helps, and new tubes haven't been manufactured in 15+ years.

## Sign 2: Flickering on Cold Start (20+ Minutes to Stabilize)

Aging electrolytic capacitors in the power supply section can't hold their rated capacitance. As they warm up, they slowly recover. This gets worse over time as caps degrade further.

## Sign 3: Permanent Burn-In

If you can read parameter screen text even with the machine off, the phosphor is permanently burned. This is cosmetic until it isn't — the burned areas eventually lose all phosphor and stop displaying entirely.

## Sign 4: Screen Shrinking or Distorting at Edges

Classic flyback transformer failure symptom. The HV section can't maintain proper voltage. It will get worse, and eventually the HV section fails completely = blank screen.

## Sign 5: High-Pitched Whine

A failing flyback transformer often produces an audible whine at 15-20 kHz. Some operators can hear it (younger ears), some can't. If you hear a high-pitched noise from the CRT enclosure, the flyback is failing.

## The Bottom Line

Any one of these signs = start planning. Two or more = order the replacement now, before the machine goes down mid-job.

Model identification guide: [{SITE}/en/compatibility-matrix.html]({SITE}/en/compatibility-matrix.html)
All brand guides: [{SITE}]({SITE})""",
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

    article = pick_devto(ARTICLES)
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
        save_devto_used(article["canonical"])
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


def post_gitlab():
    """GitLab Snippets - DA 96, Dofollow, public snippet indexed by Google"""
    cfg = load_config()
    pat = cfg.get("gitlab_pat")
    if not pat:
        print("[SKIP] GitLab - no PAT")
        return None

    article = pick(ARTICLES)
    print(f"\n[GitLab] {article['title'][:70]}...")

    # Build snippet content: title + key points + link
    snippet_content = f"""# {article['title']}

{article['body_devto']}

---
*Reference: [{SITE}]({SITE})*
"""

    resp = requests.post(
        "https://gitlab.com/api/v4/snippets",
        headers={"PRIVATE-TOKEN": pat, "Content-Type": "application/json"},
        json={
            "title": article["title"][:70],
            "file_name": "cnc-display-upgrade-guide.md",
            "content": snippet_content,
            "visibility": "public",
        },
        timeout=30
    )

    if resp.status_code in [200, 201]:
        url = resp.json().get("web_url", "")
        print(f"  [OK] {url}")
        log_post("GitLab", article["title"], url)
        return url
    print(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:150]}")
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
# Git 自动提交 + 推送
# ============================================================
def auto_git_push():
    """Commit today's backlink results and push to GitHub via SSH."""
    import subprocess
    try:
        # Check if we're in a git repo
        r = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, cwd=str(BASE))
        if r.returncode != 0:
            print("[GIT] Not a git repo, skipping")
            return

        # Stage tracker + canonicals + today's content
        files = ["backlinks_daily/post_tracker.csv", "backlinks_daily/devto_canonicals.json"]
        today_dir = OUTPUT / TODAY
        if today_dir.exists():
            files.append(f"backlinks_daily/{TODAY}")

        for f in files:
            subprocess.run(["git", "add", f], capture_output=True, cwd=str(BASE))

        # Check if there are changes
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, cwd=str(BASE))
        if r.returncode == 0:
            print("[GIT] No changes to commit")
            return

        # Commit
        msg = f"Daily backlinks {TODAY}: auto-published"
        r = subprocess.run(["git", "commit", "-m", msg], capture_output=True, cwd=str(BASE))
        if r.returncode != 0:
            err = r.stderr.decode('utf-8', errors='replace')[:200]
            print(f"[GIT] Commit failed: {err}")
            return

        # Push
        r = subprocess.run(["git", "push", "origin", "main"], capture_output=True, cwd=str(BASE))
        if r.returncode != 0:
            err = r.stderr.decode('utf-8', errors='replace')[:200]
            print(f"[GIT] Push failed: {err}")
            # Try pull+rebase then push
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, cwd=str(BASE))
            r = subprocess.run(["git", "push", "origin", "main"], capture_output=True, cwd=str(BASE))
            if r.returncode == 0:
                print("[GIT] Pushed (after rebase)")
            else:
                print(f"[GIT] Push still failed: {r.stderr.decode('utf-8', errors='replace')[:200]}")
                return

        print(f"[GIT] Pushed: {msg}")
    except Exception as e:
        print(f"[GIT] Error: {e}")


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
    r = post_gitlab()
    if r: results["GitLab"] = r

    # === GENERATE MANUAL ===
    day_dir = gen_manual_content()

    # === SUMMARY ===
    print(f"\n{'='*50}")
    print(f"DONE: {len(results)} auto-published + manual content generated")
    for k, v in results.items():
        print(f"  [{k}] {v}")
    print(f"  [Manual] {day_dir}")
    print(f"{'='*50}")

    # === AUTO GIT PUSH ===
    auto_git_push()
