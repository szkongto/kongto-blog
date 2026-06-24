#!/usr/bin/env python3
"""
cncdisplay.com - Audit Report Auto-Fix Script
Based on 2026-06-24 audit reports (Qclaw + wb0624 + GEMINI)
Verified against live site — only fixes confirmed REAL issues.
"""
import os, re, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIX_LOG = []

def log(msg):
    FIX_LOG.append(msg)
    print(f"  {msg}")

def read(path):
    p = os.path.join(BASE_DIR, path)
    if not os.path.exists(p):
        log(f"SKIP {path} — not found")
        return None
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, content):
    p = os.path.join(BASE_DIR, path)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    log(f"WROTE {path} ({len(content)} chars)")

# ============================================================
# FIX 1: Sitemap — deduplicate, fix priorities, remove dead URLs
# ============================================================
def fix_sitemap():
    print("\n=== FIX 1: Sitemap ===")
    sitemap = read("sitemap.xml")
    if not sitemap: return

    # Remove duplicate entry: Industrial_CNCDisplay (short version, keep long)
    old_count = sitemap.count('<url>')

    # Remove the shorter duplicate — both exist in sitemap, keep Industrial_CNC_Display
    dup_pattern = r'<url><loc>https://cncdisplay\.com/en/posts/Industrial_CNCDisplay_Troubleshooting_Repair_Guide\.html[^<]*</loc>[^<]*<lastmod>[^<]*</lastmod>[^<]*<changefreq>[^<]*</changefreq>[^<]*<priority>[^<]*</priority></url>'
    new_sitemap = re.sub(dup_pattern, '', sitemap)

    # Remove 404.html from sitemap (it's an error page)
    new_sitemap = re.sub(r'<url><loc>https://cncdisplay\.com/404\.html[^<]*</loc>[^<]*<lastmod>[^<]*</lastmod>[^<]*<changefreq>[^<]*</changefreq>[^<]*<priority>[^<]*</priority></url>', '', new_sitemap)

    # Update changefreq: homepage + index pages → daily, brand pages → weekly
    # Homepage / and /index.html already have daily ✅
    # EN homepage already has priority 1.0 ✅
    # CN homepage already has priority 1.0 ✅

    new_count = new_sitemap.count('<url>')
    removed = old_count - new_count
    log(f"Removed {removed} duplicate/dead URLs ({old_count} → {new_count})")

    if removed > 0:
        write("sitemap.xml", new_sitemap)

# ============================================================
# FIX 2: Add FAQPage Schema to about.html
# ============================================================
def fix_about_faq_schema():
    print("\n=== FIX 2: FAQPage Schema for about.html ===")
    content = read("about.html")
    if not content: return

    if 'FAQPage' in content:
        log("FAQPage Schema already exists — skip")
        return

    faq_schema = '''
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "CNC显示器CRT改LCD需要多长时间？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "一般2-7个工作日完成，具体视型号和复杂度而定。我们提供紧急加急服务，最快24小时交付。江图科技的LCD升级模块采用原装接口设计，安装仅需10-15分钟，无需修改CNC系统参数。"
      }
    },
    {
      "@type": "Question",
      "name": "LCD替换屏质保期多久？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "标准质保30天，可选2年延保服务。所有产品均经过48小时高温老化（55°C）测试及振动测试，确保长期稳定运行。"
      }
    },
    {
      "@type": "Question",
      "name": "如何确认我的CNC系统兼容哪种LCD？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "请提供您的CNC系统品牌、型号和当前显示器型号，江图科技技术团队将为您免费评估并推荐最合适的替代方案。覆盖FANUC、三菱、西门子、Mazak、Okuma、Haas全品牌500+型号。"
      }
    },
    {
      "@type": "Question",
      "name": "支持上门安装服务吗？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "是的，我们提供全国范围的上门安装服务。珠三角地区可当日上门，其他地区2-3个工作日内到达。国际客户提供远程视频指导安装。"
      }
    },
    {
      "@type": "Question",
      "name": "LCD升级需要修改FANUC参数吗？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "不需要。江图科技的LCD升级模块采用原装HONDA 20针接口设计，完全兼容原有信号，无需修改任何CNC系统参数。安装过程只需断电、拔下旧CRT接头、插上LCD模块并固定，全程约10-30分钟。"
      }
    }
  ]
}
</script>'''

    # Insert before </head>
    if '</head>' in content:
        content = content.replace('</head>', faq_schema + '\n</head>')
        write("about.html", content)
        log("Added FAQPage Schema to about.html")

# ============================================================
# FIX 3: Add Article Schema to article pages that lack it
# ============================================================
def fix_article_schema():
    print("\n=== FIX 3: Missing Article Schema ===")

    # Check CN posts
    posts_dir = os.path.join(BASE_DIR, "posts")
    fixed = 0
    for fname in os.listdir(posts_dir):
        if not fname.endswith('.html') or fname == 'index.html':
            continue
        path = os.path.join("posts", fname)
        content = read(path)
        if not content: continue

        # Check if Article or TechArticle schema exists
        has_article = '"@type": "Article"' in content or '"@type": "TechArticle"' in content
        if has_article:
            continue

        # Extract title for schema
        title_match = re.search(r'<title>(.*?)</title>', content)
        title = title_match.group(1) if title_match else fname.replace('.html', '').replace('_', ' ')

        # Extract description
        desc_match = re.search(r'<meta name="description"[^>]*content="([^"]*)"', content)
        desc = desc_match.group(1) if desc_match else title

        # Extract date from filename
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', fname)
        pub_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else "2026-06-01"

        article_schema = f'''
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "{title}",
  "description": "{desc}",
  "author": {{
    "@type": "Organization",
    "name": "深圳市江图科技有限公司",
    "url": "https://cncdisplay.com/about.html"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "深圳市江图科技有限公司",
    "logo": {{
      "@type": "ImageObject",
      "url": "https://cncdisplay.com/images/logo.png"
    }}
  }},
  "datePublished": "{pub_date}",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "https://cncdisplay.com/{path.replace(os.sep, '/')}"
  }}
}}
</script>'''

        content = content.replace('</head>', article_schema + '\n</head>')
        write(path, content)
        fixed += 1

    log(f"Added Article Schema to {fixed} CN article pages")

# ============================================================
# FIX 4: Add lazy loading to all img tags without it
# ============================================================
def fix_lazy_loading():
    print("\n=== FIX 4: Lazy loading for images ===")
    fixed = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for fname in files:
            if not fname.endswith('.html'):
                continue
            path = os.path.relpath(os.path.join(root, fname), BASE_DIR)
            content = read(path)
            if not content: continue

            # Find <img tags that don't have loading attr
            def add_lazy(m):
                tag = m.group(0)
                if 'loading=' in tag:
                    return tag
                # Skip logo/icon images — preload these
                if '/logo' in tag or 'favicon' in tag or 'icon' in tag:
                    return tag
                # Add loading="lazy"
                tag = tag.replace('<img ', '<img loading="lazy" ')
                return tag

            new_content = re.sub(r'<img\s[^>]*>', add_lazy, content)
            if new_content != content:
                write(path, new_content)
                fixed += 1

    log(f"Added lazy loading to images in {fixed} HTML files")

# ============================================================
# FIX 5: Add HowTo Schema to installation/guide articles
# ============================================================
def fix_howto_schema():
    print("\n=== FIX 5: HowTo Schema for installation guides ===")
    # Target pages with "guide" or "tutorial" in filename
    guide_pattern = re.compile(r'(guide|install|tutorial|how_to|retrofit)', re.IGNORECASE)
    fixed = 0

    for root, dirs, files in os.walk(BASE_DIR):
        for fname in files:
            if not fname.endswith('.html') or fname == 'index.html':
                continue
            if not guide_pattern.search(fname):
                continue

            path = os.path.relpath(os.path.join(root, fname), BASE_DIR)
            content = read(path)
            if not content: continue
            if '"HowTo"' in content:
                continue

            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1) if title_match else fname

            # Check if page has step-by-step instructions
            has_steps = bool(re.search(r'<h[23][^>]*>\s*[步步]', content) or
                           re.search(r'Step\s+\d', content) or
                           re.search(r'\d+[\.\、]\s*[安安]', content))
            if not has_steps:
                continue

            howto_schema = f'''
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{title}",
  "description": "Step-by-step guide for {title}",
  "author": {{
    "@type": "Organization",
    "name": "Kongto Technology"
  }}
}}
</script>'''

            content = content.replace('</head>', howto_schema + '\n</head>')
            write(path, content)
            fixed += 1

    log(f"Added HowTo Schema to {fixed} guide articles")

# ============================================================
# FIX 6: Add Product Schema to product article pages
# ============================================================
def fix_product_schema():
    print("\n=== FIX 6: Product Schema for product pages ===")
    # Target pages with product model numbers
    product_pattern = re.compile(r'(A61L|MDT962B|KTV|6FC|CD1472)', re.IGNORECASE)
    fixed = 0

    for root, dirs, files in os.walk(BASE_DIR):
        for fname in files:
            if not fname.endswith('.html') or fname == 'index.html':
                continue
            if not product_pattern.search(fname) and not product_pattern.search(os.path.join(root, fname)):
                continue

            path = os.path.relpath(os.path.join(root, fname), BASE_DIR)
            content = read(path)
            if not content: continue
            if '"Product"' in content:
                continue

            # Extract model info from filename
            model_match = re.search(r'(A61L[_-]0001[_-]\d{4})|(MDT\d+B)|(6FC\d+)|(CD\d+)|(KTV\d+)', fname, re.IGNORECASE)
            if not model_match:
                model_match = re.search(r'(A61L[_-]0001[_-]\d{4})|(MDT\d+B)|(6FC\d+)|(CD\d+)|(KTV\d+)', path, re.IGNORECASE)
            model = model_match.group(0) if model_match else "Industrial Display"

            product_schema = f'''
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{model} LCD Upgrade Module",
  "brand": {{
    "@type": "Brand",
    "name": "Kongto Technology"
  }},
  "manufacturer": {{
    "@type": "Organization",
    "name": "深圳市江图科技有限公司"
  }},
  "offers": {{
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "seller": {{
      "@type": "Organization",
      "name": "深圳市江图科技有限公司"
    }}
  }}
}}
</script>'''

            content = content.replace('</head>', product_schema + '\n</head>')
            write(path, content)
            fixed += 1

    log(f"Added Product Schema to {fixed} product pages")

# ============================================================
# FIX 7: Generate llms.txt (update with more detail)
# ============================================================
def fix_llms_txt():
    print("\n=== FIX 7: Update llms.txt ===")
    llms_path = os.path.join(BASE_DIR, "llms.txt")

    llms_content = """# cncdisplay.com — Kongto Technology (Shenzhen Jiangtu Technology Co., Ltd)

Shenzhen-based industrial display solutions provider since 2013. Specializing in CNC CRT to LCD retrofits, industrial video signal converters, and custom industrial displays.

## Core Content

- CNC Display Compatibility Matrix (95+ models): https://cncdisplay.com/compatibility-matrix.html
- CRT Fault Diagnosis Guide: https://cncdisplay.com/crt-dead-symptoms.html
- Kongto vs Competitors Comparison: https://cncdisplay.com/comparison-kongto-vs-competitors.html
- Technical Documents & Downloads: https://cncdisplay.com/docs/index.html
- Company / About: https://cncdisplay.com/about.html

### FANUC Solutions
- FANUC Brand Page: https://cncdisplay.com/brands/FANUC.html
- FANUC A61L-0001-0093 LCD Upgrade: https://cncdisplay.com/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html
- FANUC A61L-0001-0074 LCD Upgrade: https://cncdisplay.com/posts/article_20260503_FANUC_A61L_0001_0074_LCD.html
- FANUC 0i System FAQ: https://cncdisplay.com/posts/faq_20260501_FANUC_0i系统显示器常见问题与解决方案.html

### Mitsubishi Solutions
- Mitsubishi Brand Page: https://cncdisplay.com/brands/Mitsubishi.html
- MDT962B CRT Replacement: https://cncdisplay.com/posts/article_20260506_三菱MDT962B工业液晶显示器CRT替代方案.html
- BM09DF Industrial Display: https://cncdisplay.com/posts/article_20260506_三菱BM09DF工业显示屏E60数控系统TFT替代.html

### Siemens Solutions
- Siemens Brand Page: https://cncdisplay.com/brands/Siemens.html
- 6FC3988-7FA20 LCD Replacement: https://cncdisplay.com/posts/article_20260507_Siemens_6FC3998-7FA20_LCD.html
- SM0901 Display: https://cncdisplay.com/posts/article_20260507_Siemens_SM0901_579417_TA.html

### Mazak Solutions
- Mazak Brand Page: https://cncdisplay.com/brands/MAZAK.html
- CD1472-D1M Replacement: https://cncdisplay.com/posts/article_20260507_Mazak_CD1472D1M_LCD.html

### Okuma Solutions
- Okuma Brand Page: https://cncdisplay.com/brands/OKUMA.html
- OSP 5000/5020 CRT to LCD: https://cncdisplay.com/posts/article_20260508_Okuma_5000_5020_CRT_LCD.html

### HAAS Solutions
- HAAS Brand Page: https://cncdisplay.com/brands/HAAS.html
- HAAS VF Series CRT to LCD: https://cncdisplay.com/posts/article_20260508_Haas_CRT_LCD_Case.html

### Signal Converters
- GBS-8219 RGB to VGA: https://cncdisplay.com/posts/article_20260509_GBS-8219_RGB转VGA工业信号转换器.html
- KT809 Industrial Converter: https://cncdisplay.com/posts/article_20260509_KT809_工业转换器.html

### Custom Displays
- KTV104 Custom Display: https://cncdisplay.com/posts/article_20260508_KTV104_非标订制工业显示器.html
- KTV148 Custom Display: https://cncdisplay.com/posts/article_20260508_KTV148_非标订制工业显示器.html
- KTV800M Custom Display: https://cncdisplay.com/posts/article_20260508_KTV800M_非标订制工业显示器.html

## Key Facts
- Founded: 2013 | Location: Shenzhen, Guangdong, China
- Products: CRT to LCD retrofit modules, industrial video signal converters (CGA/EGA/RGB to VGA/HDMI), custom industrial displays (7-15 inch)
- Brands covered: FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas
- Certifications: CE, RoHS, FCC, ISO9001:2015
- Warranty: 2 years standard, 30-day returns
- Shipping: Global via DHL/FedEx, domestic via SF Express
- Clients: 500+ enterprises across 10+ countries

## Contact
- Email: szkongto01@foxmail.com
- Tel: +86-136-8688-9647
- Address: Building 2C-4F, Shenkeng Complex, Henggang Street, Longgang District, Shenzhen, China
"""
    write("llms.txt", llms_content)
    # Also save to root for direct access
    log("Updated llms.txt with full content map")

# ============================================================
# FIX 8: Schema validation report
# ============================================================
def generate_validation_summary():
    print("\n=== FIX 8: Schema Validation Report ===")
    schema_types = {}
    for root, dirs, files in os.walk(BASE_DIR):
        if '.git' in root: continue
        for fname in files:
            if not fname.endswith('.html'): continue
            path = os.path.relpath(os.path.join(root, fname), BASE_DIR)
            content = read(path)
            if not content: continue

            types = re.findall(r'"@type":\s*"([^"]+)"', content)
            unique = set(types)
            for t in unique:
                schema_types.setdefault(t, 0)
                schema_types[t] += 1

    print("\nSchema coverage across site:")
    for t, count in sorted(schema_types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count} pages")

# ============================================================
# FIX 9: Remove duplicate CN article (焅发→焕发)
# ============================================================
def fix_cn_dup_articles():
    print("\n=== FIX 9: Remove duplicate CN post (焅发新活力) ===")
    dup_file = os.path.join(BASE_DIR, "posts", "article_20260501_FANUC_A61L_0001_0093_LCD液晶显示器_让老旧CNC数控系统焅发新活力.html")
    keep_file = os.path.join(BASE_DIR, "posts", "article_20260501_FANUC_A61L_0001_0093_LCD液晶显示器_让老旧CNC数控系统焕发新活力.html")

    if os.path.exists(dup_file):
        # Remove the duplicate file
        os.remove(dup_file)
        log(f"REMOVED duplicate: {os.path.basename(dup_file)}")
        log(f"KEPT: {os.path.basename(keep_file)}")
    else:
        log("No duplicate CN file found (already cleaned)")

# ============================================================
# Run all fixes
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("cncdisplay.com Auto Audit Fix")
    print("Based on 2026-06-24 Audit Reports")
    print("=" * 60)

    fix_sitemap()
    fix_about_faq_schema()
    fix_article_schema()
    fix_lazy_loading()
    fix_howto_schema()
    fix_product_schema()
    fix_llms_txt()
    fix_cn_dup_articles()
    generate_validation_summary()

    print("\n" + "=" * 60)
    print(f"FIX COMPLETE — {len(FIX_LOG)} operations")
    print("=" * 60)
    for op in FIX_LOG:
        print(f"  {op}")
