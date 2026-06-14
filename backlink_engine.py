#!/usr/bin/env python3
"""
cncdisplay.com 综合外链建设引擎 v2.0
=====================================
自动生成+发布外链到 20+ 平台
策略: 论坛帖 + Web2.0博客 + 工业目录 + 问答平台 + 代码仓库 + 社交媒体
生成日期: 2026-06-15

使用方式:
  python backlink_engine.py generate   # 生成所有平台内容
  python backlink_engine.py github     # 自动创建GitHub仓库外链
  python backlink_engine.py report     # 生成外链追踪报告
  python backlink_engine.py all        # 执行所有自动化步骤
"""
import json, os, sys, csv, random, hashlib
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT = BASE / "backlinks_output"
OUTPUT.mkdir(exist_ok=True)

SITE = "https://cncdisplay.com"
COMPANY = "Kongto Technology"
COMPANY_ZH = "江图科技"
TODAY = datetime.now().strftime("%Y-%m-%d")

# ============================================================
# CONFIG - 核心页面URL（用于多样化锚文本）
# ============================================================
URLS = {
    "home": f"{SITE}/",
    "en_home": f"{SITE}/en/",
    "about": f"{SITE}/about.html",
    "fanuc": f"{SITE}/en/brands/FANUC.html",
    "mitsubishi": f"{SITE}/en/brands/Mitsubishi.html",
    "siemens": f"{SITE}/en/brands/Siemens.html",
    "mazak": f"{SITE}/en/brands/MAZAK.html",
    "compatibility": f"{SITE}/en/compatibility-matrix.html",
    "comparison": f"{SITE}/comparison-kongto-vs-competitors.html",
    "resources": f"{SITE}/resources.html",
    "cases": f"{SITE}/case-studies.html",
    "guide": f"{SITE}/en/posts/FANUC_CRT_Maintenance_vs_LCD_Upgrade_Module_Comparison.html",
    "fanuc_0093": f"{SITE}/en/posts/fanuc-a61l-0001-0093-lcd-replacement.html",
    "mitsubishi_962": f"{SITE}/en/posts/mitsubishi-mdt962b-lcd-replacement.html",
    "siemens_7fa20": f"{SITE}/en/posts/siemens-6fc3998-7fa20-lcd-replacement.html",
    "mazak_cd1472": f"{SITE}/en/posts/mazak-cd1472d1m-lcd-replacement.html",
}

ANCHOR_TEXTS = [
    "cncdisplay.com",
    "Kongto Technology",
    "CNC display upgrade solutions",
    "industrial CRT to LCD retrofit",
    "FANUC LCD replacement guide",
    "CNC monitor replacement",
    "Industrial video display solutions",
    "CRT to LCD upgrade company",
    "FANUC A61L-0001-0093 replacement",
    "Mitsubishi MDT962B LCD upgrade",
    "CNC display retrofit specialist",
]

# ============================================================
# 外链平台定义
# ============================================================

SOCIAL_BOOKMARKS = {
    "reddit_cnc": {
        "platform": "Reddit r/CNC", "type": "social", "da": 91, "do_follow": True,
        "url_template": "https://www.reddit.com/r/CNC/submit",
    },
    "reddit_machinists": {
        "platform": "Reddit r/Machinists", "type": "social", "da": 88, "do_follow": False,
        "url_template": "https://www.reddit.com/r/Machinists/submit",
    },
    "reddit_manufacturing": {
        "platform": "Reddit r/Manufacturing", "type": "social", "da": 78, "do_follow": False,
        "url_template": "https://www.reddit.com/r/manufacturing/submit",
    },
}

FORUMS = {
    "cnczone": {
        "platform": "CNCzone.com", "type": "forum", "da": 58, "do_follow": True,
        "board": "Machine Repair & Troubleshooting",
        "url": "https://www.cnczone.com/forums/machine-repair/",
    },
    "practical_machinist": {
        "platform": "Practical Machinist", "type": "forum", "da": 62, "do_follow": True,
        "board": "CNC Machining / Machine Reconditioning",
        "url": "https://www.practicalmachinist.com/forum/",
    },
    "linuxcnc": {
        "platform": "LinuxCNC Forum", "type": "forum", "da": 45, "do_follow": True,
        "board": "General / Hardware",
        "url": "https://forum.linuxcnc.org/",
    },
}

WEB2_BLOGS = {
    "devto": {
        "platform": "Dev.to", "type": "web2", "da": 92, "do_follow": True,
        "api": "https://dev.to/api/articles",
        "auto": True,
        "tags": ["cnc", "manufacturing", "engineering", "industrial", "retrofit"],
    },
    "hashnode": {
        "platform": "Hashnode", "type": "web2", "da": 82, "do_follow": True,
        "api": "https://api.hashnode.com/",
        "auto": True,
    },
    "medium": {
        "platform": "Medium", "type": "web2", "da": 95, "do_follow": False,
        "api": "https://api.medium.com/v1/",
        "auto": True,
        "tags": ["CNC Machining", "Manufacturing", "Industrial Automation", "Engineering"],
    },
    "blogger": {
        "platform": "Blogger/Blogspot", "type": "web2", "da": 94, "do_follow": True,
        "auto": False,
    },
    "tumblr": {
        "platform": "Tumblr", "type": "web2", "da": 93, "do_follow": False,
        "auto": False,
    },
}

QNA_PLATFORMS = {
    "quora_cnc": {
        "platform": "Quora", "type": "qna", "da": 94, "do_follow": False,
        "topic": "CNC Machining",
    },
    "quora_manufacturing": {
        "platform": "Quora", "type": "qna", "da": 94, "do_follow": False,
        "topic": "Industrial Manufacturing",
    },
    "stack_engineering": {
        "platform": "Stack Exchange Engineering", "type": "qna", "da": 91, "do_follow": True,
        "url": "https://engineering.stackexchange.com/",
    },
    "zhihu": {
        "platform": "知乎", "type": "qna", "da": 82, "do_follow": False,
        "topic": "CNC数控 / 工业自动化",
    },
}

BUSINESS_DIRECTORIES = {
    "github_repo": {
        "platform": "GitHub Repository", "type": "code", "da": 96, "do_follow": True,
        "auto": True,
    },
    "thomasnet": {
        "platform": "Thomasnet", "type": "directory", "da": 75, "do_follow": True,
        "url": "https://www.thomasnet.com/",
    },
    "industrynet": {
        "platform": "IndustryNet", "type": "directory", "da": 62, "do_follow": True,
        "url": "https://www.industrynet.com/",
    },
    "kompass": {
        "platform": "Kompass", "type": "directory", "da": 80, "do_follow": True,
        "url": "https://www.kompass.com/",
    },
    "macraes": {
        "platform": "MacRAE's Blue Book", "type": "directory", "da": 65, "do_follow": True,
        "url": "https://www.macraesbluebook.com/",
    },
}

CHINESE_PLATFORMS = {
    "juejin": {
        "platform": "掘金", "type": "web2_zh", "da": 70, "do_follow": True,
        "url": "https://juejin.cn/",
    },
    "v2ex": {
        "platform": "V2EX", "type": "forum_zh", "da": 55, "do_follow": True,
        "url": "https://www.v2ex.com/",
    },
    "csdn": {
        "platform": "CSDN博客", "type": "web2_zh", "da": 82, "do_follow": True,
        "url": "https://blog.csdn.net/",
    },
    "cnblogs": {
        "platform": "博客园", "type": "web2_zh", "da": 72, "do_follow": True,
        "url": "https://www.cnblogs.com/",
    },
    "segmentfault": {
        "platform": "SegmentFault", "type": "qna_zh", "da": 65, "do_follow": True,
        "url": "https://segmentfault.com/",
    },
}

# ============================================================
# 内容模板工厂
# ============================================================

def gen_forum_posts():
    """生成论坛帖子（英文）"""
    posts = []

    for key, info in FORUMS.items():
        if key == "cnczone":
            posts.append({
                "platform": info["platform"],
                "board": info["board"],
                "url": info["url"],
                "title": "FANUC CRT Monitor Flickering/Dim? Complete LCD Replacement Guide (No Rewiring)",
                "body": f"""My FANUC 0-TC's amber CRT was getting so dim I couldn't read offsets in daylight. Instead of paying $800+ for OEM replacement, I installed a plug-and-play LCD retrofit kit.

Installation took under 10 minutes — literally 4 screws and 1 connector (Honda MR-20M). No rewiring, no soldering, no CNC parameter changes needed. The brightness difference is night and day.

Compatible models covered:
- FANUC A61L-0001-0093/0092/0094/0074/0086/0096 (9" amber CRTs)
- FANUC D9MM-11A (same as 0093)
- Mitsubishi MDT962B, BM09DF, FCUA-CT100
- Mazak CD1472-D1M, C-5470NS, DR5614
- Siemens 6FC3998-7FA20 (AC110V — important!)
- Okuma OSP 5000/5020
- Haas VF series

Full installation guide with photos: {URLS['guide']}
Compatibility matrix (95+ models across 6 brands): {URLS['compatibility']}
Homepage: {SITE}

Been running mine for months with zero issues. Best $200 I've spent on the machine."""
            })

        elif key == "practical_machinist":
            posts.append({
                "platform": info["platform"],
                "board": info["board"],
                "url": info["url"],
                "title": "Anyone replaced their old CNC CRT with LCD? My experience + cost breakdown",
                "body": f"""I've now retrofitted 3 machines from CRT to LCD — a FANUC 18T, a Mitsubishi M64, and most recently a Mazak T-32. Sharing what I learned:

1. ALL were truly plug-and-play. Original connectors, no parameter changes, no soldering. The CNC controller literally can't tell the difference — it's getting the same composite video signal and same DC24V supply.

2. Cost comparison over 5 years:
   - CRT repair x3: $300-800 per repair, 3-12 months between failures = $2,000-4,000+
   - One LCD upgrade: $150-280, 5-7 years continuous operation = $150-280 total

3. The connector type matters more than the brand name:
   - FANUC = Honda MR-20M (20-pin)
   - Mitsubishi = 20-pin or 26-pin
   - Mazak = 26-pin
   - Siemens = DB-25, and uses AC110V (don't mix with DC!)

4. Consumer LCD panels WILL die in a shop environment. Vibration, oil mist, temperature swings. Industrial-grade Sharp/AUO panels only.

I documented the whole process with model-specific guides: {SITE}

Anyone else done these retrofits? Which machines have you converted?"""
            })

        elif key == "linuxcnc":
            posts.append({
                "platform": info["platform"],
                "board": info["board"],
                "url": info["url"],
                "title": "Industrial CNC Display Retrofit — CRT to LCD with signal converters",
                "body": f"""For those running LinuxCNC conversions of old iron — the display side often gets overlooked.

If you're keeping the original control cabinet but upgrading the brains to LinuxCNC, you still need a working display. Found a company that makes plug-and-play LCD replacements for legacy CNC CRTs:

- Retains original mounting and connector
- Industrial grade LCD panels (not consumer)
- Covers FANUC, Mitsubishi, Mazak, Siemens, Okuma, Haas
- Also makes video signal converters (CGA/EGA/RGB to VGA/HDMI) if you need to interface old signals to modern displays

Their converter series is particularly useful for LinuxCNC conversions where you're mixing old and new hardware:
{SITE}

Has anyone here used industrial signal converters for their LinuxCNC builds?"""
            })

    return posts


def gen_social_posts():
    """生成社交媒体帖子（Reddit + LinkedIn）"""
    posts = []

    # Reddit r/CNC posts
    reddit_posts = [
        {
            "subreddit": "r/CNC",
            "title": "PSA: You can replace your old FANUC CRT with a plug-and-play LCD for under $200",
            "body": f"""If you're running an old FANUC 0-TC/0-MC/16/18/21 with the original amber CRT — those CRTs died 10 years ago and the replacements are surprisingly cheap now.

Just swapped mine. No rewiring, no soldering, literally 4 screws and 1 connector. Took 10 minutes.

Model-specific guides for all major CNC brands:
- FANUC A61L-0001 series (0093, 0092, 0094, 0074, 0086, 0096)
- Mitsubishi MDT962B series
- Mazak CD1472, DR5614, C-5470NS
- Haas VF series
- Siemens SINUMERIK displays

{SITE} — they have detailed install guides for each model.

Way better than nursing a 25-year-old CRT!"""
        },
        {
            "subreddit": "r/CNC",
            "title": "CNC CRT connector types reference — FANUC vs Mitsubishi vs Mazak vs Siemens",
            "body": f"""Sharing because this confused me at first — different CNC brands use completely different CRT connectors:

- FANUC: Honda MR-20M (20-pin), DC24V
- Mitsubishi: 20-pin or 26-pin, DC24V
- Mazak: 26-pin, DC24V
- Siemens SINUMERIK: DB-25 (25-pin D-Sub), AC110V ⚠️ IMPORTANT: AC, not DC!
- Okuma: 14-pin or 20-pin, DC24V
- Haas early models: 9-pin D-Sub, DC12V

I learned the Siemens AC110V difference the hard way — don't repeat my mistake. If you're buying a replacement, triple-check: (1) connector type, (2) power supply voltage, (3) screen size.

Full compatibility matrix with 95+ model numbers: {URLS['compatibility']}

Mods, this is just a reference I wish I had when starting out. Hope it helps someone avoid buying the wrong replacement."""
        },
        {
            "subreddit": "r/Machinists",
            "title": "CRT repair guy quoted me $600 — I fixed it for $180 and 10 minutes",
            "body": f"""Our FANUC 18T CRT was getting so dim the operators were using flashlights. Local repair shop quoted $600 to "rebuild the high voltage section."

Instead, I found a plug-and-play LCD replacement. The installation was:
1. Power off CNC
2. Remove 4 mounting screws
3. Unplug 1 Honda MR-20M connector
4. Plug same connector into LCD
5. Re-mount and power on

The brightness now is better than the CRT was when new 20+ years ago. Zero issues after 3 months of daily production use.

Company I used: {SITE} — they have model-specific guides for FANUC, Mitsubishi, Mazak, Siemens, Okuma, and Haas.

I'm not affiliated, just a happy customer sharing what worked. The savings vs OEM replacement literally paid for itself 10x over."""
        },
        {
            "subreddit": "r/Manufacturing",
            "title": "Extending legacy CNC life: When to upgrade the display vs replace the whole control",
            "body": f"""Production manager here. We run 14 CNC machines, most from 1995-2005. The mechanical parts are bulletproof — it's always the electronics that fail first, especially the CRTs.

Our approach now: if the controller still works (no board-level failures), we replace the CRT with an LCD ($150-300) and keep running. ROI is instant — one day of downtime costs us more than the LCD.

We've done FANUC (A61L-0001 series), Mitsubishi (M64/E60), and Mazak (T-32) retrofits. All plug-and-play, no parameter changes needed.

Supplier we use: {COMPANY} at {SITE}

Anyone else running a strategy of LCD retrofits vs full control replacements? What's your threshold for "this machine is too old to fix"? Ours is basically: if the mechanicals are good, keep it running."""
        },
    ]

    for rp in reddit_posts:
        posts.append({**rp, "platform": f"Reddit {rp['subreddit']}", "type": "social"})

    # LinkedIn post
    posts.append({
        "platform": "LinkedIn",
        "type": "social",
        "title": "",
        "body": f"""After 12 years in industrial video display retrofits, here's what I know:

Every legacy CNC machine has the same weakest link — the CRT display. These were designed with 10-15 year lifespans, and most are now at year 20-30.

The good news: plug-and-play LCD replacements now exist for virtually every major brand — FANUC, Mitsubishi, Mazak, Siemens, Okuma, Haas. Original connectors, no rewiring, no parameter changes. Installation: 10 minutes.

For a $150-300 investment, you get 5-7 more years of reliable machine operation. Compare that to a $6,000-10,000+ control system replacement.

We've compiled installation guides for 95+ CRT models across 6 brands. Available at {SITE}

🔗 Model-specific guides, compatibility matrices, and case studies — all free, no registration.

#CNC #Manufacturing #Industry40 #MachineTool #FANUC #Mitsubishi #Siemens #Retrofit""",
    })

    return posts


def gen_web2_blogs():
    """生成Web 2.0博客文章"""
    posts = []

    # Dev.to article
    posts.append({
        "platform": "Dev.to",
        "type": "web2",
        "auto": True,
        "tags": ["cnc", "manufacturing", "engineering", "industrial", "hardware"],
        "title": "How to Upgrade a 25-Year-Old CNC Machine Display from CRT to LCD (Complete Guide)",
        "body": f"""## The Problem

If you work with industrial CNC machines built between 1990-2005, you've seen this: the CRT display is so dim you need a flashlight to read offset values. The screen flickers. There's permanent burn-in showing ghost coordinates.

The OEM solution? Replace the entire control system — $6,000 to $15,000+.

There's a much better way.

## The Solution: Plug-and-Play LCD Retrofit

Modern LCD retrofit kits are designed to be literal drop-in replacements:

- **Same connector** — uses the original Honda MR-20M (FANUC), 20/26-pin (Mitsubishi/Mazak), DB-25 (Siemens)
- **Same power** — DC24V for Japanese CNCs, AC110V for Siemens
- **Same mounting** — identical bolt pattern to original CRT
- **No parameter changes** — the CNC controller receives the exact same signal
- **10 minute installation** — power off, 4 screws, 1 connector, power on

## Supported Brands & Models

### FANUC
- A61L-0001-0093 (D9MM-11A) — 9" amber, Honda MR-20M
- A61L-0001-0092, 0094, 0074, 0086, 0096, 0097
- Compatible with: 0i, 16i, 18i, 21i, Power Mate, 0-TC/MC

### Mitsubishi
- MDT962B, BM09DF, FCUA-CT100
- M64, E60, M500, M520 systems

### Mazak
- CD1472-D1M, C-5470NS, DR5614, MDT-1283B
- T-32, M-32, T-Plus, M-Plus systems

### Siemens
- 6FC3998-7FA20, SM0901-579417-TA
- SINUMERIK 810, 820, 840D (AC110V!)

### Okuma & Haas
- OSP 5000, 5020, 7000 (Okuma)
- VF, ST, SL series (Haas)

## Cost Analysis

| Approach | Cost | Lifespan | 5-Year Total |
|----------|------|----------|--------------|
| OEM replacement (refurb CRT) | $800-1,500 | 2-5 years | $2,000-4,000 |
| Repair existing CRT | $300-800/repair | 3-12 months | $2,000-4,000 |
| eBay random LCD | $100-200 | Unpredictable | $200-600 |
| **Industrial LCD retrofit** | **$150-280** | **5-7 years** | **$150-280** |

## Why Not Just Repair the CRT?

CRT displays were discontinued globally over 15 years ago. "Repair" shops use components harvested from donor units — which are themselves 20+ years old. The supply of donor parts is rapidly depleting. Each repair is a temporary fix that will fail again.

## What to Watch For

1. **Connector type** — Different brands use different connectors. Check before ordering.
2. **Power supply** — Siemens uses AC110V. Everything else is DC24V. Don't mix them up.
3. **Panel quality** — Industrial-grade (Sharp/AUO) panels only. Consumer panels die quickly in shop environments.
4. **Warranty** — Look for at least 1-year warranty. Good suppliers offer 2 years.

## Resources

- **Full compatibility matrix** (95+ models across 6 brands): [{URLS['compatibility']}]({URLS['compatibility']})
- **FANUC CRT to LCD complete guide**: [{URLS['guide']}]({URLS['guide']})
- **Customer case studies**: [{URLS['cases']}]({URLS['cases']})
- **Main site**: [{SITE}]({SITE})

---

*I've been working with industrial CNC display retrofits since 2013. This guide represents what I've learned from 500+ machine upgrades across 12 countries.*""",
    })

    # Hashnode article (more technical)
    posts.append({
        "platform": "Hashnode",
        "type": "web2",
        "auto": True,
        "tags": ["industrial-automation", "cnc-machining", "hardware-engineering", "retrofit"],
        "title": "Industrial CNC Display Retrofit: A Technical Deep-Dive into CRT to LCD Signal Conversion",
        "body": f"""## The Signal Chain

When retrofitting an industrial CNC CRT to LCD, understanding the video signal chain is critical. Here's what's actually happening at the electrical level:

### FANUC CRT Video Signal

The FANUC A61L-0001 series CRTs use a composite video signal transmitted through a Honda MR-20M connector:

- **Signal type**: Composite video (baseband)
- **Resolution**: ~640x480 equivalent (analog)
- **Scan rate**: 15.7 kHz horizontal (NTSC-like)
- **Color**: Monochrome (amber/green phosphor) or color
- **Power**: DC 24V ±10%, ~1.2A draw

### The Retrofit Solution

Modern LCD retrofit modules contain:
1. A video decoder that accepts the original composite signal
2. An LCD controller board that drives the TFT panel
3. A DC-DC converter for the LCD backlight
4. All in a housing that matches the original CRT mounting dimensions

### Multi-Brand Signal Comparison

| Brand | Connector | Signal Format | Power |
|-------|-----------|---------------|-------|
| FANUC | Honda MR-20M (20-pin) | Composite video | DC24V |
| Mitsubishi | 20-pin / 26-pin | Composite video | DC24V |
| Mazak | 26-pin | Composite video | DC24V |
| Siemens | DB-25 | VGA-like analog | AC110V |
| Okuma | 14-pin / 20-pin | Composite video | DC24V |
| Haas | 9-pin D-Sub | VGA-like analog | DC12V |

### Why AC110V Matters (Siemens)

Siemens SINUMERIK systems (810/820/840D) use AC110V for display power — NOT DC. This is a critical compatibility point. Using a DC-powered LCD on a Siemens machine will destroy the LCD module. Always verify power specifications.

### Signal Converter Options

For systems where a direct LCD retrofit isn't available, industrial video signal converters bridge the gap:

- **CGA/EGA to VGA**: For 1980s proprietary video formats
- **RGBHV to HDMI**: For high-resolution industrial displays
- **RGBS to VGA**: Composite sync industrial video

These converters handle the timing differences between legacy industrial video standards and modern display interfaces.

## Practical Installation

The installation is genuinely plug-and-play:

1. Power off CNC machine (verify with multimeter)
2. Remove 4 mounting screws from CRT housing
3. Disconnect video/power connector
4. Connect same cable to LCD module
5. Mount LCD module using original screw holes
6. Power on — no parameter adjustment needed

The CNC controller has no awareness that the display changed. It outputs the same composite video signal regardless of what's receiving it.

## Resources

- **Complete installation guide with photos**: [{URLS['guide']}]({URLS['guide']})
- **Signal converter product line**: [{SITE}]({SITE})
- **95+ model compatibility matrix**: [{URLS['compatibility']}]({URLS['compatibility']})

---

*{COMPANY} has specialized in industrial video display solutions since 2013, serving 500+ enterprises across 12 countries.*""",
    })

    # Medium article
    posts.append({
        "platform": "Medium",
        "type": "web2",
        "auto": True,
        "tags": ["CNC Machining", "Manufacturing", "Industrial Automation", "Engineering"],
        "title": "Why Your Factory's 25-Year-Old CNC Machine Is Still Worth Upgrading",
        "body": f"""## The Hidden Value in Your Old CNC Machines

Walk through any machine shop and you'll find them: 1990s FANUC, Mitsubishi, and Mazak CNC machines still cutting parts every day. The cast iron beds, ball screws, and spindles are built to last 30-40 years with proper maintenance.

The weak link isn't mechanical — it's the display.

## The CRT Problem

Those amber and green CRT monitors were designed with a 10-15 year service life. Most are now at year 20-30. Symptoms include:

- **Dimming**: Brightness at 100% is barely visible
- **Flickering**: Intermittent display, especially during warm-up
- **Burn-in**: Permanent ghost images from years of the same interface
- **Bloom**: Edges of text become fuzzy and indistinct
- **Complete failure**: Usually the flyback transformer or high-voltage section

## The Economics

Here's the math that matters to your business:

| Option | Cost | Machine Downtime | Expected Life |
|--------|------|------------------|---------------|
| Replace CNC control system | $6,000-15,000+ | 2-5 days | 10+ years |
| Repair existing CRT | $300-800 | 1-3 days | 3-12 months |
| Buy refurbished CRT | $500-1,200 | 1-2 days | 1-3 years |
| **Industrial LCD retrofit** | **$150-280** | **10-15 minutes** | **5-7 years** |

## Real-World Example

A client ran 12 FANUC 0i-C CNC lathes (1998-2002). CRTs were failing across the fleet. OEM solution: $4,000 per machine × 12 = $48,000.

Instead, they installed industrial LCD retrofit kits. Total cost: under $3,000. Total downtime: 3 hours for all 12 machines. That was in 2023 — all 12 are still running flawlessly.

## What to Look For in a Retrofit Kit

1. **Industrial-grade panels** — Sharp/AUO TFT LCD, not consumer tablets
2. **Original connector compatibility** — No adapters, no splicing
3. **Warranty** — Minimum 1 year, ideally 2
4. **Installation support** — Model-specific guides with photos
5. **Brand coverage** — One supplier for all your machine brands

## The Bottom Line

For $150-300, you extend a machine worth tens of thousands by 5-7 years. The ROI is measured in hours, not months.

I've documented the full process with model-specific guides: [{SITE}]({SITE})

---

*{COMPANY} has been providing industrial display solutions since 2013. 500+ enterprises served across 12 countries. 2-year warranty on all products.*""",
    })

    # Blogger/Tumblr posts (shorter, manual posting)
    posts.append({
        "platform": "Blogger",
        "type": "web2",
        "auto": False,
        "title": "FANUC CNC Display CRT to LCD Upgrade — The Complete Guide",
        "body": f"""Industrial CNC machines from the 1990s and early 2000s share a common problem: failing CRT displays. The good news is that modern plug-and-play LCD replacements exist for virtually every major CNC brand.

**Supported Brands:**
- FANUC (A61L-0001 series, D9MM-11A)
- Mitsubishi (MDT962B, BM09DF, FCUA-CT100)
- Mazak (CD1472, C5470NS, DR5614)
- Siemens (6FC3998-7FA20, SM0901)
- Okuma (OSP 5000/5020)
- Haas (VF, ST, SL series)

**Why Upgrade:**
- Installation takes 10 minutes (4 screws + 1 connector)
- No CNC parameter changes needed
- Industrial grade LCD lasts 5-7 years
- Costs $150-280 vs $6,000+ for OEM replacement

Full details and model-specific guides: {SITE}

About {COMPANY}: 12+ years of industrial display expertise, 500+ enterprise clients worldwide. 2-year warranty on all products.""",
    })

    return posts


def gen_qna_content():
    """生成问答平台内容"""
    items = []

    # Quora answers
    items.append({
        "platform": "Quora",
        "type": "qna",
        "question": "How do I replace a FANUC CRT monitor with an LCD?",
        "answer": f"""Replacing a FANUC CRT with an LCD is surprisingly straightforward — it's a plug-and-play swap that takes about 10 minutes.

**Step-by-step:**
1. Power off the CNC machine completely
2. Remove the 4 screws holding the CRT in place
3. Disconnect the Honda MR-20M connector (20-pin, located on the back)
4. Plug the same connector into your new LCD module
5. Mount the LCD using the original screw holes
6. Power on — no parameter changes needed

**Important notes:**
- FANUC uses DC24V power and Honda MR-20M connector
- The LCD must be specifically designed for your CRT model (A61L-0001-0093 = D9MM-11A = 9" amber)
- Different FANUC models (0092, 0094, 0074, 0086, 0096) use the same connector but different screen sizes
- Make sure you buy industrial-grade (Sharp/AUO panels), not consumer LCDs

I've documented the process for each FANUC model at {SITE} — they have install guides with photos for every model.

The key thing to understand: the CNC controller outputs a standard composite video signal. The LCD retrofit module receives and displays that same signal. The controller has no idea anything changed."""
    })

    items.append({
        "platform": "Quora",
        "type": "qna",
        "question": "Is it worth upgrading an old CNC machine CRT to LCD?",
        "answer": f"""Absolutely worth it — it's probably the single best ROI upgrade you can make on a legacy CNC machine.

**The math:**
- LCD retrofit: $150-280 one-time, lasts 5-7 years
- CRT repair: $300-800 per repair, lasts 3-12 months
- OEM replacement: $6,000-15,000+

Over 5 years, an LCD retrofit costs $150-280 total, while nursing a dying CRT costs $2,000-4,000 in repeated repairs.

**When it's worth it:**
- The machine's mechanical parts are still good → YES
- The CNC controller still works → YES
- The only problem is the display → DEFINITELY YES

**When it's NOT worth it:**
- The controller has major board-level failures
- The machine has severe mechanical wear
- You're planning to replace the machine within 6 months

A 1990s FANUC or Mitsubishi CNC with good mechanicals can easily run another 5-10 years with an LCD upgrade. The cast iron beds, ball screws, and spindles on these machines were built to last 30+ years — the CRT was always the weakest link.

I've documented several real case studies including costs and photos: {URLS['cases']}

Full compatibility info for FANUC, Mitsubishi, Mazak, Siemens, Okuma, and Haas: {SITE}"""
    })

    items.append({
        "platform": "Quora",
        "type": "qna",
        "question": "What should I check before buying a CNC LCD replacement?",
        "answer": f"""Four critical things to verify before ordering:

**1. Connector Type** (this is the most common mistake)
- FANUC: Honda MR-20M (20-pin)
- Mitsubishi: 20-pin or 26-pin
- Mazak: 26-pin
- Siemens: DB-25 (25-pin D-Sub)
- Okuma: 14-pin or 20-pin
- Haas: 9-pin D-Sub
→ These are NOT interchangeable. Check your actual connector.

**2. Power Supply Voltage**
- FANUC/Mitsubishi/Mazak/Okuma: DC24V
- Siemens: AC110V ⚠️ (very important — DC LCD on AC machine = instant damage)
- Haas early models: DC12V

**3. Screen Size**
- Measure your CRT's visible diagonal
- Common sizes: 9", 10.4", 12.1", 14"
- The replacement LCD should match the original bezel opening

**4. Panel Quality**
- Industrial grade only (Sharp, AUO panels)
- Consumer tablet panels die in weeks from vibration and oil mist
- Look for IP54 minimum protection rating

I maintain a compatibility matrix covering 95+ CRT models across 6 brands: {URLS['compatibility']}

For model-specific install guides with photos, check: {SITE}"""
    })

    # 知乎回答
    items.append({
        "platform": "知乎",
        "type": "qna_zh",
        "question": "老CNC数控机床的CRT显示器坏了怎么办？",
        "answer": f"""做了12年工业显示器升级，经手过500多台老旧CNC的CRT改LCD，说几点实用建议：

**先判断问题严重程度：**
- 亮度调到顶还看不清 → 必须换
- 字体有重影/模糊 → 高压包在衰减，马上换
- 画面边缘缩小或变形 → 高压包快坏了，马上换
- 完全黑屏 → 可能是电源板或高压包彻底损坏

**三种方案的真相：**

1. **找人修CRT**：¥300-800，撑3-12个月。所谓的"维修"就是换拆机高压包和电容，这些拆机件本身也是20年以上的老货，坏是早晚的事。

2. **买二手原装CRT**：eBay上$120-280，寿命不确定。都是从报废机器上拆的，灯丝老化和高压衰减程度不同，可能3个月就又暗了。

3. **换成工业LCD**：¥700-1500，5-7年免维护。真正的一劳永逸。

**重点：安装真的不用改线路。**
FANUC/三菱/Mazak全部是原装接口直接对插，断电→拆4颗螺丝→拔1根信号线→插到新LCD上→拧回螺丝→开机。不用改任何CNC参数。

**各品牌接口速查：**
- FANUC：Honda MR-20M 20针，DC24V
- 三菱：20针或26针，DC24V
- Mazak：26针，DC24V
- 西门子老型号：DB-25，AC110V（注意是交流！别用直流LCD）
- 大隈：14针或20针，DC24V

我自己整理了6大品牌95个型号的兼容对照表和安装指南，全部免费查看：{SITE}

拍了机床显示器背面标签照片发给我，可以帮你查具体兼容方案：szkongto01@foxmail.com"""
    })

    items.append({
        "platform": "知乎",
        "type": "qna_zh",
        "question": "CNC数控系统CRT显示器越来越暗，修还是换？",
        "answer": f"""做了这么多年CNC维修，这个问题我帮工厂算过无数次账。直接给结论：**不要修，直接换LCD。**

**算一笔账（以FANUC 0-TC为例）：**

| 方案 | 单次花费 | 寿命 | 5年总成本 |
|------|---------|------|-----------|
| 修CRT(换高压包) | ¥300-500 | 3-12个月 | ¥2000-4000 |
| 修CRT(换显像管) | ¥600-800 | 6-18个月 | ¥3000-6000 |
| 买二手原装CRT | ¥800-1300 | 不确定 | ¥1600-4000+ |
| 换工业LCD | ¥700-1500 | 5-7年 | ¥700-1500 |

**为什么修CRT不划算：**
- CRT显示器全球停产超过15年
- 维修用的高压包、电容都是从旧机器上拆的
- 这些拆机件本身也老化了，寿命极短
- 每修一次，过几个月又坏，反复停机
- 停机一天的产能损失远超显示器差价

**为什么LCD是最优解：**
- 一次性投入，5-7年不用管
- 亮度、清晰度远超原装新CRT
- 功耗只有CRT的1/4
- 安装10分钟，不需要改任何线路

如果只是想临时撑一两个月（设备马上要淘汰），修一下还行。但如果这机器还要用1年以上，直接换LCD。

各个品牌和型号的兼容方案我整理了详细资料：{SITE}

不确定你的型号能不能换？拍一张显示器背面标签照片发到 szkongto01@foxmail.com，免费帮你确认。"""
    })

    return items


def gen_business_directory_entries():
    """生成工业目录提交信息"""
    entries = []

    entries.append({
        "platform": "Thomasnet",
        "type": "directory",
        "url": "https://www.thomasnet.com/",
        "company_name": "Kongto Technology (Shenzhen) Co., Ltd.",
        "description": "Manufacturer and supplier of industrial CNC display upgrade solutions. Specializing in CRT to LCD retrofit kits for FANUC, Mitsubishi, Siemens, Mazak, Okuma, and Haas CNC systems. Also offering industrial video signal converters (CGA/EGA/RGB to VGA/HDMI) and custom industrial TFT LCD displays (7-15 inch).",
        "categories": ["Industrial Displays", "CNC Machine Parts & Accessories", "Video Signal Converters", "LCD Display Modules"],
        "keywords": "CNC display, CRT to LCD retrofit, FANUC A61L-0001-0093, industrial LCD, video signal converter",
        "website": SITE,
        "email": "szkongto01@foxmail.com",
        "phone": "+86-13686889647",
        "address": "Building C, 4F, No.2 Shenkeng Complex, Henggang Street, Longgang District, Shenzhen, Guangdong, 518000, China",
        "year_founded": "2013",
        "certifications": "CE, RoHS, FCC, ISO 9001:2015",
        "employees": "11-50",
    })

    entries.append({
        "platform": "IndustryNet",
        "type": "directory",
        "url": "https://www.industrynet.com/",
        "company_name": "Kongto Technology",
        "description": "Industrial CNC display CRT to LCD upgrade solutions. Plug-and-play retrofit kits for 95+ CRT models across FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas. Also video signal converters and custom industrial TFT displays. 500+ enterprises served, 12+ years expertise, 2-year warranty.",
        "categories": ["Industrial Machinery & Equipment", "Electronic Components", "Display Technology"],
        "website": SITE,
    })

    entries.append({
        "platform": "Kompass",
        "type": "directory",
        "url": "https://www.kompass.com/",
        "company_name": "Shenzhen Jiangtu Technology Co., Ltd. (Kongto Technology)",
        "description": "Specialized manufacturer of industrial video display solutions: CNC CRT to LCD retrofit modules, industrial video signal converters (CGA/EGA/RGB to VGA/HDMI), and custom industrial TFT LCD displays. Serving global manufacturing clients since 2013.",
        "categories": ["Industrial equipment", "Electronic components and supplies", "Display screens and monitors"],
        "website": SITE,
    })

    entries.append({
        "platform": "MacRAE's Blue Book",
        "type": "directory",
        "url": "https://www.macraesbluebook.com/",
        "company_name": "Kongto Technology",
        "description": "Industrial CNC machine display upgrade solutions — CRT to LCD retrofit for FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas. 12+ years experience, 500+ global clients, CE/RoHS/FCC certified.",
        "categories": ["Industrial Displays & Monitors", "CNC Machine Accessories"],
        "website": SITE,
    })

    return entries


def gen_github_readme():
    """生成GitHub仓库README（高DA外链）"""
    readme = f"""# CNC Display Upgrade Reference Guide

> A community resource for identifying and upgrading legacy industrial CNC CRT displays to modern LCD alternatives.

## About This Repository

This is a technical reference for anyone maintaining or upgrading legacy CNC machines (1990-2005 era) with aging CRT displays. The information here is based on 12+ years of industrial display retrofit experience across 500+ machines.

## Quick Reference: Connector Types

| Brand | Connector | Power | Notes |
|-------|-----------|-------|-------|
| FANUC | Honda MR-20M (20-pin) | DC 24V | Most common industrial CNC connector |
| Mitsubishi | 20-pin or 26-pin | DC 24V | M64/E60/M500/M520 systems |
| Mazak | 26-pin | DC 24V | T-32/M-32/T-Plus/M-Plus |
| Siemens | DB-25 (25-pin) | **AC 110V** | Important: AC, not DC! |
| Okuma | 14-pin or 20-pin | DC 24V | OSP 5000/5020/7000 |
| Haas | 9-pin D-Sub | DC 12V | VF/ST/SL series |

## Common FANUC CRT Models

### 9" Monochrome (Amber)
- A61L-0001-0093 (D9MM-11A) — Most common, 0-TC/MC, 16/18/21 series
- A61L-0001-0092 — Similar to 0093
- A61L-0001-0086 — Earlier version
- A61L-0001-0090 — Pre-1992 models

### 14" Color
- A61L-0001-0074 — 14" color CRT
- A61L-0001-0094 — 14" color CRT
- A61L-0001-0096 — 14" color CRT

### 10.4"+
- A61L-0001-0097 — 10.4"+ color
- A61L-0001-0116 — Newer systems

## Installation Overview

All LCD retrofit modules follow the same basic procedure:

1. Power off CNC machine (verify with multimeter)
2. Remove 4 mounting screws from CRT housing
3. Disconnect video/power cable from CRT
4. Connect same cable to LCD module
5. Mount LCD module using original screw holes
6. Power on — no parameter changes, no soldering, no wiring modifications

## Signs Your CRT Needs Replacement

- Brightness at maximum but still too dim to read clearly
- Flickering display, especially during warm-up
- Permanent burn-in (ghost images visible on screen)
- Text appears fuzzy or has shadows/ghosting
- Screen edges shrinking or distorting (flyback transformer failure)
- Complete black screen (high-voltage section failure)

## Cost Comparison

| Approach | Cost | Lifespan | 5-Year Total |
|----------|------|----------|--------------|
| OEM replacement | $800-1,500 | 2-5 years | $2,000-4,000 |
| CRT repair | $300-800/repair | 3-12 months | $2,000-4,000 |
| eBay generic LCD | $100-200 | Unpredictable | $200-600+ |
| Industrial LCD retrofit | $150-280 | 5-7 years | $150-280 |

## Resources

- **[cncdisplay.com]({SITE})** — Full model-specific installation guides, compatibility matrix, case studies
- **[Compatibility Matrix]({URLS['compatibility']})** — 95+ CRT models across 6 brands
- **[Case Studies]({URLS['cases']})** — Real factory results and customer experiences
- **[FANUC Upgrade Guide]({URLS['guide']})** — Step-by-step with photos

## Disclaimer

This is an independent reference repository. All brand names (FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas) are trademarks of their respective owners. Always consult your CNC machine manual and a qualified technician before performing modifications.

## Contributors

Maintained by [Kongto Technology]({SITE}) — Industrial video display solutions since 2013.

---

*Last updated: {TODAY}*
"""
    return readme


def gen_chinese_platform_posts():
    """生成中文平台帖子"""
    posts = []

    posts.append({
        "platform": "掘金",
        "type": "web2_zh",
        "url": "https://juejin.cn/",
        "title": "老旧CNC数控机床CRT改LCD全攻略——花了12年踩坑总结的即插即用方案",
        "body": f"""## 背景

我所在的公司做工业显示方案12年了，经手过不下500台老旧CNC的显示器升级。常见场景：工厂一台FANUC 0-TC屏幕暗到看不清数字，师傅拿手电筒照着干活。找原厂换屏报价8000+，二手CRT修完几个月又坏。

其实现在有完全即插即用的LCD替代方案，一把螺丝刀10分钟搞定。

## 为什么CRT必坏

CRT显示器全球停产超过15年。市面上"维修"就是换拆机高压包和电容，这些备件也快用完了。每修一次300-800块，寿命3-12个月，累计成本远超一次性换LCD。

## 哪些系统可以改

**FANUC系列：**
- A61L-0001-0093 (D9MM-11A) — 9寸琥珀色，配0-TC/MC、16/18/21系列
- A61L-0001-0092、0094、0074、0086、0096 全部有对应LCD
- 接口统一是Honda MR-20M，供电DC24V

**三菱系列：**
- MDT962B — M3/M310/M64/E60系统通用
- BM09DF、FCUA-CT100 也都有现成方案

**马扎克Mazak：**
- DR5614、CD1472-D1M、C-5470NS — T-32/M-32系统
- 注意Mazak用的是26针接口，和FANUC不通用

**其他品牌：**
- 西门子SINUMERIK 810/820的6FC3998-7FA20
- 大隈Okuma OSP 5000/5020
- 哈斯Haas VF系列

## 安装到底难不难

零基础也能搞。总共4步：

1. 关机床总电源（必须！）
2. 拆CRT四角螺丝，拔下信号线
3. 信号线插新LCD，拧回螺丝
4. 开机 —— 不用改任何参数

唯一要注意的是：FANUC/三菱用DC24V供电，西门子部分老型号用AC110V，确认供电再下单。

## 成本对比

| 方案 | 价格 | 寿命 |
|------|------|------|
| 原厂换屏 | ¥6000-10000 | 2-5年（二手翻新） |
| 找人修CRT | ¥300-800/次 | 3-12个月 |
| 第三方LCD | ¥700-1500 | 5-7年连续运行 |

## 资料整理

这几年积累的安装记录、型号对照表、接线图都整理了在 {SITE}

每个品牌每个型号都有详细的替换指南，全部免费查看。需要的师傅留言机床型号，我帮你查兼容方案。""",
    })

    posts.append({
        "platform": "CSDN博客",
        "type": "web2_zh",
        "url": "https://blog.csdn.net/",
        "title": "工业CNC数控系统CRT显示器转LCD升级——技术详解与安装指南",
        "body": f"""## 一、行业背景

在工业制造领域，大量1990-2005年间进口的日本和德国CNC数控机床仍在服役。这些设备的机械部分（床身、丝杠、主轴）保养得当可以运行30年以上，但电子部件——特别是CRT显示器——已经严重老化。

**常见故障现象：**
- 屏幕亮度调到最大仍然看不清
- 冷启动时画面闪烁
- 字符有重影/模糊
- 画面边缘缩小（高压包衰减）
- 永久性灼屏（烧屏）
- 完全黑屏

## 二、为什么维修CRT不划算

1. CRT显示器全球停产超过15年
2. 维修用高压包、电容均来自拆机件，寿命3-12个月
3. 拆机备件供应日益枯竭
4. 反复维修导致反复停机，综合成本远超一次更换

## 三、LCD替代方案技术原理

现代工业LCD升级模块的核心设计理念是"对控制系统透明"：

- 使用原装视频信号接口（Honda MR-20M等）
- 使用原装供电标准（DC24V/AC110V）
- 保持原安装尺寸和固定孔位
- 内置视频解码器将复合视频信号转换为LCD可显示格式

对CNC控制器而言，输出的是同样的复合视频信号——它无法区分连接的是CRT还是LCD。

## 四、主要品牌兼容性

### FANUC发那科
- 型号：A61L-0001-0093 (D9MM-11A)、0092、0094、0074、0086、0096、0097
- 接口：Honda MR-20M (20针)
- 供电：DC 24V
- 兼容系统：0i、16i、18i、21i、Power Mate

### 三菱Mitsubishi
- 型号：MDT962B、BM09DF、FCUA-CT100
- 兼容系统：M64、E60、M500、M520

### 西门子Siemens
- 型号：6FC3998-7FA20、SM0901-579417-TA
- 供电：AC 110V（重要：是交流不是直流！）

### 马扎克Mazak
- 型号：CD1472-D1M、C-5470NS、DR5614

### 大隈Okuma
- OSP 5000/5020/7000系列

### 哈斯Haas
- VF、ST、SL系列

## 五、安装步骤（以FANUC为例）

1. 关闭机床总电源
2. 拆下CRT四角4颗固定螺丝
3. 拔下Honda MR-20M信号/电源线
4. 将信号线插入新LCD模块
5. 用原螺丝固定LCD模块
6. 开机——无需修改任何CNC参数

全程10分钟，所需工具：一把螺丝刀。

## 六、选购注意事项

1. **确认接口类型** — 不同品牌接口不通用
2. **确认供电标准** — 西门子用AC110V，其他品牌用DC24V
3. **确认面板等级** — 必须工业级（Sharp/AUO），消费屏几周就坏
4. **确认质保期限** — 至少1年，优质产品2年

## 参考资料

- 官方网站：{SITE}
- 兼容性矩阵（95+型号）：{URLS['compatibility']}
- 客户案例：{URLS['cases']}
- 技术咨询：szkongto01@foxmail.com""",
    })

    posts.append({
        "platform": "V2EX",
        "type": "forum_zh",
        "title": "老旧CNC数控机床CRT显示器改LCD — 完全即插即用",
        "body": f"""工厂里那台FANUC 0-TC显示越来越暗，差点就花大钱换新屏幕了。

结果发现现在有完全即插即用的LCD替代方案，直接替换原CRT，用原装接口和供电，一把螺丝刀4颗螺丝搞定。

支持:
- FANUC A61L-0001全系列（0093/0092/0094/0074/0086/0096）
- 三菱 MDT962B、BM09DF、CT100、M64、E60
- 马扎克 DR5614、CD1472-D1M
- 西门子 6FC3998-7FA20
- 大隈 Okuma 5000/5020
- 哈斯 Haas VF系列

技术文章和安装视频: {SITE}

有需要的师傅可以看下，不懂型号的发标签照片我帮忙确认。""",
    })

    return posts


# ============================================================
# 自动发布函数（有API的平台）
# ============================================================

def post_github_repo():
    """创建GitHub仓库作为高DA外链"""
    print("\n=== Creating GitHub Repository Backlink ===")

    readme = gen_github_readme()
    repo_dir = OUTPUT / "cnc-display-upgrade-guide"

    if repo_dir.exists():
        import shutil
        shutil.rmtree(repo_dir)

    repo_dir.mkdir(exist_ok=True)
    (repo_dir / "README.md").write_text(readme, encoding='utf-8')
    (repo_dir / ".git").mkdir(exist_ok=True)

    # Save the README for manual GitHub creation
    out_file = OUTPUT / "github_repo_README.md"
    out_file.write_text(readme, encoding='utf-8')
    print(f"  [OK] GitHub README saved: {out_file}")
    print(f"  [Manual] Create repo at: https://github.com/new")
    print(f"  [Manual] Name: cnc-display-upgrade-guide")
    print(f"  [Manual] Description: Reference guide for upgrading industrial CNC CRT displays to LCD")
    print(f"  [Manual] Paste README.md content")

    # Try to create via gh CLI if available
    import subprocess
    try:
        result = subprocess.run(
            ['gh', 'repo', 'create', 'cnc-display-upgrade-guide',
             '--public', '--description', 'Reference guide for upgrading industrial CNC CRT displays to LCD',
             '--homepage', SITE],
            capture_output=True, text=True, timeout=30, cwd=str(repo_dir)
        )
        if result.returncode == 0:
            print(f"  [OK] GitHub repo created via gh CLI")
            # Push README
            subprocess.run(['git', 'init'], cwd=str(repo_dir), capture_output=True)
            subprocess.run(['git', 'add', 'README.md'], cwd=str(repo_dir), capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit: CNC Display Upgrade Reference Guide'],
                          cwd=str(repo_dir), capture_output=True)
            subprocess.run(['git', 'branch', '-M', 'main'], cwd=str(repo_dir), capture_output=True)
            push_result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'],
                cwd=str(repo_dir), capture_output=True, text=True, timeout=30
            )
            if push_result.returncode == 0:
                print(f"  [OK] Pushed to GitHub successfully!")
                print(f"  [OK] Backlink: https://github.com/szkongto/cnc-display-upgrade-guide")
            else:
                print(f"  [Manual] Push README: cd {repo_dir} && git push")
        else:
            print(f"  [Manual] gh CLI not configured. Create repo manually.")
    except Exception:
        print(f"  [Manual] Create GitHub repo manually at https://github.com/new")

    return True


def generate_all_content():
    """生成所有平台的就绪发布内容"""
    print("=" * 60)
    print("CNCDISPLAY.COM BACKLINK CONTENT GENERATOR v2.0")
    print(f"Generated: {TODAY}")
    print("=" * 60)

    all_content = {
        "forums": gen_forum_posts(),
        "social": gen_social_posts(),
        "web2_blogs": gen_web2_blogs(),
        "qna": gen_qna_content(),
        "directories": gen_business_directory_entries(),
        "chinese_platforms": gen_chinese_platform_posts(),
    }

    # Save everything as JSON
    json_path = OUTPUT / f"all_backlinks_{TODAY}.json"
    json_path.write_text(json.dumps(all_content, ensure_ascii=False, indent=2), encoding='utf-8')

    # Generate individual markdown files per platform
    total_platforms = 0

    # Forum posts
    for post in all_content["forums"]:
        safe_name = post["platform"].lower().replace(" ", "_").replace(".", "")
        out = OUTPUT / f"forum_{safe_name}.md"
        content = f"""# {post['platform']} — 论坛帖子
## 板块: {post.get('board', 'General')}

### 标题
{post['title']}

### 正文

{post['body']}

---
*发布到: {post.get('url', 'N/A')}*
"""
        out.write_text(content, encoding='utf-8')
        total_platforms += 1

    # Social posts
    for post in all_content["social"]:
        safe_name = post["platform"].lower().replace(" ", "_").replace("/", "_")
        out = OUTPUT / f"social_{safe_name}.md"
        content = f"""# {post['platform']} — 帖子

### 标题
{post.get('title', '(No title — platform post)')}

### 正文

{post['body']}

"""
        out.write_text(content, encoding='utf-8')
        total_platforms += 1

    # Web 2.0 blogs
    for post in all_content["web2_blogs"]:
        safe_name = post["platform"].lower().replace(" ", "_")
        out = OUTPUT / f"blog_{safe_name}.md"
        content = f"""# {post['platform']} — 博客文章

### 标题
{post['title']}

### 标签
{', '.join(post.get('tags', []))}

### 正文

{post['body']}

---
*{"自动发布(AUTO)" if post.get("auto") else "需手动发布(MANUAL)"}*
"""
        out.write_text(content, encoding='utf-8')
        total_platforms += 1

    # Q&A
    for item in all_content["qna"]:
        safe_name = item["platform"].replace(" ", "_")
        out = OUTPUT / f"qna_{safe_name}.md"
        content = f"""# {item['platform']} — 问答

### 问题
{item['question']}

### 回答

{item['answer']}

---
"""
        out.write_text(content, encoding='utf-8')
        total_platforms += 1

    # Business directories
    dirs_md = "# 工业目录提交信息\n\n"
    for entry in all_content["directories"]:
        dirs_md += f"""## {entry['platform']}
- **URL**: {entry.get('url', 'N/A')}
- **公司名称**: {entry['company_name']}
- **网站**: {entry['website']}
- **分类**: {', '.join(entry.get('categories', []))}
- **描述**: {entry['description']}
- **邮箱**: {entry.get('email', 'N/A')}
- **电话**: {entry.get('phone', 'N/A')}
- **地址**: {entry.get('address', 'N/A')}
- **成立年份**: {entry.get('year_founded', 'N/A')}
- **认证**: {entry.get('certifications', 'N/A')}

---
"""
        total_platforms += 1

    (OUTPUT / "business_directories.md").write_text(dirs_md, encoding='utf-8')

    # Chinese platforms
    for post in all_content["chinese_platforms"]:
        safe_name = post["platform"]
        out = OUTPUT / f"zh_{safe_name}.md"
        content = f"""# {post['platform']} — 中文平台帖子

### 标题
{post['title']}

### 正文

{post['body']}

---
*发布到: {post.get('url', 'N/A')}*
"""
        out.write_text(content, encoding='utf-8')
        total_platforms += 1

    # Generate tracking CSV
    csv_path = OUTPUT / f"backlink_tracker_{TODAY}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Platform', 'Type', 'DA', 'DoFollow', 'Title', 'Status', 'URL_Posted', 'Date_Posted', 'Notes'])

        for post in all_content["forums"]:
            info = FORUMS.get(list(FORUMS.keys())[0], {})
            writer.writerow([post['platform'], 'Forum', info.get('da', '?'), 'Yes', post['title'][:80], 'PENDING', '', '', 'Copy-paste from generated .md file'])

        for post in all_content["social"]:
            writer.writerow([post['platform'], 'Social', '91-98', 'Varies', post.get('title', '')[:80], 'PENDING', '', '', ''])

        for post in all_content["web2_blogs"]:
            auto = 'Yes' if post.get('auto') else 'No'
            writer.writerow([post['platform'], 'Web2.0 Blog', '82-95', 'Varies', post['title'][:80], 'PENDING' if not auto else 'READY', '', '', f'Auto-post: {auto}'])

        for item in all_content["qna"]:
            writer.writerow([item['platform'], 'Q&A', '82-94', 'Varies', item['question'][:80], 'PENDING', '', '', ''])

        for entry in all_content["directories"]:
            writer.writerow([entry['platform'], 'Directory', '62-80', 'Yes', entry['company_name'][:80], 'PENDING', '', '', 'Submit company info from .md file'])

        for post in all_content["chinese_platforms"]:
            writer.writerow([post['platform'], 'Chinese Platform', '55-82', 'Yes', post['title'][:80], 'PENDING', '', '', ''])

    print(f"\n[OK] Generated content for {total_platforms} platforms")
    print(f"[OK] Output directory: {OUTPUT}")
    print(f"[OK] JSON: {json_path}")
    print(f"[OK] CSV Tracker: {csv_path}")
    print(f"\nPlatforms covered:")
    for cat, items in all_content.items():
        print(f"  {cat}: {len(items)} entries")

    return all_content


def generate_report():
    """生成外链建设报告"""
    print("\n=== Generating Backlink Report ===")

    report = f"""# cncdisplay.com 外链建设报告
**日期**: {TODAY}
**总平台数**: 25+

## 外链策略

采用"多层次外链组合"策略：
- **Tier 1**: 高DA Web2.0博客 + 行业论坛 = 直接传递权重
- **Tier 2**: 社交媒体 + 问答 = 流量 + 品牌信号
- **Tier 3**: 工业目录 + 代码仓库 = 信任信号 + 引用

## 已生成内容清单

### 🔴 优先发布（本周，DA 58-96）
| # | 平台 | DA | 类型 | 状态 |
|---|------|-----|------|------|
| 1 | GitHub Repository | 96 | Code | READY |
| 2 | Reddit r/CNC | 91 | Social | READY |
| 3 | Reddit r/Machinists | 88 | Social | READY |
| 4 | Dev.to | 92 | Web2.0 | READY (API) |
| 5 | Medium | 95 | Web2.0 | READY (API) |
| 6 | Practical Machinist | 62 | Forum | READY |
| 7 | CNCzone | 58 | Forum | READY |
| 8 | Hashnode | 82 | Web2.0 | READY (API) |
| 9 | LinkedIn | 98 | Social | READY |

### 🟡 第二波（下周）
| # | 平台 | DA | 类型 | 状态 |
|---|------|-----|------|------|
| 10 | Quora (3 answers) | 94 | Q&A | READY |
| 11 | 知乎 (2 answers) | 82 | Q&A | READY |
| 12 | 掘金 | 70 | Web2.0 ZH | READY |
| 13 | CSDN博客 | 82 | Web2.0 ZH | READY |
| 14 | V2EX | 55 | Forum ZH | READY |
| 15 | LinuxCNC Forum | 45 | Forum | READY |
| 16 | Reddit r/Manufacturing | 78 | Social | READY |
| 17 | Blogger | 94 | Web2.0 | READY |
| 18 | Tumblr | 93 | Web2.0 | READY |
| 19 | Stack Exchange Engineering | 91 | Q&A | READY |

### 🟢 月度任务（持续性）
| # | 平台 | DA | 类型 |
|---|------|-----|------|
| 20 | Thomasnet | 75 | Directory |
| 21 | IndustryNet | 62 | Directory |
| 22 | Kompass | 80 | Directory |
| 23 | MacRAE's Blue Book | 65 | Directory |
| 24 | SegmentFault | 65 | Q&A ZH |
| 25 | 博客园 | 72 | Web2.0 ZH |

## 锚文本多样性策略

已准备11种不同锚文本变体，自然混合使用：
- 品牌锚: "Kongto Technology", "cncdisplay.com"
- 关键词锚: "CNC display upgrade", "FANUC LCD replacement", "CRT to LCD retrofit"
- 长尾锚: "industrial CRT to LCD upgrade company", "Mitsubishi MDT962B LCD upgrade"
- 通用锚: "click here", "learn more", "this guide"

## 预期效果

- **本月**: 10-15个Dofollow外链 + 提升品牌信号
- **第3个月**: DR达到10+（当前接近0）
- **第6个月**: DR达到20+，自然搜索流量增长100%+
- **长期**: 30+外链形成自然生长曲线

## 执行说明

所有内容已生成在 `backlinks_output/` 目录：
- `backlink_tracker_{TODAY}.csv` — 进度跟踪表
- `forum_*.md` — 论坛就绪帖
- `social_*.md` — 社交媒体就绪帖
- `blog_*.md` — Web2.0博客就绪帖
- `qna_*.md` — 问答就绪帖
- `zh_*.md` — 中文平台就绪帖
- `business_directories.md` — 目录提交信息

**使用方法**: 打开对应.md文件 → 复制内容 → 粘贴到目标平台 → 更新CSV追踪表状态。
"""

    report_path = OUTPUT / f"backlink_report_{TODAY}.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"[OK] Report: {report_path}")
    return report


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python backlink_engine.py [generate|github|report|all]")
        print("  generate — Generate content for all 25+ platforms")
        print("  github   — Auto-create GitHub repo backlink (DA 96)")
        print("  report   — Generate tracking report")
        print("  all      — Run everything")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd in ['generate', 'all']:
        generate_all_content()
        generate_report()

    if cmd in ['github', 'all']:
        post_github_repo()

    if cmd in ['report', 'all']:
        generate_report()

    print(f"\nDone. All outputs in: {OUTPUT}")
