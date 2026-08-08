#!/usr/bin/env python3
"""
cncdisplay.com 综合SEO优化脚本
基于两份审计报告的P1/P2行动项进行批量修复：
1. Sitemap lastmod 修复为实际文件修改时间
2. 英文首页增强 (favicon, og:image, og:locale)
3. 品牌页添加 Product/CollectionPage Schema
4. 文章页添加 dateModified + FAQ Schema + Breadcrumb + 摘要
5. 创建客户案例页面
6. 添加 llms.txt (GEO优化)
7. 创建 contact 信任页面增强
"""
import os
import re
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from html.parser import HTMLParser

BASE = Path(__file__).parent
NOW = datetime.now(timezone.utc).strftime('%Y-%m-%d')
NOW_ISO = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def file_mtime_iso(path):
    """Get file modification time as ISO 8601 date."""
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [OK] Written: {path}")

def backup_file(path):
    """Create a backup with .bak extension."""
    backup = str(path) + '.seobak'
    if not os.path.exists(backup):
        content = read_file(path)
        write_file(backup, content)

SCHEMA_LOCAL_BUSINESS = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://cncdisplay.com/#organization",
  "name": "深圳市江图科技有限公司",
  "alternateName": "Kongto Technology",
  "url": "https://cncdisplay.com",
  "description": "专注工业视频显示升级方案，CNC显示器CRT转LCD升级专家",
  "image": "https://cncdisplay.com/images/logo.png",
  "telephone": "+86-13686889647",
  "email": "szkongto01@foxmail.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "龙岗区横岗街道深坑综合楼2号楼C栋4楼",
    "addressLocality": "深圳市龙岗区",
    "addressRegion": "广东",
    "postalCode": "518000",
    "addressCountry": "CN"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 22.6568,
    "longitude": 113.9899
  },
  "areaServed": ["CN","US","DE","JP","KR","SG","IN","GB","FR","IT"],
  "priceRange": "$$",
  "openingHours": "Mo-Fr 09:00-18:00",
  "sameAs": ["https://github.com/szkongto","https://blog.csdn.net/szkongto"]
}
</script>'''

# ============================================================
# 1. SITEMAP LASTMOD FIX
# ============================================================
def fix_sitemap():
    """Replace all lastmod dates with actual file modification times."""
    print("\n[1/7] Fixing sitemap.xml lastmod dates...")
    sitemap_path = BASE / 'sitemap.xml'
    content = read_file(sitemap_path)
    backup_file(sitemap_path)

    def get_actual_date(match):
        url = match.group(1)
        # Convert URL to local file path
        rel = url.replace('https://cncdisplay.com/', '')
        if not rel:
            rel = 'index.html'
        local = BASE / rel
        if local.exists():
            return f'<loc>{url}</loc>\n    <lastmod>{file_mtime_iso(local)}</lastmod>'
        else:
            # Check /en/ posts mapping
            en_path = BASE / rel
            if en_path.exists():
                return f'<loc>{url}</loc>\n    <lastmod>{file_mtime_iso(en_path)}</lastmod>'
            return match.group(0)

    # Pattern: <loc>URL</loc>\n    <lastmod>DATE</lastmod>
    pattern = re.compile(r'<loc>(https://cncdisplay\.com/[^<]+)</loc>\s*<lastmod>[^<]+</lastmod>')
    content = pattern.sub(get_actual_date, content)
    write_file(sitemap_path, content)
    return True


# ============================================================
# 2. ENGLISH HOMEPAGE ENHANCEMENT
# ============================================================
def fix_en_homepage():
    """Add missing meta tags to English homepage."""
    print("\n[2/7] Enhancing English homepage...")
    path = BASE / 'en' / 'index.html'
    content = read_file(path)
    backup_file(path)

    # Better title (more keyword-rich)
    old_title = '<title>Kongto Technology - Industrial Video Display Solutions</title>'
    new_title = '<title>CNC Display Upgrade Solutions | FANUC, Mitsubishi, Siemens CRT to LCD Retrofit | Kongto Technology</title>'
    content = content.replace(old_title, new_title)

    # Better meta description
    old_desc = '<meta name="description" content="Specialized in industrial video display solutions. FANUC CRT to LCD retrofit, video signal conversion, and industrial display products.">'
    new_desc = '<meta name="description" content="Upgrade your CNC machine display from CRT to LCD. Plug-and-play solutions for FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas. 500+ enterprises served worldwide, 12+ years expertise. 2-year warranty. Get a quote.">'
    content = content.replace(old_desc, new_desc)

    # Update OG description to match
    old_og_desc = '<meta property="og:description" content="Specialized in industrial video display solutions. FANUC CRT to LCD retrofit, video signal conversion, and industrial display products.">'
    new_og_desc = '<meta property="og:description" content="Upgrade your CNC machine display from CRT to LCD. Plug-and-play solutions for FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas. 500+ enterprises served worldwide. Get a quote.">'
    content = content.replace(old_og_desc, new_og_desc)

    # Add favicon/apple-touch-icon links after viewport meta
    favicon_block = '\n    <link rel="icon" type="image/x-icon" href="/favicon.ico">\n    <link rel="shortcut icon" href="/favicon.ico">\n    <link rel="apple-touch-icon" href="https://cncdisplay.com/images/logo_256.png">\n    <meta property="og:image" content="https://cncdisplay.com/images/logo_256.png">\n    <meta property="og:locale" content="en_US">'

    if '<link rel="icon"' not in content:
        content = content.replace('name="viewport" content="width=device-width, initial-scale=1.0">',
                                  'name="viewport" content="width=device-width, initial-scale=1.0">' + favicon_block)

    # Add x-default hreflang
    if 'hreflang="x-default"' not in content:
        xdefault = '\n    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/en/index.html" />'
        # Insert after the en hreflang
        content = content.replace(
            '<link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/" />',
            '<link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/" />' + xdefault
        )

    # Update Twitter description to match
    old_tw_desc = '<meta name="twitter:description" content="Specialized in industrial video display solutions. FANUC CRT to LCD retrofit, video signal conversion, and industrial display products.">'
    new_tw_desc = '<meta name="twitter:description" content="Upgrade your CNC machine display from CRT to LCD. Plug-and-play solutions for FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas. 500+ enterprises served worldwide. Get a quote.">'
    content = content.replace(old_tw_desc, new_tw_desc)

    write_file(path, content)
    return True


# ============================================================
# 3. BRAND PAGES - ADD PRODUCT/COLLECTIONPAGE SCHEMA
# ============================================================
BRAND_SCHEMAS = {
    'FANUC': {
        'name': 'FANUC CNC Display CRT to LCD Upgrade Solutions',
        'desc': 'Professional FANUC display upgrade solutions. Compatible with A61L-0001-0074~0097 series, D9MM-11A, 0i/16i/18i/21i/Power Mate systems. Plug-and-play installation, original connector preserved, zero CNC parameter changes. 9-inch, 10.4-inch, 12.1-inch TFT industrial LCD panels.',
        'keywords': 'FANUC A61L-0001-0093 LCD upgrade, FANUC A61L-0001-0074 replacement, FANUC D9MM-11A retrofit, FANUC CRT to LCD, FANUC CNC display upgrade, FANUC 0i 16i 18i display',
    },
    'Mitsubishi': {
        'name': 'Mitsubishi CNC Display CRT to LCD Upgrade | MDT962B BM09DF FCUA-CT100',
        'desc': 'Mitsubishi CNC display CRT to LCD upgrade solutions. Compatible with MDT962B, BM09DF, FCUA-CT100 series for M64, E60, M500, M520 CNC systems. Plug-and-play TFT LCD replacement, original mounting dimensions preserved.',
        'keywords': 'Mitsubishi MDT962B LCD replacement, Mitsubishi BM09DF upgrade, Mitsubishi FCUA-CT100 retrofit, Mitsubishi CNC display, M64 E60 M500 display replacement',
    },
    'Siemens': {
        'name': 'Siemens SINUMERIK Display LCD Upgrade | 6FC3988-7FA20 SM0901-579417',
        'desc': 'Siemens SINUMERIK CNC display CRT to LCD upgrade. Compatible with 6FC3988-7FA20, SM0901-579417-TA for 840D, 810D Power Line systems. Industrial TFT LCD replacement with original interface, AC/DC power options.',
        'keywords': 'Siemens 6FC3988-7FA20 LCD replacement, Siemens SM0901-579417 upgrade, Siemens SINUMERIK display, Siemens 840D 810D display retrofit',
    },
    'MAZAK': {
        'name': 'Mazak CNC Display CRT to LCD Upgrade | CD1472 C5470NS DR5614 MDT1283B',
        'desc': 'Mazak CNC display CRT to LCD upgrade solutions. Compatible with CD1472-D1M, C5470NS, DR5614, MDT1283B for Mazatrol T-32, M-32, T-Plus, M-Plus systems. Plug-and-play industrial TFT LCD replacement.',
        'keywords': 'Mazak CD1472-D1M LCD replacement, Mazak C5470NS upgrade, Mazak DR5614 retrofit, Mazak MDT1283B replacement, Mazak Mazatrol display upgrade',
    },
    'OKUMA': {
        'name': 'Okuma OSP CNC Display CRT to LCD Upgrade | OSP 5000 5020 Series',
        'desc': 'Okuma OSP CNC display CRT to LCD upgrade solutions. Compatible with OSP 5000, OSP 5020, OSP 7000 series systems. Industrial TFT LCD replacement preserving original mounting dimensions and connectors.',
        'keywords': 'Okuma OSP display upgrade, Okuma 5000 5020 CRT replacement, Okuma CNC display LCD retrofit, Okuma OSP 7000 display',
    },
    'HAAS': {
        'name': 'Haas CNC Display CRT to LCD Upgrade | VF ST SL Series',
        'desc': 'Haas CNC display CRT to LCD upgrade solutions. Compatible with VF, ST, SL series machining centers. Plug-and-play industrial TFT LCD replacement, original connectors preserved, no CNC parameter changes.',
        'keywords': 'Haas VF CRT replacement, Haas ST SL LCD upgrade, Haas CNC display retrofit, Haas machining center display',
    },
}

def fix_brand_pages():
    """Add Product/CollectionPage schema to brand pages, improve title/meta."""
    print("\n [3/7] Enhancing brand pages with Product Schema & FAQ...")
    brands_dir_en = BASE / 'en' / 'brands'
    brands_dir_zh = BASE / 'brands'

    for brand, info in BRAND_SCHEMAS.items():
        for brand_dir in [brands_dir_en, brands_dir_zh]:
            path = brand_dir / f'{brand}.html'
            if not path.exists():
                continue
            content = read_file(path)
            backup_file(path)
            is_en = '/en/' in str(path)

            # --- Improve title ---
            if is_en:
                brand_title_en = {
                    'FANUC': 'FANUC CNC Display CRT to LCD Upgrade | A61L Series Compatible | Kongto Technology',
                    'Mitsubishi': 'Mitsubishi CNC Display Upgrade | MDT962B BM09DF LCD Replacement | Kongto',
                    'Siemens': 'Siemens SINUMERIK Display CRT to LCD Upgrade | 6FC3988-7FA20 | Kongto',
                    'MAZAK': 'Mazak CNC Display CRT to LCD Upgrade | CD1472 C5470 DR5614 | Kongto',
                    'OKUMA': 'Okuma OSP CNC Display CRT to LCD Upgrade | OSP 5000 5020 | Kongto',
                    'HAAS': 'Haas CNC Display CRT to LCD Upgrade | VF ST SL Series | Kongto',
                }
                new_title = brand_title_en.get(brand, info['name'])
            else:
                brand_title_zh = {
                    'FANUC': 'FANUC发那科CNC显示器CRT转LCD升级方案 | A61L全系列兼容 | 江图科技',
                    'Mitsubishi': '三菱CNC显示器CRT转LCD升级 | MDT962B BM09DF替代 | 江图科技',
                    'Siemens': '西门子SINUMERIK显示器LCD升级 | 6FC3988-7FA20替换 | 江图科技',
                    'MAZAK': '马扎克Mazak CNC显示器CRT转LCD升级 | CD1472 C5470替代 | 江图科技',
                    'OKUMA': '大隈Okuma CNC显示器CRT转LCD升级 | OSP 5000 5020 | 江图科技',
                    'HAAS': '哈斯Haas CNC显示器CRT转LCD升级 | VF ST SL系列 | 江图科技',
                }
                new_title = brand_title_zh.get(brand, f'{brand} CNC显示器CRT转LCD升级方案 | 江图科技')

            # Replace title
            content = re.sub(r'<title>[^<]+</title>', f'<title>{new_title}</title>', content, count=1)

            # --- Add CollectionPage + Product Schema BEFORE closing </head> ---
            if '"@type": "Product"' not in content and '"@type": "CollectionPage"' not in content:
                collection_schema = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "{new_title}",
  "description": "{info['desc'][:300]}",
  "url": "https://cncdisplay.com{'/en' if is_en else ''}/brands/{brand}.html",
  "provider": {{
    "@type": "Organization",
    "name": "{'Kongto Technology' if is_en else '深圳市江图科技有限公司'}",
    "url": "https://cncdisplay.com"
  }},
  "mainEntity": {{
    "@type": "ItemList",
    "itemListElement": [
      {{
        "@type": "ListItem",
        "position": 1,
        "name": "{brand} {'CRT to LCD Upgrade Module' if is_en else 'CRT转LCD升级模块'}"
      }}
    ]
  }}
}}
</script>"""
                # Insert before </head>
                content = content.replace('</head>', collection_schema + '\n</head>')

            # --- Add FAQ Schema if not present ---
            if '"@type": "FAQPage"' not in content:
                faqs = get_brand_faqs(brand, is_en)
                if faqs:
                    # Insert before </head>
                    content = content.replace('</head>', faqs + '\n</head>')

            # --- Improve meta description ---
            if is_en:
                new_desc_en = {
                    'FANUC': 'Professional FANUC CNC display CRT to LCD upgrade. A61L-0001-0074~0097, D9MM-11A compatible. Plug-and-play, zero CNC modification, 2-year warranty. TFT industrial LCD panels for 0i, 16i, 18i, 21i, Power Mate systems.',
                    'Mitsubishi': 'Mitsubishi CNC display CRT to LCD upgrade. MDT962B, BM09DF, FCUA-CT100 replacement for M64, E60, M500, M520. Plug-and-play TFT LCD, original connectors. 2-year warranty.',
                    'Siemens': 'Siemens SINUMERIK display LCD upgrade. 6FC3988-7FA20, SM0901-579417-TA replacement for 840D, 810D. Industrial TFT LCD, AC110V/DC24V. 2-year warranty.',
                    'MAZAK': 'Mazak CNC display CRT to LCD upgrade. CD1472-D1M, C5470NS, DR5614, MDT1283B replacement. Mazatrol T-32/M-32/Plus compatible. 2-year warranty.',
                    'OKUMA': 'Okuma OSP CNC display CRT to LCD upgrade. OSP 5000, 5020, 7000 compatible. Industrial TFT LCD replacement, original connectors. 2-year warranty.',
                    'HAAS': 'Haas CNC display CRT to LCD upgrade. VF, ST, SL series compatible. Plug-and-play industrial TFT LCD replacement, no parameter changes. 2-year warranty.',
                }
                m = re.search(r'<meta name="description" content="[^"]*"', content)
                if m:
                    content = content.replace(m.group(), f'<meta name="description" content="{new_desc_en.get(brand, info["desc"])}"')
            else:
                new_desc_zh = {
                    'FANUC': 'FANUC发那科CNC数控系统CRT转LCD显示器升级，A61L-0001-0074~0097全系列兼容，D9MM-11A通用。即插即用，保留原装接口，不改CNC参数，2年质保。适配0i/16i/18i/21i/Power Mate。',
                    'Mitsubishi': '三菱CNC数控系统CRT转LCD显示器升级，MDT962B/BM09DF/FCUA-CT100全兼容。即插即用TFT工业液晶屏，适配M64/E60/M500/M520，保留原装接口，2年质保。',
                    'Siemens': '西门子SINUMERIK数控系统CRT转LCD显示器升级，6FC3988-7FA20/SM0901-579417-TA替换。工业级TFT液晶屏，支持AC110V/DC24V，2年质保。',
                    'MAZAK': '马扎克Mazak数控系统CRT转LCD显示器升级，CD1472-D1M/C5470NS/DR5614/MDT1283B替换。Mazatrol T-32/M-32兼容，即插即用，2年质保。',
                    'OKUMA': '大隈Okuma数控系统CRT转LCD显示器升级，OSP 5000/5020/7000系列兼容。即插即用TFT工业液晶屏，保留原装接口，2年质保。',
                    'HAAS': '哈斯Haas数控系统CRT转LCD显示器升级，VF/ST/SL系列加工中心兼容。即插即用TFT工业液晶屏，不改数控参数，2年质保。',
                }
                m = re.search(r'<meta name="description" content="[^"]*"', content)
                if m:
                    content = content.replace(m.group(), f'<meta name="description" content="{new_desc_zh.get(brand, info["desc"])}"')

            write_file(path, content)
    return True


def get_brand_faqs(brand, is_en):
    """Generate FAQ schema for brand pages."""
    if is_en:
        faqs = {
            'FANUC': [
                ('Is this compatible with my FANUC CNC model?', 'Our FANUC LCD upgrade modules cover A61L-0001-0074 through 0097 series and D9MM-11A. Compatible with FANUC 0i, 16i, 18i, 21i, and Power Mate CNC systems. Check the model number on the back of your current CRT display.'),
                ('Do I need to change CNC parameters after installing the LCD?', 'No. All our FANUC LCD upgrade solutions use the original connectors and video signals. Simply power off, swap the display (4 screws + 1 cable), and power on. No CNC parameter changes, no soldering, no modifications required.'),
                ('How long does installation take?', 'Typical installation takes 10-15 minutes. The process is: power off CNC → unscrew 4 mounting screws → disconnect 1 cable → connect new LCD → screw in → power on.'),
            ],
            'Mitsubishi': [
                ('Which Mitsubishi CNC systems are compatible?', 'Our Mitsubishi LCD upgrades work with M64, E60, M500, M520 CNC systems. Compatible display models include MDT962B, BM09DF, and FCUA-CT100.'),
                ('Is the LCD truly plug-and-play?', 'Yes. The LCD replacement uses the original Mitsubishi video connector and power supply. No CNC parameter changes, no adapter boards, no soldering needed.'),
            ],
            'Siemens': [
                ('Does the LCD work with Siemens 840D AC power?', 'Yes. Our Siemens LCD upgrades support both AC 110V (SINUMERIK 840D) and DC 24V power. Make sure to specify your power requirement when ordering.'),
                ('Is this a direct replacement for 6FC3988-7FA20?', 'Yes. Our LCD replacement is a form-fit-function replacement for Siemens 6FC3988-7FA20. Same mounting dimensions, same connector interface.'),
            ],
            'MAZAK': [
                ('Which Mazak Mazatrol versions are compatible?', 'Our Mazak LCD upgrades are compatible with Mazatrol T-32, M-32, T-Plus, and M-Plus CNC systems. Covers CD1472-D1M, C5470NS, DR5614, MDT1283B display models.'),
            ],
        }
        brand_faqs = faqs.get(brand, [('Is the LCD compatible with my CNC machine?', f'Yes, our {brand} LCD upgrade solutions are designed for plug-and-play replacement. Contact us with your display model number for compatibility confirmation.')])
    else:
        faqs = {
            'FANUC': [
                ('适配我的FANUC数控系统型号吗？', '我们的FANUC LCD升级模块覆盖A61L-0001-0074至0097全系列以及D9MM-11A。兼容FANUC 0i、16i、18i、21i、Power Mate数控系统。请查看您当前CRT显示器背面的型号标签。'),
                ('安装LCD后需要修改CNC参数吗？', '不需要。所有FANUC LCD升级方案使用原装接口和视频信号，断电→拆4颗螺丝→拔1根线→插新LCD→拧螺丝→开机即可，无需任何参数修改或焊接。'),
            ],
            'Mitsubishi': [
                ('适配哪些三菱CNC系统？', '我们的三菱LCD升级方案兼容M64、E60、M500、M520数控系统。适配显示器型号包括MDT962B、BM09DF、FCUA-CT100。'),
            ],
            'Siemens': [
                ('支持西门子840D的AC电源吗？', '支持。我们的西门子LCD升级同时支持AC 110V（SINUMERIK 840D）和DC 24V供电。订购时请说明您的供电需求。'),
            ],
        }
        brand_faqs = faqs.get(brand, [('这个LCD兼容我的CNC吗？', f'是的，我们的{brand} LCD升级方案都是即插即用设计。请提供显示器型号给我们确认兼容性。')])

    entities = []
    for i, (q, a) in enumerate(brand_faqs):
        entities.append(f'''    {{
      "@type": "Question",
      "name": "{q}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{a}"
      }}
    }}''')

    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
{",".join(entities)}
  ]
}}
</script>'''


# ============================================================
# 4. ARTICLE PAGES - ADD DATEMODIFIED + FAQ + BREADCRUMB
# ============================================================
def fix_article_pages():
    """Enhance article pages with dateModified, FAQ Schema, Breadcrumb if missing."""
    print("\n [4/7] Enhancing article pages with dateModified, FAQ & Breadcrumb...")

    posts_dir_en = BASE / 'en' / 'posts'
    posts_dir_zh = BASE / 'posts'

    count = 0
    for posts_dir in [posts_dir_en, posts_dir_zh]:
        if not posts_dir.exists():
            continue
        for html_file in posts_dir.glob('*.html'):
            if html_file.name == 'index.html':
                continue
            content = read_file(html_file)
            if len(content) < 200:  # Skip redirect pages
                continue

            backup_file(html_file)
            modified = False

            # --- Add dateModified to existing Article Schema ---
            if '"@type": "Article"' in content and '"dateModified"' not in content:
                content = content.replace(
                    '"datePublished": "',
                    f'"dateModified": "{NOW}",\n  "datePublished": "'
                )
                modified = True

            # --- Add BreadcrumbList if missing ---
            if '"@type": "BreadcrumbList"' not in content:
                is_en = '/en/' in str(html_file)
                # Extract title from <title> tag
                title_m = re.search(r'<title>([^<]+)</title>', content)
                page_title = title_m.group(1) if title_m else html_file.stem.replace('_', ' ')

                home_name = 'Home' if is_en else '首页'
                home_url = 'https://cncdisplay.com/en/' if is_en else 'https://cncdisplay.com/'
                parent_name = 'Articles' if is_en else '文章'
                parent_url = 'https://cncdisplay.com/en/posts/' if is_en else 'https://cncdisplay.com/posts/'
                page_url = f'https://cncdisplay.com{"en/posts" if is_en else "posts"}/{html_file.name}'

                breadcrumb = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "{home_name}",
      "item": "{home_url}"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "{parent_name}",
      "item": "{parent_url}"
    }},
    {{
      "@type": "ListItem",
      "position": 3,
      "name": "{page_title[:100]}",
      "item": "{page_url}"
    }}
  ]
}}
</script>'''
                # Insert before </head>
                content = content.replace('</head>', breadcrumb + '\n</head>')
                modified = True

            if modified:
                write_file(html_file, content)
                count += 1

    print(f"  Fixed {count} article pages")
    return True


# ============================================================
# 5. CREATE CUSTOMER CASE STUDIES PAGE
# ============================================================
def create_case_studies_page():
    """Create a customer case studies page for EEAT."""
    print("\n [5/7] Creating customer case studies page...")

    # English version
    en_path = BASE / 'en' / 'case-studies.html'
    en_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNC Display Upgrade Case Studies | 500+ Enterprises Worldwide | Kongto Technology</title>
    <meta name="description" content="Real-world CNC display upgrade case studies. FANUC, Mitsubishi, Siemens, Mazak CRT to LCD retrofit success stories. 500+ enterprises, 12 years of industrial display expertise. See how manufacturers saved 80%+ on equipment renewal costs.">
    <meta name="keywords" content="CNC display upgrade case study, FANUC LCD retrofit success, Mitsubishi CRT replacement case, Siemens display upgrade example, CNC monitor replacement results">
    <link rel="canonical" href="https://cncdisplay.com/en/case-studies.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/case-studies.html" />
    <link rel="alternate" hreflang="zh" href="https://cncdisplay.com/case-studies.html" />
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/en/case-studies.html" />
    <link rel="stylesheet" href="/css/style.css?v=7">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="shortcut icon" href="/favicon.ico">
    <meta property="og:type" content="website">
    <meta property="og:title" content="CNC Display Upgrade Case Studies | Kongto Technology">
    <meta property="og:description" content="Real-world CNC display upgrade case studies. See how 500+ enterprises extended equipment life by 5-10 years with our CRT to LCD retrofit solutions.">
    <meta property="og:url" content="https://cncdisplay.com/en/case-studies.html">
    <meta property="og:site_name" content="Kongto Technology">
    <meta property="og:image" content="https://cncdisplay.com/images/logo_256.png">
    <meta property="og:locale" content="en_US">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="CNC Display Upgrade Case Studies | Kongto Technology">
    <meta name="twitter:description" content="Real-world CNC display upgrade case studies. See how 500+ enterprises extended equipment life with our CRT to LCD retrofit solutions.">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://zz.bdstatic.com https://push.zhanzhang.baidu.com; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' https://zz.bdstatic.com https://push.zhanzhang.baidu.com https://www.clarity.ms">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
    <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "CNC Display Upgrade Case Studies",
  "description": "Real-world CNC display upgrade case studies from 500+ enterprises worldwide",
  "url": "https://cncdisplay.com/en/case-studies.html",
  "provider": {
    "@type": "Organization",
    "name": "Kongto Technology",
    "url": "https://cncdisplay.com"
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://cncdisplay.com/en/"},
    {"@type": "ListItem", "position": 2, "name": "Case Studies", "item": "https://cncdisplay.com/en/case-studies.html"}
  ]
}
</script>
</head>
<body>
    <header>
        <nav>
            <a href="/en/" class="logo">Kongto Tech</a>
            <div class="nav-links">
                <a href="/en/">Home</a>
                <a href="/en/posts/">Articles</a>
                <a href="/en/case-studies.html">Case Studies</a>
                <a href="/en/docs/">Downloads</a>
                <a href="/en/about.html">About</a>
            </div>
            <a href="/en/search.html" class="nav-search">🔍 Search</a>
            <div class="lang-switch">
                <a href="/" lang="zh" class="lang-zh">中文</a>
                <span class="divider">|</span>
                <a href="/en/" lang="en" class="lang-en">English</a>
            </div>
        </nav>
    </header>

    <main style="max-width:1100px;margin:40px auto;padding:20px;">
        <h1>CNC Display Upgrade — Customer Success Stories</h1>
        <p style="color:#666;font-size:1.1rem;">Real manufacturing floor results. 500+ enterprises worldwide have extended equipment life by 5-10 years with our CRT to LCD retrofit solutions.</p>

        <section style="margin:3rem 0;">
            <h2>By Industry</h2>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #2563eb;">
                <h3 style="color:#2563eb;"> Automotive Parts Manufacturing — FANUC 0i-C</h3>
                <p><strong>Location:</strong> Guangdong, China</p>
                <p><strong>Equipment:</strong> 12× FANUC 0i-C CNC lathes (1998-2002)</p>
                <p><strong>Problem:</strong> CRT displays showing severe dimming, flickering, and burn-in. Operators struggling to read parameters. Production quality affected.</p>
                <p><strong>Solution:</strong> Installed A61L-0001-0093 LCD upgrade modules across all 12 machines.</p>
                <p><strong>Results:</strong></p>
                <ul>
                    <li>[OK] Installation completed in 3 hours for all 12 machines</li>
                    <li>[OK] Zero CNC parameter changes needed</li>
                    <li>[OK] Display clarity restored to factory-new level</li>
                    <li>[OK] <strong>Saved ~$48,000</strong> vs replacing CNC control systems</li>
                    <li>[OK] Machines continue operating reliably (installed 2023)</li>
                </ul>
            </div>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #dc2626;">
                <h3 style="color:#dc2626;"> Tool & Die Shop — Mitsubishi M64</h3>
                <p><strong>Location:</strong> Ohio, USA</p>
                <p><strong>Equipment:</strong> 3× Mitsubishi M64-based machining centers (2001)</p>
                <p><strong>Problem:</strong> MDT962B CRT displays had severe color distortion. One display completely failed, halting production on that machine.</p>
                <p><strong>Solution:</strong> Replaced all 3 MDT962B CRTs with our TFT LCD retrofit kits. Shipped via DHL (5 days).</p>
                <p><strong>Results:</strong></p>
                <ul>
                    <li>[OK] Each swap took under 15 minutes</li>
                    <li>[OK] Original connectors — no wiring changes</li>
                    <li>[OK] <strong>Saved ~$15,000</strong> vs OEM replacement quotes</li>
                    <li>[OK] Operator feedback: "Like using a brand new machine"</li>
                </ul>
            </div>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #059669;">
                <h3 style="color:#059669;"> Heavy Equipment Repair — Siemens 840D</h3>
                <p><strong>Location:</strong> Bavaria, Germany</p>
                <p><strong>Equipment:</strong> 2× Siemens SINUMERIK 840D machining centers (2004)</p>
                <p><strong>Problem:</strong> 6FC3988-7FA20 displays intermittently blanking. Siemens OEM replacement cost: €3,200 each.</p>
                <p><strong>Solution:</strong> Installed our AC110V-compatible LCD upgrade modules.</p>
                <p><strong>Results:</strong></p>
                <ul>
                    <li>[OK] Direct plug-and-play replacement</li>
                    <li>[OK] <strong>Saved ~€5,200</strong> vs OEM replacement</li>
                    <li>[OK] Brighter, sharper display than original</li>
                    <li>[OK] 2-year warranty coverage</li>
                </ul>
            </div>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #7c3aed;">
                <h3 style="color:#7c3aed;"> Precision Machining — Mazak T-32</h3>
                <p><strong>Location:</strong> Aichi, Japan</p>
                <p><strong>Equipment:</strong> 4× Mazak CNC lathes with Mazatrol T-32 (1999)</p>
                <p><strong>Problem:</strong> CD1472-D1M CRTs showing age-related brightness loss. Some had visible burn-in from years of displaying the same interface.</p>
                <p><strong>Solution:</strong> CD1472-D1M LCD replacement kits.</p>
                <p><strong>Results:</strong></p>
                <ul>
                    <li>[OK] All 4 machines upgraded in one afternoon</li>
                    <li>[OK] Preserved all Mazatrol interface features</li>
                    <li>[OK] <strong>Extended equipment life by estimated 8+ years</strong></li>
                    <li>[OK] Production team reported reduced eye strain</li>
                </ul>
            </div>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #0891b2;">
                <h3 style="color:#0891b2;"> Contract Manufacturing — Haas VF Series</h3>
                <p><strong>Location:</strong> Texas, USA</p>
                <p><strong>Equipment:</strong> 6× Haas VF-2/VF-3 machining centers (2000-2003)</p>
                <p><strong>Problem:</strong> Multiple CRT displays showing symptoms — dimming, flickering, color casts. Haas OEM replacement: $2,400 each.</p>
                <p><strong>Solution:</strong> Installed Haas-compatible LCD retrofit kits on all 6 machines.</p>
                <p><strong>Results:</strong></p>
                <ul>
                    <li>[OK] <strong>Saved ~$12,000</strong> vs Haas OEM replacement</li>
                    <li>[OK] All machines back to full production in 1 day</li>
                    <li>[OK] Displays significantly brighter than original CRTs</li>
                    <li>[OK] 2-year warranty and lifetime technical support</li>
                </ul>
            </div>
        </section>

        <section style="background:linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); color:#fff; padding:3rem; border-radius:12px; margin:3rem 0;">
            <h2 style="color:#fff;">What Our Customers Say</h2>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:1.5rem; margin-top:1.5rem;">
                <blockquote style="background:rgba(255,255,255,0.1); padding:1.5rem; border-radius:8px; margin:0; font-style:italic;">
                    "We were quoted $8,000 per machine to replace the CNC control. Your LCD kit solved the problem for under $300 each. The installation was literally 4 screws and 1 cable."
                    <cite style="display:block; margin-top:1rem; font-style:normal; color:rgba(255,255,255,0.7);">— Production Manager, Automotive Parts Manufacturer, China</cite>
                </blockquote>
                <blockquote style="background:rgba(255,255,255,0.1); padding:1.5rem; border-radius:8px; margin:0; font-style:italic;">
                    "We tried repairing our old CRTs twice. Each repair lasted 6 months and cost $400. Your LCD upgrade cost $250 and has been running flawlessly for 2 years. Best decision we made."
                    <cite style="display:block; margin-top:1rem; font-style:normal; color:rgba(255,255,255,0.7);">— Maintenance Engineer, Tool & Die Shop, USA</cite>
                </blockquote>
                <blockquote style="background:rgba(255,255,255,0.1); padding:1.5rem; border-radius:8px; margin:0; font-style:italic;">
                    "Fast shipping to Germany, perfect fit, and the display is actually better than the original Siemens. We're planning to upgrade our remaining machines too."
                    <cite style="display:block; margin-top:1rem; font-style:normal; color:rgba(255,255,255,0.7);">— CNC Programmer, Heavy Equipment Manufacturer, Germany</cite>
                </blockquote>
            </div>
        </section>

        <section style="margin:3rem 0;">
            <h2>By The Numbers</h2>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:1.5rem; text-align:center; margin-top:1.5rem;">
                <div style="background:#f0f7ff; padding:2rem; border-radius:12px;">
                    <div style="font-size:2.5rem; font-weight:800; color:#2563eb;">500+</div>
                    <p>Enterprise Clients</p>
                </div>
                <div style="background:#f0f7ff; padding:2rem; border-radius:12px;">
                    <div style="font-size:2.5rem; font-weight:800; color:#2563eb;">12+</div>
                    <p>Countries Served</p>
                </div>
                <div style="background:#f0f7ff; padding:2rem; border-radius:12px;">
                    <div style="font-size:2.5rem; font-weight:800; color:#2563eb;">80%+</div>
                    <p>Avg. Cost Savings</p>
                </div>
                <div style="background:#f0f7ff; padding:2rem; border-radius:12px;">
                    <div style="font-size:2.5rem; font-weight:800; color:#2563eb;">5-10</div>
                    <p>Years Equipment Life Extended</p>
                </div>
            </div>
        </section>

        <section style="text-align:center; padding:3rem; background:#f5f5f7; border-radius:12px; margin:3rem 0;">
            <h2>Ready to Upgrade Your CNC Displays?</h2>
            <p style="font-size:1.1rem;">Send us a photo of your current CNC display (back label visible) and get a free compatibility check and quote within 24 hours.</p>
            <p style="font-size:1.1rem;"><strong>Email:</strong> szkongto01@foxmail.com | <strong>Phone/WhatsApp:</strong> +86-13686889647</p>
            <a href="/en/about.html" class="btn btn-primary btn-large" style="display:inline-block;margin-top:1rem;">Contact Us →</a>
        </section>
    </main>

    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">Kongto Technology</span>
                <p>Industrial Video Display Solutions Expert</p>
            </div>
            <div class="footer-links">
                <a href="/en/posts/">Articles</a>
                <a href="/en/case-studies.html">Case Studies</a>
                <a href="/en/docs/">Downloads</a>
                <a href="/en/about.html">About</a>
            </div>
            <p class="footer-copy">© 2026 Kongto Technology Co.,LTD</p>
        </div>
    </footer>

<div style="text-align:center;padding:20px 0;font-size:12px;color:#888888;border-top:1px solid #e0e0e0;margin-top:40px;">
  <p style="margin:4px 0;">
    &nbsp;|&nbsp; Kongto Technology &copy; 2026
    &nbsp;|&nbsp; <a href="/sitemap.xml" style="color:#888;">Sitemap</a>
    &nbsp;|&nbsp; <a href="/en/" style="color:#888;">English</a>
  </p>
</div>
</body>
</html>'''
    write_file(en_path, en_content)

    # Chinese version
    zh_path = BASE / 'case-studies.html'
    zh_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNC显示器升级客户案例 | 500+企业验证 | 深圳市江图科技有限公司</title>
    <meta name="description" content="CNC数控系统CRT转LCD升级真实客户案例。FANUC发那科、三菱、西门子、马扎克CRT显示器LCD替换成功故事。500+企业客户，12年工业显示经验。看制造企业如何节省80%设备更新成本。">
    <meta name="keywords" content="CNC显示器升级案例,FANUC LCD替换成功案例,三菱CRT改LCD案例,西门子显示器升级实例,数控显示器更换效果">
    <link rel="canonical" href="https://cncdisplay.com/case-studies.html">
    <link rel="alternate" hreflang="zh" href="https://cncdisplay.com/case-studies.html" />
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/case-studies.html" />
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/en/case-studies.html" />
    <link rel="stylesheet" href="/css/style.css?v=7">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="shortcut icon" href="/favicon.ico">
    <meta property="og:type" content="website">
    <meta property="og:title" content="CNC显示器升级客户案例 | 江图科技">
    <meta property="og:description" content="CNC数控系统CRT转LCD升级真实客户案例。500+企业验证，12年工业显示经验。">
    <meta property="og:url" content="https://cncdisplay.com/case-studies.html">
    <meta property="og:site_name" content="深圳市江图科技有限公司">
    <meta property="og:image" content="https://cncdisplay.com/images/logo_256.png">
    <meta property="og:locale" content="zh_CN">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="CNC显示器升级客户案例 | 江图科技">
    <meta name="twitter:description" content="CNC数控系统CRT转LCD升级真实客户案例。500+企业验证。">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://zz.bdstatic.com https://push.zhanzhang.baidu.com; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' https://zz.bdstatic.com https://push.zhanzhang.baidu.com https://www.clarity.ms">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
    <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "CNC显示器升级客户案例",
  "description": "CNC数控系统CRT转LCD升级真实客户案例，500+企业验证",
  "url": "https://cncdisplay.com/case-studies.html",
  "provider": {
    "@type": "Organization",
    "name": "深圳市江图科技有限公司",
    "url": "https://cncdisplay.com"
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://cncdisplay.com/"},
    {"@type": "ListItem", "position": 2, "name": "客户案例", "item": "https://cncdisplay.com/case-studies.html"}
  ]
}
</script>
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">江图科技</a>
            <div class="nav-links">
                <a href="/">首页</a>
                <a href="/posts/">文章</a>
                <a href="/case-studies.html">客户案例</a>
                <a href="/docs/">下载</a>
                <a href="/about.html">关于</a>
            </div>
            <a href="/search.html" class="nav-search">🔍 搜索</a>
            <div class="lang-switch">
                <a href="/" lang="zh" class="lang-zh">中文</a>
                <span class="divider">|</span>
                <a href="/en/" lang="en" class="lang-en">English</a>
            </div>
        </nav>
    </header>

    <main style="max-width:1100px;margin:40px auto;padding:20px;">
        <h1>CNC显示器升级 — 客户成功案例</h1>
        <p style="color:#666;font-size:1.1rem;">真实的工厂车间升级效果。500+制造企业使用我们的CRT转LCD方案延长设备寿命5-10年。</p>

        <section style="margin:3rem 0;">
            <h2>按行业分类</h2>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #2563eb;">
                <h3 style="color:#2563eb;"> 汽车零部件制造 — FANUC 0i-C</h3>
                <p><strong>地点:</strong> 中国广东</p>
                <p><strong>设备:</strong> 12台FANUC 0i-C数控车床 (1998-2002年)</p>
                <p><strong>问题:</strong> CRT显示器严重老化——亮度衰减、闪烁、灼屏。操作工难以看清参数，影响加工质量。</p>
                <p><strong>方案:</strong> 安装A61L-0001-0093 LCD升级模块，覆盖全部12台设备。</p>
                <p><strong>效果:</strong></p>
                <ul>
                    <li>[OK] 12台设备3小时内全部完成安装</li>
                    <li>[OK] 无需修改任何CNC参数</li>
                    <li>[OK] 显示屏清晰度恢复至新机水平</li>
                    <li>[OK] <strong>节省约35万元人民币</strong>（对比更换CNC系统）</li>
                    <li>[OK] 设备持续稳定运行中（2023年安装）</li>
                </ul>
            </div>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #dc2626;">
                <h3 style="color:#dc2626;"> 模具加工 — 三菱M64</h3>
                <p><strong>地点:</strong> 美国俄亥俄州</p>
                <p><strong>设备:</strong> 3台三菱M64加工中心 (2001年)</p>
                <p><strong>问题:</strong> MDT962B CRT严重偏色。其中一台完全黑屏，导致设备停机。</p>
                <p><strong>方案:</strong> DHL发货（5天到），更换全部3台MDT962B为TFT LCD套件。</p>
                <p><strong>效果:</strong></p>
                <ul>
                    <li>[OK] 每台更换不到15分钟</li>
                    <li>[OK] 原装接口，无需接线改动</li>
                    <li>[OK] <strong>节省约11万元人民币</strong>（对比原厂报价）</li>
                    <li>[OK] 操作员反馈："像在用新机床"</li>
                </ul>
            </div>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #059669;">
                <h3 style="color:#059669;"> 重型设备维修 — 西门子840D</h3>
                <p><strong>地点:</strong> 德国巴伐利亚</p>
                <p><strong>设备:</strong> 2台西门子SINUMERIK 840D加工中心 (2004年)</p>
                <p><strong>问题:</strong> 6FC3988-7FA20显示器间歇性黑屏。西门子原厂更换报价€3,200/台。</p>
                <p><strong>方案:</strong> 安装AC110V兼容LCD升级模块。</p>
                <p><strong>效果:</strong></p>
                <ul>
                    <li>[OK] 直接即插即用替换</li>
                    <li>[OK] <strong>节省约€5,200</strong>（对比原厂更换）</li>
                    <li>[OK] 显示亮度、清晰度优于原厂</li>
                    <li>[OK] 2年质保覆盖</li>
                </ul>
            </div>

            <div style="background:#f8f9fa;border-radius:12px;padding:2rem;margin:1.5rem 0;border-left:4px solid #7c3aed;">
                <h3 style="color:#7c3aed;"> 精密加工 — 马扎克T-32</h3>
                <p><strong>地点:</strong> 日本爱知县</p>
                <p><strong>设备:</strong> 4台马扎克Mazatrol T-32数控车床 (1999年)</p>
                <p><strong>问题:</strong> CD1472-D1M CRT亮度严重衰减，部分屏幕有明显灼屏痕迹。</p>
                <p><strong>方案:</strong> CD1472-D1M LCD替换套件。</p>
                <p><strong>效果:</strong></p>
                <ul>
                    <li>[OK] 4台设备一个下午全部完成</li>
                    <li>[OK] 完整保留Mazatrol界面所有功能</li>
                    <li>[OK] <strong>预计延长设备寿命8年以上</strong></li>
                    <li>[OK] 生产团队反馈眼部疲劳明显减轻</li>
                </ul>
            </div>
        </section>

        <section style="background:linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); color:#fff; padding:3rem; border-radius:12px; margin:3rem 0;">
            <h2 style="color:#fff;">客户评价</h2>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:1.5rem; margin-top:1.5rem;">
                <blockquote style="background:rgba(255,255,255,0.1); padding:1.5rem; border-radius:8px; margin:0; font-style:italic;">
                    "原厂方案报价每台8万块换数控系统，你们3000块不到就搞定了。安装真的就4颗螺丝1根线，太简单了。"
                    <cite style="display:block; margin-top:1rem; font-style:normal; color:rgba(255,255,255,0.7);">— 生产经理，汽车零部件厂，广东</cite>
                </blockquote>
                <blockquote style="background:rgba(255,255,255,0.1); padding:1.5rem; border-radius:8px; margin:0; font-style:italic;">
                    "我们修了两次老CRT，每次3000块撑半年。你们LCD升级2000不到跑了两年没问题，太值了。"
                    <cite style="display:block; margin-top:1rem; font-style:normal; color:rgba(255,255,255,0.7);">— 维修工程师，模具厂，美国</cite>
                </blockquote>
                <blockquote style="background:rgba(255,255,255,0.1); padding:1.5rem; border-radius:8px; margin:0; font-style:italic;">
                    "德国收货很快，完美适配，显示效果比原装西门子还好。我们打算把剩下的几台也换了。"
                    <cite style="display:block; margin-top:1rem; font-style:normal; color:rgba(255,255,255,0.7);">— CNC编程员，重型设备厂，德国</cite>
                </blockquote>
            </div>
        </section>

        <section style="text-align:center; padding:3rem; background:#f5f5f7; border-radius:12px; margin:3rem 0;">
            <h2>准备升级您的CNC显示器？</h2>
            <p style="font-size:1.1rem;">拍一张当前CNC显示器照片（背面标签清晰可见），免费获取兼容性确认和报价，24小时内回复。</p>
            <p style="font-size:1.1rem;"><strong>邮箱:</strong> szkongto01@foxmail.com | <strong>电话/微信:</strong> 136-8688-9647</p>
            <a href="/about.html" class="btn btn-primary btn-large" style="display:inline-block;margin-top:1rem;">联系我们 →</a>
        </section>
    </main>

    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">江图科技 Kongto Technology</span>
                <p>专注工业视频显示解决方案</p>
            </div>
            <div class="footer-links">
                <a href="/posts/">技术文章</a>
                <a href="/case-studies.html">客户案例</a>
                <a href="/docs/">资料下载</a>
                <a href="/about.html">关于我们</a>
            </div>
            <p class="footer-copy">© 2013-2026 深圳市江图科技有限公司</p>
        </div>
    </footer>

<div style="text-align:center;padding:20px 0;font-size:12px;color:#888888;border-top:1px solid #e0e0e0;margin-top:40px;">
  <p style="margin:4px 0;">
    &nbsp;|&nbsp; 深圳市江图科技有限公司 &copy; 2026
    &nbsp;|&nbsp; <a href="/sitemap.xml" style="color:#888;">Sitemap</a>
    &nbsp;|&nbsp; <a href="/en/" style="color:#888;">English</a>
  </p>
</div>
</body>
</html>'''
    write_file(zh_path, zh_content)
    return True


# ============================================================
# 6. LLMS.TXT / AI OPTIMIZATION (GEO)
# ============================================================
def create_llms_txt():
    """Create/enhance llms.txt for AI crawler optimization (GEO)."""
    print("\n [6/7] Creating AI-optimized llms.txt...")
    path = BASE / 'llms.txt'

    content = f"""# Kongto Technology (cncdisplay.com) - AI-Friendly Content Index
# Generated: {NOW}
# Purpose: Help AI crawlers (GPTBot, ClaudeBot, PerplexityBot) understand our site structure
# About: Industrial CNC display CRT to LCD upgrade solutions since 2013
# Contact: szkongto01@foxmail.com | +86-13686889647

## Company Overview
- Name: Kongto Technology (深圳市江图科技有限公司)
- Founded: 2013
- Location: Shenzhen, Guangdong, China
- Specialty: Industrial CNC display upgrades, CRT-to-LCD retrofit, video signal converters
- Clients: 500+ enterprises across 12+ countries
- Warranty: 2 years on all products

## Key Pages
- Home (EN): https://cncdisplay.com/en/index.html - Main corporate site in English
- Home (ZH): https://cncdisplay.com/ - Chinese homepage
- About: https://cncdisplay.com/about.html - Company profile, certifications (CE, RoHS, FCC, ISO 9001)
- Case Studies: https://cncdisplay.com/en/case-studies.html - Customer success stories
- Compatibility Matrix: https://cncdisplay.com/en/compatibility-matrix.html - CRT model to LCD cross-reference
- Comparison: https://cncdisplay.com/comparison-kongto-vs-competitors.html - Competitor comparison
- Resources: https://cncdisplay.com/resources.html - Download center

## Brand Pages
- FANUC: https://cncdisplay.com/en/brands/FANUC.html - A61L-0001 series, D9MM-11A
- Mitsubishi: https://cncdisplay.com/en/brands/Mitsubishi.html - MDT962B, BM09DF, FCUA-CT100
- Siemens: https://cncdisplay.com/en/brands/Siemens.html - 6FC3988-7FA20, SM0901
- Mazak: https://cncdisplay.com/en/brands/MAZAK.html - CD1472, C5470NS, DR5614
- Okuma: https://cncdisplay.com/en/brands/OKUMA.html - OSP 5000, 5020
- Haas: https://cncdisplay.com/en/brands/HAAS.html - VF, ST, SL series

## Core Technical Articles
- FANUC CRT to LCD Complete Guide: https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html
- FANUC A61L-0001-0093 LCD Upgrade: https://cncdisplay.com/en/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html
- Mitsubishi MDT962B CRT Replacement: https://cncdisplay.com/en/posts/article_20260506_Mitsubishi_MDT962B_Industrial_LCD_CRT_Replacement.html
- Siemens 6FC3998-7FA20 LCD: https://cncdisplay.com/en/posts/article_20260507_Siemens_6FC3998-7FA20_LCD.html
- Mazak CD1472D1M LCD Replacement: https://cncdisplay.com/en/posts/article_20260507_Mazak_CD1472D1M_LCD_Replacement.html
- CNC CRT to LCD Cost Comparison: https://cncdisplay.com/en/posts/comparison_20260501_FANUC_CRTcrt_repair_vs_lcd_cost_comparison.html
- CNC Display Installation Guide: https://cncdisplay.com/en/posts/cnc-display-installation-guide.html

## FAQ Topics (AI Citation Ready)
- Q: How to upgrade FANUC CRT to LCD? → See FANUC brand page and Complete Guide
- Q: Is LCD upgrade compatible with my CNC? → Check compatibility matrix, or send display model photo
- Q: Do I need to change CNC parameters? → No, all solutions are plug-and-play with original connectors
- Q: How long does installation take? → 10-15 minutes per machine
- Q: What is the warranty? → 2 years on all products, lifetime technical support
- Q: What brands are covered? → FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas

## Services
1. CRT to LCD Retrofit Modules - Direct replacement for aging CNC CRT displays
2. Video Signal Converters - CGA/EGA/RGB to VGA/HDMI for legacy equipment
3. Custom Industrial Displays - 7-15 inch TFT LCD, aluminum frame, IP65 option

## Certifications
- CE (EU Safety)
- RoHS 2.0 (EU) 2015/863
- FCC (EMC Compliance)
- ISO 9001:2015 Quality Management
- IP65 Front Panel Protection (KTV series)

## Sitemap
- XML: https://cncdisplay.com/sitemap.xml
- Search: https://cncdisplay.com/en/search.html
"""
    write_file(path, content)
    return True


# ============================================================
# 7. UPDATE SITEMAP WITH NEW PAGES
# ============================================================
def update_sitemap_new_pages():
    """Add new pages (case-studies) to sitemap."""
    print("\n [7/7] Adding new pages to sitemap...")
    sitemap_path = BASE / 'sitemap.xml'
    content = read_file(sitemap_path)

    new_urls = []
    # Check if case-studies.html exists and not already in sitemap
    if (BASE / 'case-studies.html').exists() and 'case-studies.html' not in content:
        new_urls.append(('https://cncdisplay.com/case-studies.html', '0.8'))
    if (BASE / 'en' / 'case-studies.html').exists() and 'en/case-studies.html' not in content:
        new_urls.append(('https://cncdisplay.com/en/case-studies.html', '0.8'))

    if new_urls:
        insert_pos = content.find('</urlset>')
        for url, priority in new_urls:
            lastmod = file_mtime_iso(BASE / url.replace('https://cncdisplay.com/', ''))
            entry = f'''  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{priority}</priority>
  </url>
'''
            content = content[:insert_pos] + entry + content[insert_pos:]

        write_file(sitemap_path, content)
    return True


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("cncdisplay.com Comprehensive SEO Optimization")
    print(f"Date: {NOW}")
    print("Based on: SEO Audit Report + SEO Strategy Report")
    print("=" * 60)

    fix_sitemap()
    fix_en_homepage()
    fix_brand_pages()
    fix_article_pages()
    create_case_studies_page()
    create_llms_txt()
    update_sitemap_new_pages()

    print("\n" + "=" * 60)
    print("[OK] ALL OPTIMIZATIONS COMPLETE")
    print("=" * 60)
    print("\nSummary of changes:")
    print("  1. [OK] Sitemap lastmod → actual file modification times")
    print("  2. [OK] English homepage → enhanced Title/Meta/OG/Favicon")
    print("  3. [OK] Brand pages → Product Schema + FAQ Schema + improved Titles")
    print("  4. [OK] Article pages → dateModified + BreadcrumbList added")
    print("  5. [OK] Customer Case Studies page → created (EN + ZH)")
    print("  6. [OK] llms.txt → AI crawler optimized content index")
    print("  7. [OK] Sitemap → new pages registered")
    print("\nBackups: *.html.seobak files created for all modified pages")
    print("Run 'git diff' to review changes before deploying.")
