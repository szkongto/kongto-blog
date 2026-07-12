"""Sprint Plan Day 2: Homepage + Brand page + ZH product sync.
Target: Optimize Titles/Descs/H1s for ranking.
"""
import os, re

SITE = r'd:\code\seo_deploy'

# ====== EN HOMEPAGE ======
HOME_EN = r'd:\code\seo_deploy\index.html'

# ====== BRAND PAGE OPTIMIZATIONS ======
BRAND_TARGETS = {
    'FANUC.html': {
        'title': 'FANUC CRT to LCD Replacement | A61L Series Plug & Play | Kongto',
        'desc': 'FANUC CRT to LCD replacement — A61L-0001-0072 to 0097 series. Plug-and-play, no rewiring, 10-15 min install. Factory direct, 2-year warranty, ships today.',
        'h1': 'FANUC',  # keep as-is, FANUC is an acronym
    },
    'HAAS.html': {
        'title': 'Haas CNC CRT to LCD Replacement | VF Series LCD Upgrade | Kongto',
        'desc': 'Haas CNC CRT to LCD replacement — VF1/VF2/VF3, 28HM-NM4 compatible. Plug-and-play, no modifications. 10.4-inch TFT, 2-year warranty. Ships today.',
        'h1': 'Haas',  # fix all-caps
    },
    'Heidenhain.html': {
        'title': 'Heidenhain CRT to LCD Upgrade | BE211/BE411/BE510 | Kongto',
        'desc': 'Heidenhain CNC CRT to LCD upgrade — BE211, BE411, BE510 models. TNC 310/320/410/415/425/430 compatible. Factory direct, 2-year warranty, ships today.',
        'h1': 'Heidenhain CRT to LCD Display Upgrade',
    },
    'index.html': {
        'title': 'CNC Display Upgrade by Brand — CRT to LCD | Kongto',
        'desc': 'CNC display upgrade by brand — FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas, Heidenhain, Toshiba. Factory direct CRT-to-LCD modules. 2-year warranty.',
        'h1': 'CNC Display Upgrade Solutions by Brand',
    },
    'Matsushita.html': {
        'title': 'Matsushita CRT to LCD Upgrade | Panasonic CNC Display | Kongto',
        'desc': 'Matsushita (Panasonic) CRT to LCD upgrade — OEM supplier for Mazak CRT displays incl. TR-120S9C. Factory direct, in stock, 2-year warranty.',
        'h1': 'Matsushita (Panasonic) CRT to LCD Display Upgrade',
    },
    'MAZAK.html': {
        'title': 'Mazak CRT to LCD Replacement | CD1472/MDT1283B | Kongto',
        'desc': 'Mazak CRT to LCD replacement — CD1472, C-5470NS, MDT1283B, DR5614 series. Plug-and-play, no rewiring. Mazatrol T-32/M-32 compatible. 2-year warranty.',
        'h1': 'Mazak CNC Display Solutions',
    },
    'Mitsubishi.html': {
        'title': 'Mitsubishi CRT to LCD Upgrade | MDT962B/M500/M60 | Kongto',
        'desc': 'Mitsubishi CRT to LCD upgrade — MDT962B, BM09DF, FCUA-CT100. MELDAS M60/M64/M500/M520. Plug-and-play, no modifications. 2-year warranty.',
        'h1': 'Mitsubishi CNC Display Solutions',
    },
    'OKUMA.html': {
        'title': 'Okuma CRT to LCD Replacement | OSP5000/7000 Upgrade | Kongto',
        'desc': 'Okuma CRT to LCD replacement — OSP500L-G, OSP5000, OSP5020, OSP7000. Plug-and-play, no rewiring. $430, 2-year warranty, ships today.',
        'h1': 'Okuma CNC Display Solutions',
    },
    'Siemens.html': {
        'title': 'Siemens CRT to LCD Upgrade | SINUMERIK 840D Display | Kongto',
        'desc': 'Siemens CRT to LCD upgrade — SINUMERIK 810/820/840D, 6FC3988, SM0901. Plug-and-play, no parameter changes. Factory direct, 2-year warranty.',
        'h1': 'Siemens CNC Display Solutions',
    },
    'Toshiba.html': {
        'title': 'Toshiba CRT to LCD Replacement | D9MM-11A/D14CM-01A | Kongto',
        'desc': 'Toshiba CRT to LCD replacement — D9MM-11A, D14CM-01A. FANUC OEM equivalents. Factory direct, plug-and-play, in stock, 2-year warranty.',
        'h1': 'Toshiba CRT to LCD Display Upgrade',
    },
}

# ====== ZH PRODUCT TITLE OPTIMIZATIONS ======
# Key mapping: EN filename base → ZH optimized Title, Desc
ZH_PRODUCT_TARGETS = {
    'fanuc-a61l-0001-0093': {
        'title': 'FANUC A61L-0001-0093 LCD升级替换 | 8英寸CRT改TFT $155 | 江图科技',
        'desc': 'FANUC A61L-0001-0093 LCD升级替换方案 — 即插即用，无需改线。8英寸TFT，800×600，10-15分钟安装。$155含2年质保，现货当天发货。',
    },
    'fanuc-a61l-0001-0094': {
        'title': 'FANUC A61L-0001-0094 LCD升级替换 | 12.1英寸TFT $350 | 江图科技',
        'desc': 'FANUC A61L-0001-0094 LCD升级替换 — 12.1英寸TFT，即插即用，无需改参数。800×600，350-450cd/m²。$350含2年质保，现货。',
    },
    'fanuc-a61l-0001-0092': {
        'title': 'FANUC A61L-0001-0092 MDT-947 LCD替换 | 8英寸TFT $255 | 江图科技',
        'desc': 'FANUC A61L-0001-0092 MDT-947 LCD替换 — 8英寸TFT，即插即用，兼容FANUC 0/0i/16i/18i系列。无需改线。$255含2年质保。',
    },
    'fanuc-a61l-0001-0090': {
        'title': 'FANUC A61L-0001-0090 LCD升级替换 | 8英寸TFT $350 | 江图科技',
        'desc': 'FANUC A61L-0001-0090 LCD升级替换 — 8英寸TFT，直接替换原CRT。同款20针Honda接口，无需转接。$350含2年质保。',
    },
    'fanuc-a61l-0001-0076': {
        'title': 'FANUC A61L-0001-0076 LCD替换 | 8英寸即插即用 $255 | 江图科技',
        'desc': 'FANUC A61L-0001-0076 LCD替换 — 8英寸TFT，即插即用套件。800×600，10-15分钟安装。兼容FANUC 0/0i系列。$255含2年质保。',
    },
    'fanuc-a61l-0001-0086': {
        'title': 'FANUC A61L-0001-0086 LCD替换 | 8.4英寸TFT $255 | 江图科技',
        'desc': 'FANUC A61L-0001-0086 LCD替换 — 8.4英寸TFT，即插即用升级。直接替换CRT，Honda 20针接口。$255含2年质保，当天发货。',
    },
    'fanuc-a61l-0001-0074': {
        'title': 'FANUC A61L-0001-0074 LCD替换 | 12.1英寸TFT $299 | 江图科技',
        'desc': 'FANUC A61L-0001-0074 LCD替换 — 12.1英寸TFT，直接替换。无需改装或改参数。$299含2年质保，24小时内发货。',
    },
    'fanuc-a61l-0001-0072': {
        'title': 'FANUC A61L-0001-0072 LCD替换 | 8英寸TFT $255 | 江图科技',
        'desc': 'FANUC A61L-0001-0072 LCD替换 — 8英寸TFT，即插即用。替换老化A61L-0001-0072 CRT。800×600分辨率。$255含2年质保。',
    },
    'fanuc-a61l-0001-0095': {
        'title': 'FANUC A61L-0001-0095 LCD替换 | 8英寸TFT $199 | 江图科技',
        'desc': 'FANUC A61L-0001-0095 LCD替换 — 8英寸TFT，即插即用模组。替换原CRT为工业LCD。$199含2年质保，全球包邮。',
    },
    'fanuc-a61l-0001-0096': {
        'title': 'FANUC A61L-0001-0096 LCD替换 | 12.1英寸TFT $350 | 江图科技',
        'desc': 'FANUC A61L-0001-0096 LCD替换 — 12.1英寸TFT，直接替换CRT。无需转接头或改线。$350含2年质保，24小时内发货。',
    },
    'fanuc-a61l-0001-0097': {
        'title': 'FANUC A61L-0001-0097 LCD替换 | 12.1英寸TFT $350 | 江图科技',
        'desc': 'FANUC A61L-0001-0097 LCD替换 — 12.1英寸TFT，即插即用。与原CRT同接口。800×600。$350含2年质保，当天发货。',
    },
    'mitsubishi-mdt962b': {
        'title': '三菱MDT962B LCD替换 | 8英寸CRT改LCD | 江图科技',
        'desc': '三菱MDT962B LCD替换 — 8英寸TFT，直接替换MELDAS/M60/M64 CRT。即插即用，无需改线。$199含2年质保。现货。',
    },
    'mitsubishi-bm09df': {
        'title': '三菱BM09DF LCD升级 | 9英寸CRT改LCD | E60数控 | 江图科技',
        'desc': '三菱BM09DF LCD升级 — 9英寸CRT转LCD，用于三菱E60/E68数控系统。即插即用模组，无需改参数。现货，当天发货。',
    },
    'mitsubishi-fcua-ct100': {
        'title': '三菱FCUA-CT100 LCD升级 | M500/M520显示屏 | 江图科技',
        'desc': '三菱FCUA-CT100 LCD升级 — M500/M520/M310数控用工业显示屏。CRT转LCD，即插即用。含2年质保。',
    },
    'mazak-cd1472': {
        'title': 'Mazak CD1472-D1M LCD替换 | 14英寸CRT改LCD | 江图科技',
        'desc': 'Mazak CD1472-D1M LCD替换 — 14英寸彩色CRT转LCD，用于Mazatrol T-32/M-32数控。即插即用。$355含2年质保。',
    },
    'mazak-mdt1283b': {
        'title': 'Mazak MDT1283B-1A LCD替换 | Mazatrol M32 CRT改LCD | 江图科技',
        'desc': 'Mazak MDT1283B-1A LCD替换 — 直接替换Mazatrol M32数控CRT。即插即用，无需改线。含2年质保。',
    },
    'mazak-14-inch-crt': {
        'title': 'Mazak 14英寸CRT改LCD替换套件 | DR5614/C-5470NS | 江图科技',
        'desc': 'Mazak 14英寸CRT改LCD替换 — 兼容DR5614、C-5470NS、AIQA8DSP40等型号。即插即用套件，无需改参数。2年质保。',
    },
    'mazak-aiqa8dsp40': {
        'title': 'Mazak AIQA8DSP40 LCD升级 | 14英寸CRT改LCD | Mazatrol T-32 | 江图科技',
        'desc': 'Mazak AIQA8DSP40 LCD升级 — 14英寸彩色CRT转LCD，用于Mazatrol T-32/640数控。即插即用模组。现货。',
    },
    'mazak-c5470ns': {
        'title': 'Mazak C-5470NS LCD升级 | 14英寸CRT改LCD | Mazatrol M-32 | 江图科技',
        'desc': 'Mazak C-5470NS LCD升级 — 14英寸CRT转LCD，用于Mazatrol M-32数控。即插即用。工业级TFT，2年质保。',
    },
    'mazak-dr5614': {
        'title': 'Mazak DR5614 LCD升级 | 14英寸CRT改LCD | Mazatrol T-32 | 江图科技',
        'desc': 'Mazak DR5614 LCD升级 — 14英寸CRT转LCD，用于Mazatrol T-32数控。直接替换。即插即用，2年质保。',
    },
    'okuma-osp-crt': {
        'title': 'Okuma OSP5000 LCD升级替换 | OSP5000/7000 CRT改LCD | 江图科技',
        'desc': 'Okuma OSP5000 LCD升级替换 — 兼容OSP500L-G、OSP5000、OSP5020、OSP7000数控。即插即用。$430含2年质保，当天发货。',
    },
    'haas-28hm-nm4': {
        'title': 'Haas 28HM-NM4 LCD替换 | 10.4英寸TFT | VF系列 | 江图科技',
        'desc': 'Haas 28HM-NM4 LCD替换 — 兼容Haas VF1/VF2/VF3数控。10.4英寸TFT，即插即用。$399含2年质保，24小时内发货。',
    },
    'siemens-6fc3988-7fa20': {
        'title': '西门子6FC3988-7FA20 LCD升级 | 8英寸TFT $399 | 江图科技',
        'desc': '西门子6FC3988-7FA20 LCD升级 — 8英寸TFT替换SINUMERIK CRT。即插即用。$399含2年质保，当天发货。',
    },
    'siemens-6fc5103': {
        'title': '西门子6FC5103-0AB01 LCD替换 | 840D CRT改LCD | 江图科技',
        'desc': '西门子6FC5103-0AB01 LCD替换 — 直接替换SINUMERIK 840D/810D CRT。DB-25接口，即插即用。现货，2年质保。',
    },
    'siemens-sm0901': {
        'title': '西门子SM0901 LCD升级 | SINUMERIK 810M显示屏 | 江图科技',
        'desc': '西门子SM0901 LCD升级 — CRT转LCD用于SINUMERIK 810M。NFP 579417 TA兼容。即插即用模组，2年质保。',
    },
    'toshiba-d14cm-01a': {
        'title': '东芝D14CM-01A LCD替换 | 12.1英寸TFT $350 | 江图科技',
        'desc': '东芝D14CM-01A LCD替换 — 12.1英寸TFT，即插即用模组。直接替换CRT。$350含2年质保，当天发货。',
    },
    'toshiba-d9mm-11a': {
        'title': '东芝D9MM-11A LCD替换 | 8英寸TFT $199 | 江图科技',
        'desc': '东芝D9MM-11A LCD替换 — 8英寸TFT，即插即用。直接替换FANUC及其他数控原CRT。$199含2年质保。',
    },
}

# ====== HOME EN ======
with open(HOME_EN, 'r', encoding='utf-8') as f:
    home_en = f.read()

orig = home_en

# Fix homepage Title - more keyword-rich for "CNC display upgrade"
home_en = home_en.replace(
    '<title>CNC CRT to LCD Upgrade | FANUC, Mitsubishi, Siemens | Kongto</title>',
    '<title>CNC Display Upgrade | CRT to LCD for FANUC/Mitsubishi/Siemens | Kongto</title>'
)
# Fix homepage meta description - includes differentiation + 500+ models
home_en = home_en.replace(
    'content="CRT-to-LCD retrofit for FANUC, Mitsubishi, Siemens, Mazak, Okuma and Haas CNC systems. Plug-and-play, 30-min install, 18-month warranty, 500+ enterprises."',
    'content="CNC display upgrade — CRT to LCD retrofit for FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas. Plug-and-play, 10-15 min install, no rewiring. Factory direct, 500+ models, 2-year warranty."'
)
# Fix og:title
home_en = home_en.replace(
    'content="CNC CRT to LCD Upgrade | FANUC, Mitsubishi, Siemens | Kongto"',
    'content="CNC Display Upgrade | CRT to LCD for FANUC/Mitsubishi/Siemens | Kongto"'
)

if home_en != orig:
    with open(HOME_EN, 'w', encoding='utf-8') as f:
        f.write(home_en)
    print(f'UPDATED: index.html')

# ====== BRAND PAGES ======
brands_dir = os.path.join(SITE, 'brands')
for fname in os.listdir(brands_dir):
    if not fname.endswith('.html'):
        continue
    if fname not in BRAND_TARGETS:
        continue

    fpath = os.path.join(brands_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    opt = BRAND_TARGETS[fname]

    # Fix mojibake
    content = content.replace('鈥?', '—')

    # Fix Title
    title_match = re.search(r'<title>(.*?)</title>', content)
    if title_match and title_match.group(1) != opt['title']:
        content = content.replace(f'<title>{title_match.group(1)}</title>', f'<title>{opt["title"]}</title>')

    # Fix Meta Description
    desc_match = re.search(r'<meta name="description" content="(.*?)">', content)
    if desc_match and desc_match.group(1) != opt['desc']:
        content = content.replace(
            f'<meta name="description" content="{desc_match.group(1)}">',
            f'<meta name="description" content="{opt["desc"]}">'
        )

    # Fix H1 - find H1 that doesn't match target
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if h1_match:
        old_h1 = h1_match.group(1).strip()
        if old_h1 != opt['h1']:
            content = content.replace(
                f'<h1>{old_h1}</h1>',
                f'<h1>{opt["h1"]}</h1>'
            )

    # Fix og:title to match
    og_match = re.search(r'<meta property="og:title" content="(.*?)">', content)
    if og_match and og_match.group(1) != opt['title']:
        content = content.replace(
            f'<meta property="og:title" content="{og_match.group(1)}">',
            f'<meta property="og:title" content="{opt["title"]}">'
        )

    # Fix og:description to match meta description
    ogdesc_match = re.search(r'<meta property="og:description" content="(.*?)">', content)
    if ogdesc_match and ogdesc_match.group(1) != opt['desc']:
        content = content.replace(
            f'<meta property="og:description" content="{ogdesc_match.group(1)}">',
            f'<meta property="og:description" content="{opt["desc"]}">'
        )

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'UPDATED: brands/{fname}')

# ====== ZH PRODUCT PAGES ======
zh_products_dir = os.path.join(SITE, 'zh', 'products')

def get_zh_base(fname):
    """Extract base name without -lcd-upgrade suffix"""
    base = fname.replace('-lcd-upgrade.html', '').replace('.html', '')
    # Handle special cases
    if base == 'haas-28hm-nm4':
        # Check if HAAS vs haas
        pass
    return base

for fname in os.listdir(zh_products_dir):
    if not fname.endswith('.html'):
        continue
    base = get_zh_base(fname)

    # Map EN base to ZH targets
    zh_base = base
    if zh_base not in ZH_PRODUCT_TARGETS:
        continue

    fpath = os.path.join(zh_products_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    opt = ZH_PRODUCT_TARGETS[zh_base]

    # Fix Title
    title_match = re.search(r'<title>(.*?)</title>', content)
    if title_match and title_match.group(1) != opt['title']:
        content = content.replace(f'<title>{title_match.group(1)}</title>', f'<title>{opt["title"]}</title>')

    # Fix Meta Description
    desc_match = re.search(r'<meta name="description" content="(.*?)">', content)
    if desc_match and desc_match.group(1) != opt['desc']:
        content = content.replace(
            f'<meta name="description" content="{desc_match.group(1)}">',
            f'<meta name="description" content="{opt["desc"]}">'
        )

    # Fix og:title
    og_match = re.search(r'<meta property="og:title" content="(.*?)">', content)
    if og_match and og_match.group(1) != opt['title']:
        # Only replace exact matches to avoid partial
        if og_match.group(1) in content:
            content = content.replace(
                f'<meta property="og:title" content="{og_match.group(1)}">',
                f'<meta property="og:title" content="{opt["title"]}">'
            )

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'UPDATED: zh/products/{fname}')

print('\nDone.')
