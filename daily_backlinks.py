#!/usr/bin/env python3
"""
每日外链自动化引擎 v5.0 — AI动态生成多平台分发
=============================================
全自动: Dev.to(DA92) + Telegra.ph(DA86) + Rentry.co(DA60) + GitLab(DA96)
AI生成: 基于网站品牌数据实时生成，永不重复
手动: LinkedIn(DA98) + Reddit(DA91) + 中文平台

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

DEVTO_USED = OUTPUT / "devto_canonicals.json"

def load_devto_used():
    if DEVTO_USED.exists():
        return set(json.loads(DEVTO_USED.read_text(encoding='utf-8')))
    return set()

def save_devto_used(canonical):
    used = load_devto_used()
    used.add(canonical)
    DEVTO_USED.write_text(json.dumps(sorted(used), indent=2), encoding='utf-8')

# ============================================================
# 品牌数据库 — 来自网站实际内容
# ============================================================
BRAND_DATA = {
    "fanuc": {
        "name": "FANUC", "name_cn": "发那科",
        "models": ["A61L-0001-0093", "A61L-0001-0092", "A61L-0001-0074", "A61L-0001-0090", "A61L-0001-0095", "D9MM-11A"],
        "connector": "Honda MR-20M (20-pin)", "power": "DC 24V",
        "controls": ["0-TC", "0-MC", "18-T", "21-T", "Power Mate", "0i"],
        "price": "$199", "page": f"{SITE}/brands/FANUC.html"
    },
    "mitsubishi": {
        "name": "Mitsubishi", "name_cn": "三菱",
        "models": ["MDT962B", "BM09DF", "FCUA-CT100", "MDT1283B"],
        "connector": "20-pin or 26-pin", "power": "DC 24V",
        "controls": ["M64", "E60", "M500", "M520", "M3", "M310"],
        "price": "$199", "page": f"{SITE}/brands/Mitsubishi.html"
    },
    "siemens": {
        "name": "Siemens", "name_cn": "西门子",
        "models": ["6FC3988-7FA20", "6FC3998-7FA20", "SM0901"],
        "connector": "DB-25 (25-pin D-Sub)", "power": "AC 110V",
        "controls": ["SINUMERIK 810", "SINUMERIK 820", "SINUMERIK 840D"],
        "price": "$299", "page": f"{SITE}/brands/Siemens.html",
        "warning": "AC 110V — only brand using AC power"
    },
    "mazak": {
        "name": "Mazak", "name_cn": "马扎克",
        "models": ["CD1472-D1M", "C-5470NS", "DR5614", "MDT1283B"],
        "connector": "26-pin proprietary", "power": "DC 24V",
        "controls": ["Mazatrol T-32", "Mazatrol M-32", "M-Plus", "Fusion 640"],
        "price": "$249", "page": f"{SITE}/brands/MAZAK.html"
    },
    "okuma": {
        "name": "Okuma", "name_cn": "大隈",
        "models": ["OSP 5000", "OSP 5020", "OSP 7000"],
        "connector": "14-pin or 20-pin", "power": "DC 24V",
        "controls": ["OSP 5000", "OSP 5020", "OSP 7000"],
        "price": "$229", "page": f"{SITE}/brands/OKUMA.html"
    },
    "haas": {
        "name": "Haas", "name_cn": "哈斯",
        "models": ["9-pin D-Sub", "15-pin VGA"],
        "connector": "9-pin D-Sub", "power": "DC 12V",
        "controls": ["Haas Classic Control", "VF series", "ST series", "SL series"],
        "price": "$179", "page": f"{SITE}/brands/HAAS.html",
        "warning": "DC 12V — only brand using 12V"
    },
}

FAILURES = [
    {"name": "屏幕变暗", "en": "dim display", "desc": "CRT brightness fading, max brightness still unreadable"},
    {"name": "闪烁", "en": "flickering screen", "desc": "periodic flicker, cold start takes 20+ min to stabilize"},
    {"name": "黑屏无显示", "en": "no display / black screen", "desc": "complete black screen, no image at all"},
    {"name": "烧屏残影", "en": "image retention / burn-in", "desc": "permanent ghost image from static CNC UI displays"},
    {"name": "高压包异响", "en": "flyback transformer whine", "desc": "high-pitched noise from failing HV section"},
    {"name": "画面扭曲", "en": "distorted / shrinking image", "desc": "screen warps at edges, image shrinks over time"},
]

ANGLES = [
    {"en": "troubleshooting guide", "zh": "故障排查指南"},
    {"en": "cost comparison", "zh": "成本对比分析"},
    {"en": "installation tutorial", "zh": "安装教程"},
    {"en": "warning alert", "zh": "重要警告"},
    {"en": "brand comparison", "zh": "品牌对比"},
    {"en": "case study", "zh": "客户案例"},
    {"en": "technical specs", "zh": "技术规格"},
    {"en": "maintenance tips", "zh": "维护技巧"},
    {"en": "compatibility check", "zh": "兼容性确认"},
    {"en": "industry trend", "zh": "行业趋势"},
]

# ============================================================
# 文章生成器 — 从品牌数据动态组合，无需AI
# ============================================================

CACHED_ARTICLE = None

def get_daily_article():
    """Generate or return cached article for today."""
    global CACHED_ARTICLE
    cache_file = OUTPUT / f"article_{TODAY}.json"
    if cache_file.exists():
        CACHED_ARTICLE = json.loads(cache_file.read_text(encoding='utf-8'))
        print(f"  [CACHE] Loaded article_{TODAY}.json")
        return CACHED_ARTICLE
    if CACHED_ARTICLE:
        return CACHED_ARTICLE
    article = _build_article()
    cache_file.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding='utf-8')
    CACHED_ARTICLE = article
    return article

def _build_article():
    """Build a unique article from brand×model×failure×angle combination."""
    brand_keys = list(BRAND_DATA.keys())
    brand_key = brand_keys[DAY_NUM % len(brand_keys)]
    brand = BRAND_DATA[brand_key]
    failure = FAILURES[DAY_NUM % len(FAILURES)]
    angle = ANGLES[(DAY_NUM // 7) % len(ANGLES)]
    model = brand["models"][DAY_NUM % len(brand["models"])]

    canonical = brand["page"]
    devto_tags = list(dict.fromkeys(["cnc", "manufacturing", "engineering", brand_key.lower()]))[:4]

    print(f"\n  [BUILD] {brand['name']} / {model} / {failure['en']} / {angle['en']}")

    title, body = _compose_article_body(brand, model, failure, angle)

    return {
        "title": title[:120],
        "devto_tags": devto_tags,
        "canonical": canonical,
        "body_devto": body,
        "brand": brand,
        "model": model,
        "failure": failure,
        "angle": angle,
    }

def _compose_article_body(brand, model, failure, angle):
    """Compose a structured article from data blocks. Each day varies structure."""
    angle_i = DAY_NUM   # variation seed
    brand_key = [k for k, v in BRAND_DATA.items() if v["name"] == brand["name"]][0]

    # Build component blocks — shuffled/selected based on day number
    intro_block = _intro(brand, model, failure, angle_i)
    detail_block = _details(brand, model, failure, angle_i)
    compare_block = _comparison(brand, angle_i)
    install_block = _installation(brand, angle_i)
    warning_block = _warnings(brand, angle_i)
    closing_block = _closing(brand, angle_i)

    # Assemble in different order based on angle
    structure_map = {
        "troubleshooting guide": [intro_block, detail_block, compare_block, install_block, closing_block],
        "cost comparison": [intro_block, compare_block, detail_block, warning_block, closing_block],
        "installation tutorial": [install_block, detail_block, compare_block, closing_block],
        "warning alert": [warning_block, intro_block, detail_block, closing_block],
        "brand comparison": [intro_block, compare_block, detail_block, install_block, warning_block, closing_block],
        "case study": [intro_block, detail_block, compare_block, closing_block],
        "technical specs": [detail_block, compare_block, install_block, closing_block],
        "maintenance tips": [intro_block, warning_block, detail_block, install_block, closing_block],
        "compatibility check": [detail_block, compare_block, warning_block, closing_block],
        "industry trend": [intro_block, compare_block, detail_block, warning_block, closing_block],
    }
    blocks = structure_map.get(angle["en"], [intro_block, detail_block, compare_block, closing_block])

    body = "\n\n".join(blocks)
    title = f"{brand['name']} {model} CRT {failure['en']}: {angle['en']}" if angle_i % 2 == 0 else f"How to Fix {brand['name']} {model} {failure['en']} — Complete Guide"

    return title, body

def _intro(brand, model, failure, seed):
    """Opening paragraph — varies by seed."""
    openers = [
        f"If you operate a {brand['name']} CNC machine with a {model} CRT display, you may have noticed it developing {failure['en']}. This isn't surprising — these CRTs were designed for 10-15 years of service, and most are now past 20.",
        f"A {brand['name']} {model} CRT showing {failure['en']} is one of the most common service calls in CNC maintenance. Here's what's actually happening inside that display and what to do about it.",
        f"CNC maintenance note: {brand['name']} {model} CRTs from the 1990s are now reaching end-of-life. {failure['en']} is a classic symptom. Here's the practical approach.",
        f"Seeing {failure['en']} on your {brand['name']} {model} CRT? You're not alone. This is the #1 reason shops call us about {brand['name']} displays.",
        f"That {brand['name']} {model} CRT has served well for decades. But when {failure['en']} starts, it's time to plan the upgrade before production stops.",
    ]
    return f"## {openers[seed % len(openers)]}"

def _details(brand, model, failure, seed):
    """Technical detail section — model-specific facts."""
    pairings = [
        f"The {model} CRT in {brand['name']} systems connects via {brand['connector']} and runs on {brand['power']}. It's compatible with {', '.join(brand['controls'][:3])} controls. The LCD replacement uses the same connector and power — no adapter needed. Price: {brand['price']}.",
        f"Key specs for {brand['name']} {model}: connector = {brand['connector']}, power = {brand['power']}, compatible with {', '.join(brand['controls'][:3])}. The LCD module matches all these specs exactly, making it a direct swap.",
        f"When replacing a {brand['name']} {model} CRT, check three things: (1) connector type — {brand['connector']}, (2) power supply — {brand['power']}, (3) control system — {', '.join(brand['controls'][:3])}. All three are covered by the standard LCD upgrade. Price: {brand['price']}.",
    ]
    detail = pairings[seed % len(pairings)]

    symptom_detail = {
        "dim display": "Brightness was measured at <100 cd/m² on an aged CRT vs. 350-450 cd/m² on the replacement LCD. Even at maximum brightness, the old CRT can't compete with shop floor lighting.",
        "flickering screen": "The flickering is caused by aging electrolytic capacitors that can no longer hold stable voltage. As the machine warms up, they partially recover — but each cold start gets worse.",
        "no display / black screen": "A blank CRT often means the flyback transformer (high-voltage section) has failed completely. This component steps up power to 20-30kV — when it goes, there's no image at all.",
        "image retention / burn-in": "Phosphor burn-in is permanent. That ghosted CNC parameter screen is etched into the tube. LCD modules use TFT technology — no phosphor layer, no burn-in, ever.",
        "flyback transformer whine": "The high-pitched whine (15-20 kHz) signals a failing flyback transformer. This component generates the 20-30kV needed for the CRT — when it fails, you get a blank screen.",
        "distorted / shrinking image": "Image distortion traces to the deflection circuit losing linearity. The horizontal and vertical scan can't maintain proper geometry as components age.",
    }
    symptom = symptom_detail.get(failure["en"], f"The {failure['en']} issue indicates the CRT is approaching end-of-life. An LCD replacement eliminates this permanently.")

    return f"## Technical Details\n\n{detail}\n\n{symptom}"

def _comparison(brand, seed):
    """Cost or spec comparison table."""
    price = brand['price'].replace('$', '')
    cautions = []
    if brand['name'] == 'Siemens':
        cautions.append(f"⚠️ {brand['name']} uses AC 110V — do NOT use a DC-only LCD module or it will be destroyed on power-up.")
    if brand['name'] == 'Haas':
        cautions.append(f"⚠️ {brand['name']} uses DC 12V — standard DC 24V modules won't work at correct brightness.")

    warn = "\n".join(cautions)
    warn_section = f"\n\n{warn}" if warn else ""

    return f"""## Cost Comparison: Repair vs Replace

| Option | Cost | Lifespan |
|--------|------|----------|
| CRT repair (rebuilt HV section) | ${price}–{int(price)*2} each | 3-12 months |
| CRT repair (donor tube swap) | ${int(price)+100}–{int(price)+300} | 6-18 months |
| Used CRT on eBay | ${int(price)*2}–{int(price)*3} | Unknown (already aged) |
| LCD replacement module | {brand['price']} (one-time) | 5-7 years continuous |

{seed % 3 == 0 and f"Over 5 years: CRT repairs cost {5 * int(price)}–{5 * int(price) * 2}, while a single LCD costs {brand['price']}. The math is clear." or seed % 3 == 1 and f"Avoid the CRT repair treadmill. A {brand['price']} LCD breaks even on the second repair visit." or f"Most shops break even on LCD cost within 12 months by eliminating just one CRT failure."}{warn_section}"""

def _installation(brand, seed):
    """Installation steps — varies by brand."""
    return f"""## Installation

1. Power off CNC machine and verify power is off with multimeter
2. Remove 4 mounting bolts from the CRT bezel
3. Disconnect the {brand['connector'].split('(')[0].strip() or brand['connector']} cable
4. Connect same cable to the replacement LCD module
5. Mount LCD using original screw holes (same pattern)
6. Power on — no CNC parameter changes required

Total time: ~15 minutes. The LCD draws {brand['power']}, matching the original CRT power supply.

Full guide: {brand['page']}"""

def _warnings(brand, seed):
    """Brand-specific warnings."""
    specific_warnings = {
        "FANUC": "FANUC uses the Honda MR-20M (20-pin) connector. Some aftermarket 'universal' LCDs use different connectors and require adapter boards. The direct replacement uses the same 20-pin plug.",
        "Mitsubishi": "Count your pins before ordering. Mitsubishi used both 20-pin (MDT962B) and 26-pin (FCUA-CT100) connectors. They are NOT interchangeable, even within the same machine series.",
        "Siemens": "CRITICAL: Siemens SINUMERIK displays run on AC 110V. Connecting a standard DC 24V LCD module will destroy it instantly. Verify your replacement explicitly supports AC input.",
        "Mazak": "Some suppliers list 'FANUC/Mazak compatible' displays. These are physically incompatible — Mazak uses a 26-pin connector, FANUC uses 20-pin Honda MR-20M.",
        "Okuma": "OSP 5000/5020 use a 14-pin connector. OSP 7000 uses 20-pin. They are NOT cross-compatible. Check the label on the back of your CRT housing before ordering.",
        "Haas": "Early Haas VF/ST/SL machines use DC 12V power — not the DC 24V used by most other CNC brands. A standard 24V module won't work at full brightness.",
    }
    warn = specific_warnings.get(brand["name"], "Verify your specific CRT model number before ordering. Take a photo of the label on the back of the CRT housing.")
    return f"## Important Note\n\n{warn}"

def _closing(brand, seed):
    """Closing — call to action linking to site."""
    closers = [
        f"An LCD module eliminates the {brand['name']} CRT failure cycle permanently. Full {brand['name']} upgrade guide and compatibility info: {brand['page']}",
        f"Stop repairing that 20+ year old {brand['name']} CRT. A {brand['price']} LCD module solves it permanently. Guide: {brand['page']}",
        f"Every {brand['name']} {brand['models'][0]} CRT will eventually fail. Plan the upgrade now instead of scrambling during a production emergency. Details: {brand['page']}",
        f"{brand['name']} LCD replacement: same connector ({brand['connector'].split('(')[0].strip() or brand['connector']}), same power ({brand['power']}), plug-and-play installation. Full guide: {brand['page']}",
    ]
    return f"## Summary\n\n{closers[seed % len(closers)]}"


def generate_manual_content(article):
    """Generate Reddit, LinkedIn, Chinese variants from today's article data."""
    brand = article["brand"]
    model = article["model"]
    failure = article["failure"]

    reddit_questions = [
        f"My {brand['name']} {model} CRT getting dim — repair or replace?",
        f"{brand['name']} CNC {model} monitor failing — anyone switched to LCD?",
        f"CRT repair shop quote for {brand['name']} {model} — fair price?",
        f"How hard is {brand['name']} {model} CRT to LCD swap?",
        f"{brand['name']} {model} display going bad — options?",
    ]
    q = reddit_questions[DAY_NUM % len(reddit_questions)]
    body = f"My {brand['name']} {model} CRT is showing {failure['en']}. Machine is mechanically solid — this screen is the only issue. Went LCD yet?"

    li_post = f"CNC maintenance reality: That {brand['name']} {model} CRT in your machine ran 20+ years — far past its design life.\n\n{brand['name']} LCD replacements use the original {brand['connector']}. Plug-and-play, ~15 min install, {brand['price']}.\n\nOne module eliminates the CRT failure cycle permanently.\n\nGuides at cncdisplay.com\n\n#Manufacturing #CNC #IndustrialAutomation"

    power_cn = brand['power'].replace('AC 110V', 'AC 110V（交流）').replace('DC 24V', 'DC 24V（直流）').replace('DC 12V', 'DC 12V（直流）')
    zh_title = f"{brand['name_cn']}CNC显示器{failure['name']}？直接改LCD"
    zh_body = f"{brand['name_cn']}数控机床{model} CRT出现{failure['name']}问题？不用修了。\n\n直接换LCD模块：\n- 接口：{brand['connector']}\n- 供电：{power_cn}\n- 适配：{', '.join(brand['controls'][:3])}\n- 价格：{brand['price']}\n- 安装：15分钟，不改CNC参数\n\n更多资料: cncdisplay.com"
    zh = {"title": zh_title, "body": zh_body}

    return q, body, li_post, zh

# ============================================================
# 全自动发文平台
# ============================================================

def get_article_for_post():
    """Get fresh article (cached per day) for today's posts."""
    article = get_daily_article()
    CACHE_FILE = OUTPUT / f"article_{TODAY}.json"
    # Since get_daily_article handles caching internally, just return
    return article


def post_devto():
    """Dev.to API - DA 92, Dofollow"""
    cfg = load_config()
    api_key = cfg.get("devto_api_key")
    if not api_key:
        print("[SKIP] Dev.to - no API key")
        return None

    article = get_article_for_post()
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

    # Canonical taken — retry without canonical_url (let Dev.to auto-generate)
    if resp.status_code == 422 and "canonical" in resp.text.lower():
        save_devto_used(article["canonical"])
        print(f"  [RETRY] Canonical taken, posting without canonical_url")
        resp = requests.post(
            "https://dev.to/api/articles",
            headers={"api-key": api_key, "Content-Type": "application/json"},
            json={"article": {
                "title": article["title"],
                "body_markdown": article["body_devto"],
                "published": True,
                "tags": article["devto_tags"],
            }},
            timeout=30
        )
        if resp.status_code in [200, 201]:
            url = resp.json().get("url", "")
            print(f"  [OK] {url}")
            log_post("Dev.to", article["title"], url)
            return url

    print(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:200]}")
    return None


def post_telegraph():
    """Telegra.ph API - DA 86, Dofollow"""
    cfg = load_config()
    token = cfg.get("telegraph_token")
    if not token:
        print("[SKIP] Telegra.ph - no token")
        return None

    article = get_article_for_post()
    telegraph_title = article["title"]
    paragraphs = []
    for line in article["body_devto"].split("\n"):
        line = line.strip()
        if not line or line.startswith("---"):
            continue
        if line.startswith("## "):
            paragraphs.append({"tag": "h2", "children": [line[3:]]})
        elif line.startswith("### "):
            paragraphs.append({"tag": "h3", "children": [line[4:]]})
        elif line.startswith("|"):
            continue
        elif line.startswith("[") and "](" in line:
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
            "content": paragraphs[:50],
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
    """Rentry.co - DA ~60, Dofollow"""
    article = get_article_for_post()
    slug = f"cnc-display-{TODAY.replace('-', '')}"

    # Condensed version for Rentry
    lines = article["body_devto"].split("\n")
    body_preview = "\n".join([l for l in lines[:30] if not l.startswith("|")])[:2000]
    text = f"# {article['title']}\n\n{body_preview}\n\n---\nFull guide: {article['canonical']}\ncncdisplay.com"

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
    """GitLab Snippets - DA 96, Dofollow"""
    cfg = load_config()
    pat = cfg.get("gitlab_pat")
    if not pat:
        print("[SKIP] GitLab - no PAT")
        return None

    article = get_article_for_post()
    print(f"\n[GitLab] {article['title'][:70]}...")

    snippet_content = f"# {article['title']}\n\n{article['body_devto']}\n\n---\n*Reference: cncdisplay.com*"

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
    """Generate Reddit, LinkedIn, Chinese post content from today's AI article."""
    article = get_article_for_post()
    q, body, li, zh = generate_manual_content(article)

    day_dir = OUTPUT / TODAY
    day_dir.mkdir(exist_ok=True)

    f = day_dir / "reddit_post.txt"
    f.write_text(f"TITLE: {q}\n\n{body}", encoding='utf-8')

    f = day_dir / "linkedin_post.txt"
    f.write_text(li, encoding='utf-8')

    f = day_dir / "zh_post.md"
    f.write_text(f"# {zh['title']}\n\n{zh['body']}", encoding='utf-8')

    print(f"\n[GEN] Manual content → {day_dir}")
    print(f"  reddit_post.txt | linkedin_post.txt | zh_post.md")
    return day_dir


# ============================================================
# 状态报告
# ============================================================
def print_status():
    print(f"=== CNCdisplay Daily Backlink Engine v5.0 (AI) ===")
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
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, cwd=str(BASE))
        if r.returncode != 0:
            print("[GIT] Not a git repo, skipping")
            return

        files = ["backlinks_daily/post_tracker.csv", "backlinks_daily/devto_canonicals.json"]
        today_dir = OUTPUT / TODAY
        if today_dir.exists():
            files.append(f"backlinks_daily/{TODAY}")

        # Also commit the cached AI article
        article_cache = OUTPUT / f"article_{TODAY}.json"
        if article_cache.exists():
            files.append(f"backlinks_daily/article_{TODAY}.json")

        for f in files:
            subprocess.run(["git", "add", f], capture_output=True, cwd=str(BASE))

        r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, cwd=str(BASE))
        if r.returncode == 0:
            print("[GIT] No changes to commit")
            return

        msg = f"Daily backlinks {TODAY}: AI-generated auto-published"
        r = subprocess.run(["git", "commit", "-m", msg], capture_output=True, cwd=str(BASE))
        if r.returncode != 0:
            err = r.stderr.decode('utf-8', errors='replace')[:200]
            print(f"[GIT] Commit failed: {err}")
            return

        r = subprocess.run(["git", "push", "origin", "main"], capture_output=True, cwd=str(BASE))
        if r.returncode != 0:
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True, cwd=str(BASE))
            r = subprocess.run(["git", "push", "origin", "main"], capture_output=True, cwd=str(BASE))
            if r.returncode == 0:
                print("[GIT] Pushed (after rebase)")
            else:
                print(f"[GIT] Push failed: {r.stderr.decode('utf-8', errors='replace')[:200]}")
                return

        print(f"[GIT] Pushed: {msg}")
    except Exception as e:
        print(f"[GIT] Error: {e}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print_status()

    results = {}

    def safe_post(name, fn):
        try:
            r = fn()
            if r:
                results[name] = r
            else:
                print(f"  [SKIP] {name}")
        except Exception as e:
            print(f"  [FAIL] {name}: {type(e).__name__}: {e}")

    safe_post("Dev.to", post_devto)
    safe_post("Telegra.ph", post_telegraph)
    safe_post("Rentry.co", post_rentry)
    safe_post("GitLab", post_gitlab)

    day_dir = gen_manual_content()

    print(f"\n{'='*50}")
    print(f"DONE: {len(results)} auto-published + manual content generated")
    for k, v in results.items():
        print(f"  [{k}] {v}")
    print(f"  [Manual] {day_dir}")
    print(f"{'='*50}")

    auto_git_push()
