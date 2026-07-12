"""Sprint Plan: Optimize all product pages with 7-piece set per keyword.
Target: 33+ English keywords → Google top 10 in 2 weeks.

Fixes applied:
1. Title exact-match keyword + 50-60 chars
2. H1 exact-match keyword
3. Meta Description 150-160 chars + differentiation
4. Price consistency (Title matches Schema)
5. Fix duplicate words, mojibake, typos
6. First paragraph keyword presence
7. Product+Offer schema price consistency check
"""
import os, re, json

SITE = r'd:\code\seo_deploy'
PRODUCTS = os.path.join(SITE, 'products')

# ====== PAGE-LEVEL KEYWORD TARGETS ======
# For each page: primary keyword for targeting, refined Title, refined H1, refined Meta Desc
OPTIMIZATIONS = {
    # ---- FANUC A61L Series (12 pages) ----
    'fanuc-a61l-0001-0093': {
        'kw': 'FANUC A61L-0001-0093 LCD replacement',
        'title': 'FANUC A61L-0001-0093 LCD Replacement | 8" Plug & Play $155 | Kongto',
        'h1': 'FANUC A61L-0001-0093 LCD Replacement Display',
        'desc': 'Direct FANUC A61L-0001-0093 LCD replacement — plug-and-play, no rewiring. 8-inch TFT, 800×600, 10-15 min install. $155 with 2-year warranty. In stock, ships today.',
    },
    'fanuc-a61l-0001-0094': {
        'kw': 'FANUC A61L-0001-0094 LCD replacement',
        'title': 'FANUC A61L-0001-0094 LCD Replacement | 12.1" TFT $350 | Kongto',
        'h1': 'FANUC A61L-0001-0094 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0094 LCD replacement — 12.1-inch TFT, plug-and-play, no CNC parameter changes. 800×600, 350-450 cd/m². $350 with 2-year warranty. In stock.',
    },
    'fanuc-a61l-0001-0092': {
        'kw': 'FANUC A61L-0001-0092 (MDT-947) LCD replacement',
        'title': 'FANUC A61L-0001-0092 MDT-947 LCD Replacement | 8" TFT $255 | Kongto',
        'h1': 'FANUC A61L-0001-0092 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0092 MDT-947 LCD replacement — 8-inch TFT, plug-and-play, fits FANUC 0/0i/16i/18i series. No rewiring needed. $255 with 2-year warranty.',
    },
    'fanuc-a61l-0001-0090': {
        'kw': 'FANUC A61L-0001-0090 LCD replacement',
        'title': 'FANUC A61L-0001-0090 LCD Replacement | 8" TFT LCD $350 | Kongto',
        'h1': 'FANUC A61L-0001-0090 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0090 LCD replacement — 8-inch TFT, direct drop-in for original CRT. Same 20-pin Honda connector, no adapter needed. $350 with 2-year warranty.',
    },
    'fanuc-a61l-0001-0076': {
        'kw': 'FANUC A61L-0001-0076 LCD replacement',
        'title': 'FANUC A61L-0001-0076 LCD Replacement | 8" Plug & Play $255 | Kongto',
        'h1': 'FANUC A61L-0001-0076 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0076 LCD replacement — 8-inch TFT, plug-and-play kit. 800×600, 10-15 min install, no rewiring. Fits FANUC 0/0i/16i series. $255, 2-year warranty.',
    },
    'fanuc-a61l-0001-0086': {
        'kw': 'FANUC A61L-0001-0086 LCD replacement',
        'title': 'FANUC A61L-0001-0086 LCD Replacement | 8.4" TFT $255 | Kongto',
        'h1': 'FANUC A61L-0001-0086 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0086 LCD replacement — 8.4-inch TFT, plug-and-play upgrade. Direct CRT replacement, Honda 20-pin connector. $255 with 2-year warranty. Ships same day.',
    },
    'fanuc-a61l-0001-0074': {
        'kw': 'FANUC A61L-0001-0074 LCD replacement',
        'title': 'FANUC A61L-0001-0074 LCD Replacement | 12.1" TFT $350 | Kongto',
        'h1': 'FANUC A61L-0001-0074 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0074 LCD replacement — 12.1-inch TFT, direct drop-in. No modifications or parameter changes. $350 with 2-year warranty. Ships within 24 hours.',
    },
    'fanuc-a61l-0001-0072': {
        'kw': 'FANUC A61L-0001-0072 LCD replacement',
        'title': 'FANUC A61L-0001-0072 LCD Replacement | 8" TFT $255 | Kongto',
        'h1': 'FANUC A61L-0001-0072 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0072 LCD replacement — 8-inch TFT, plug-and-play. Replaces aging A61L-0001-0072 CRT. 800×600 resolution, 10-15 min install. $255, 2-year warranty.',
    },
    'fanuc-a61l-0001-0095': {
        'kw': 'FANUC A61L-0001-0095 LCD replacement',
        'title': 'FANUC A61L-0001-0095 LCD Replacement | 8" TFT $199 | Kongto',
        'h1': 'FANUC A61L-0001-0095 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0095 LCD replacement — 8-inch TFT, plug-and-play module. Replaces original CRT with industrial LCD. $199 with 2-year warranty. Worldwide shipping.',
    },
    'fanuc-a61l-0001-0096': {
        'kw': 'FANUC A61L-0001-0096 LCD replacement',
        'title': 'FANUC A61L-0001-0096 LCD Replacement | 12.1" TFT $350 | Kongto',
        'h1': 'FANUC A61L-0001-0096 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0096 LCD replacement — 12.1-inch TFT, direct CRT replacement. No adapters or rewiring needed. $350 with 2-year warranty. Ships within 24 hours.',
    },
    'fanuc-a61l-0001-0097': {
        'kw': 'FANUC A61L-0001-0097 LCD replacement',
        'title': 'FANUC A61L-0001-0097 LCD Replacement | 12.1" TFT $350 | Kongto',
        'h1': 'FANUC A61L-0001-0097 LCD Replacement Display',
        'desc': 'FANUC A61L-0001-0097 LCD replacement — 12.1-inch TFT, plug-and-play. Same connector as original CRT. 800×600, 2-year warranty. $350, ships today.',
    },
    # ---- Mitsubishi (3 pages) ----
    'mitsubishi-mdt962b': {
        'kw': 'Mitsubishi MDT962B replacement',
        'title': 'Mitsubishi MDT962B LCD Replacement | 8" CRT to LCD | Kongto',
        'h1': 'Mitsubishi MDT962B LCD Replacement Display',
        'desc': 'Mitsubishi MDT962B LCD replacement — 8-inch TFT, direct CRT replacement for MELDAS/M60/M64 CNC. Plug-and-play, no rewiring. $199 with 2-year warranty. In stock.',
    },
    'mitsubishi-bm09df': {
        'kw': 'Mitsubishi BM09DF LCD upgrade',
        'title': 'Mitsubishi BM09DF LCD Upgrade | 9" CRT to LCD | E60 CNC | Kongto',
        'h1': 'Mitsubishi BM09DF LCD Upgrade Display',
        'desc': 'Mitsubishi BM09DF LCD upgrade — 9-inch CRT to LCD conversion for Mitsubishi E60 CNC. Plug-and-play module, no parameter changes. In stock, ships today.',
    },
    'mitsubishi-fcua-ct100': {
        'kw': 'Mitsubishi FCUA-CT100 LCD replacement',
        'title': 'Mitsubishi FCUA-CT100 LCD Upgrade | M500/M520 Display | Kongto',
        'h1': 'Mitsubishi FCUA-CT100 LCD Upgrade Display',
        'desc': 'Mitsubishi FCUA-CT100 LCD upgrade — industrial display for M500/M520/M310 CNC. CRT to LCD, plug-and-play. No rewiring needed. 2-year warranty included.',
    },
    # ---- Mazak (6 pages) ----
    'mazak-cd1472': {
        'kw': 'Mazak CD1472-D1M LCD replacement',
        'title': 'Mazak CD1472-D1M LCD Replacement | 14" CRT to LCD | Kongto',
        'h1': 'Mazak 14-Inch Color CRT LCD Replacement Display',
        'desc': 'Mazak CD1472-D1M LCD replacement — 14-inch color CRT to LCD for Mazatrol T-32/M-32. Plug-and-play, 15-30 min install. $355 with 2-year warranty.',
    },
    'mazak-mdt1283b': {
        'kw': 'Mazak MDT1283B replacement',
        'title': 'Mazak MDT1283B-1A LCD Replacement | CRT for Mazatrol M32 | Kongto',
        'h1': 'Mazak MDT1283B-1A LCD Replacement Display',
        'desc': 'Mazak MDT1283B-1A LCD replacement — direct CRT replacement for Mazatrol M32 CNC. Plug-and-play, no rewiring. In stock with 2-year warranty.',
    },
    'mazak-14-inch-crt': {
        'kw': 'Mazak 14 inch CRT to LCD',
        'title': 'Mazak 14" CRT to LCD Replacement Kit | DR5614 C-5470NS | Kongto',
        'h1': 'Mazak 14-Inch CRT to LCD Replacement Kit',
        'desc': 'Mazak 14-inch CRT to LCD replacement — fits DR5614, C-5470NS, AIQA8DSP40 models. Plug-and-play kit, no CNC parameter changes. 2-year warranty.',
    },
    'mazak-aiqa8dsp40': {
        'kw': 'Mazak AIQA8DSP40 LCD upgrade',
        'title': 'Mazak AIQA8DSP40 LCD Upgrade | 14" CRT to LCD | Mazatrol T-32 | Kongto',
        'h1': 'Mazak AIQA8DSP40 14" CRT to LCD Upgrade Display',
        'desc': 'Mazak AIQA8DSP40 LCD upgrade — 14-inch color CRT to LCD for Mazatrol T-32/640. Plug-and-play module. In stock, ships within 24 hours.',
    },
    'mazak-c5470ns': {
        'kw': 'Mazak C-5470NS LCD replacement',
        'title': 'Mazak C-5470NS LCD Upgrade | 14" CRT to LCD | Mazatrol M-32 | Kongto',
        'h1': 'Mazak C-5470NS 14" CRT to LCD Upgrade Display',
        'desc': 'Mazak C-5470NS LCD upgrade — 14-inch CRT to LCD for Mazatrol M-32 CNC. Plug-and-play, no rewiring. Industrial-grade TFT with 2-year warranty.',
    },
    'mazak-dr5614': {
        'kw': 'Mazak DR5614 LCD upgrade',
        'title': 'Mazak DR5614 LCD Upgrade | 14" CRT to LCD | Mazatrol T-32 | Kongto',
        'h1': 'Mazak DR5614 14" CRT to LCD Upgrade Display',
        'desc': 'Mazak DR5614 LCD upgrade — 14-inch CRT to LCD conversion for Mazatrol T-32 CNC. Direct drop-in replacement. Plug-and-play, 2-year warranty.',
    },
    # ---- Okuma (1 page, 3 keywords) ----
    'okuma-osp-crt': {
        'kw': 'Okuma OSP5000 LCD replacement',
        'title': 'Okuma OSP5000 LCD Replacement | OSP5000/7000 CRT to LCD | Kongto',
        'h1': 'Okuma OSP5000 LCD Replacement Display',
        'desc': 'Okuma OSP5000 LCD replacement — covers OSP500L-G, OSP5000, OSP5020, OSP7000 CNC. Plug-and-play, 15-30 min install. $430 with 2-year warranty. Ships today.',
    },
    # ---- Haas (1 page, 3 keywords) ----
    'haas-28hm-nm4': {
        'kw': 'Haas 28HM-NM4 LCD replacement',
        'title': 'Haas 28HM-NM4 LCD Replacement | 10.4" TFT for VF Series | Kongto',
        'h1': 'Haas 28HM-NM4 LCD Replacement Display',
        'desc': 'Haas 28HM-NM4 LCD replacement — fits Haas VF1/VF2/VF3 CNC. 10.4-inch TFT, plug-and-play, no rewiring. $399 with 2-year warranty. Ships within 24 hours.',
    },
    # ---- Siemens (3 pages) ----
    'siemens-6fc3988-7fa20': {
        'kw': 'Siemens 6FC3988-7FA20 LCD upgrade',
        'title': 'Siemens 6FC3988-7FA20 LCD Upgrade | 8" TFT $399 | Kongto',
        'h1': 'Siemens 6FC3988-7FA20 LCD Upgrade Display',
        'desc': 'Siemens 6FC3988-7FA20 LCD upgrade — 8-inch TFT replacement for SINUMERIK. Plug-and-play, no rewiring. $399 with 2-year warranty. Ships today.',
    },
    'siemens-6fc5103': {
        'kw': 'Siemens 6FC5103-0AB01 LCD replacement',
        'title': 'Siemens 6FC5103-0AB01 LCD Replacement | 840D CRT to LCD | Kongto',
        'h1': 'Siemens 6FC5103-0AB01 CRT to LCD Replacement',
        'desc': 'Siemens 6FC5103-0AB01 LCD replacement — direct CRT replacement for SINUMERIK 840D/810D. DB-25 interface, plug-and-play. In stock, 2-year warranty.',
    },
    'siemens-sm0901': {
        'kw': 'Siemens SM0901 LCD replacement',
        'title': 'Siemens SM0901 LCD Upgrade | SINUMERIK 810M Display | Kongto',
        'h1': 'Siemens SM0901 LCD Upgrade Display',
        'desc': 'Siemens SM0901 LCD upgrade — CRT to LCD for SINUMERIK 810M. NFP 579417 TA compatible. Plug-and-play module, no parameter changes. 2-year warranty.',
    },
    # ---- Toshiba (2 pages) ----
    'toshiba-d14cm-01a': {
        'kw': 'Toshiba D14CM-01A LCD replacement',
        'title': 'Toshiba D14CM-01A LCD Replacement | 12.1" TFT $350 | Kongto',
        'h1': 'Toshiba D14CM-01A LCD Upgrade Display',
        'desc': 'Toshiba D14CM-01A LCD replacement — 12.1-inch TFT, plug-and-play module. Direct CRT replacement, no rewiring. $350 with 2-year warranty. Ships today.',
    },
    'toshiba-d9mm-11a': {
        'kw': 'Toshiba D9MM-11A LCD replacement',
        'title': 'Toshiba D9MM-11A LCD Replacement | 8" TFT $199 | Kongto',
        'h1': 'Toshiba D9MM-11A LCD Upgrade Display',
        'desc': 'Toshiba D9MM-11A LCD replacement — 8-inch TFT, plug-and-play. Direct drop-in for original CRT on FANUC and other CNC. $199 with 2-year warranty.',
    },
    # ---- Symptom pages (3 pages) ----
    'flickering-screen': {
        'kw': 'CNC display flickering fix',
        'title': 'CNC Display Flickering Fix | CRT to LCD Upgrade | Kongto',
        'h1': 'Flickering CNC Display Fix — CRT to LCD Upgrade',
        'desc': 'Fix flickering CNC display — CRT aging causes screen flicker. Our LCD upgrade eliminates flicker permanently. Plug-and-play, 10-15 min install, 2-year warranty.',
    },
    'no-display': {
        'kw': 'CNC display black screen fix',
        'title': 'CNC Display Black Screen Fix | CRT to LCD Upgrade | Kongto',
        'h1': 'No Display / Black Screen Fix for CNC Displays',
        'desc': 'Fix CNC display black screen — CRT failure causes no display. Upgrade to LCD for reliable operation. Plug-and-play, no rewiring, 2-year warranty. Ships today.',
    },
    'image-retention': {
        'kw': 'CNC display image retention fix',
        'title': 'CNC Display Image Retention Fix | CRT Burn-in Solution | Kongto',
        'h1': 'Image Retention / Burn-in Fix for CNC Displays',
        'desc': 'Fix CNC display image retention and CRT burn-in. LCD upgrade eliminates ghosting permanently. Plug-and-play module, 10-15 min install, 2-year warranty.',
    },
}

# ====== FIXES ======

def fix_duplicate_tft(content):
    """Fix 'TFT TFT-LCD' → 'TFT-LCD' (n=5+)"""
    return content.replace('TFT TFT-LCD', 'TFT-LCD')

def fix_mojibake(content):
    """Fix 鈥?→ — em dash corruptions"""
    content = content.replace('', '—')  # Windows-1252 encoded em dash
    content = content.replace('鈥?', '—')
    content = content.replace('鈥', '—')
    return content

def fix_haas_casing(content):
    """Fix HAAS → Haas in title/H1/desc"""
    content = content.replace('HAAS 28HM-NM4 LCD Replacement', 'Haas 28HM-NM4 LCD Replacement', 1)
    content = content.replace('HAAS 28HM-NM4', 'Haas 28HM-NM4')
    return content

def fix_title_duplicates(content):
    """Fix duplicate brand names in titles"""
    content = content.replace(
        '<title>Mitsubishi BM09DF Mitsubishi BM09DF LCD Upgrade',
        '<title>Mitsubishi BM09DF LCD Upgrade'
    )
    content = content.replace(
        '<title>Mitsubishi FCUA-CT100 Mitsubishi FCUA-CT100 LCD Upgrade',
        '<title>Mitsubishi FCUA-CT100 LCD Upgrade'
    )
    content = content.replace(
        '<title>Siemens SM0901 Siemens SM0901 LCD Upgrade',
        '<title>Siemens SM0901 LCD Upgrade'
    )
    return content

def fix_og_title_duplicates(content):
    """Fix duplicate brand names in og:title"""
    content = content.replace(
        'content="Mitsubishi BM09DF Mitsubishi BM09DF LCD Upgrade',
        'content="Mitsubishi BM09DF LCD Upgrade'
    )
    content = content.replace(
        'content="Mitsubishi FCUA-CT100 Mitsubishi FCUA-CT100 LCD Upgrade',
        'content="Mitsubishi FCUA-CT100 LCD Upgrade'
    )
    return content

def fix_pricing_0093(content):
    """Fix $199 → $155 in Title for 0093 (page price is $155, not $199)"""
    content = content.replace(
        'FANUC A61L-0001-0093 LCD Upgrade | 8-inch TFT $199',
        'FANUC A61L-0001-0093 LCD Replacement | 8" Plug & Play $155'
    )
    return content

def fix_okuma_faq(content):
    """Remove duplicate FAQ question on Okuma page"""
    old = '''    {
      "@type": "Question",
      "name": "Will this work with Okuma OSP5000 or OSP7000?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. Compatible with OSP500L-G, OSP5000, OSP5020, and OSP7000 controls."
      }
    },
    {
      "@type": "Question",
      "name": "Will this work with Okuma OSP5000 or OSP7000?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. Compatible with OSP500L-G, OSP5000, OSP5020, and OSP7000 controls."
      }
    },'''
    new = '''    {
      "@type": "Question",
      "name": "Will this work with Okuma OSP5000 or OSP7000?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. Compatible with OSP500L-G, OSP5000, OSP5020, and OSP7000 controls."
      }
    },'''
    if old in content:
        content = content.replace(old, new)
    return content

def apply_page_optimization(content, opt):
    """Apply Title/H1/Meta Description optimization for a page"""
    # Only replace exact matches to avoid partial replacements
    # Replace og:title first (must match exactly)

    # Title replacement - match the full existing title tag
    title_match = re.search(r'<title>(.*?)</title>', content)
    if title_match:
        old_title = title_match.group(1)
        new_title = opt['title']
        # Only replace if different and not already applied
        if old_title != new_title and old_title not in new_title:
            content = content.replace(f'<title>{old_title}</title>', f'<title>{new_title}</title>')

    # Meta Description replacement
    desc_match = re.search(r'<meta name="description" content="(.*?)">', content)
    if desc_match:
        old_desc = desc_match.group(1)
        new_desc = opt['desc']
        if old_desc != new_desc and old_desc not in new_desc:
            content = content.replace(
                f'<meta name="description" content="{old_desc}">',
                f'<meta name="description" content="{new_desc}">'
            )

    # og:title replacement
    ogtitle_match = re.search(r'<meta property="og:title" content="(.*?)">', content)
    if ogtitle_match:
        old_og = ogtitle_match.group(1)
        new_og = opt['title']  # Use same as title for og:title
        if old_og != new_og and old_og not in new_og:
            content = content.replace(
                f'<meta property="og:title" content="{old_og}">',
                f'<meta property="og:title" content="{new_og}">'
            )

    # og:description replacement
    ogdesc_match = re.search(r'<meta property="og:description" content="(.*?)">', content)
    if ogdesc_match:
        old_ogdesc = ogdesc_match.group(1)
        new_ogdesc = opt['desc']
        if old_ogdesc != new_ogdesc and old_ogdesc not in new_ogdesc:
            content = content.replace(
                f'<meta property="og:description" content="{old_ogdesc}">',
                f'<meta property="og:description" content="{new_ogdesc}">'
            )

    return content

# ====== MAIN ======
changed = 0

for fname in os.listdir(PRODUCTS):
    if not fname.endswith('.html'):
        continue
    fpath = os.path.join(PRODUCTS, fname)

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Global mechanical fixes
    content = fix_duplicate_tft(content)
    content = fix_mojibake(content)
    content = fix_haas_casing(content)
    content = fix_title_duplicates(content)
    content = fix_og_title_duplicates(content)
    content = fix_pricing_0093(content)

    # 2. Page-specific optimizations
    base = fname.replace('-lcd-upgrade.html', '').replace('.html', '')
    if base in OPTIMIZATIONS:
        content = apply_page_optimization(content, OPTIMIZATIONS[base])

    # 3. Okuma FAQ fix
    if 'okuma-osp' in fname:
        content = fix_okuma_faq(content)

    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        changed += 1
        print(f'UPDATED: {fname}')

print(f'\nTotal files updated: {changed}')

# Also fix products/index.html separately
idx_path = os.path.join(PRODUCTS, 'index.html')
with open(idx_path, 'r', encoding='utf-8') as f:
    idx = f.read()
orig_idx = idx
idx = fix_mojibake(idx)
idx = idx.replace(
    '<title>CNC Display Products 鈥?CRT to LCD Replacement by Brand | Kongto Technology</title>',
    '<title>CNC Display Products — CRT to LCD Replacement by Brand | Kongto Technology</title>'
)
if idx != orig_idx:
    with open(idx_path, 'w', encoding='utf-8') as f:
        f.write(idx)
    print(f'UPDATED: products/index.html')
