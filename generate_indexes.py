#!/usr/bin/env python3
"""Auto-generate posts/index.html and en/posts/index.html from filesystem."""
import os, re
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

# Category definitions with keywords
CN_CATEGORIES = [
    ("fanuc", "FANUC 发那科 显示器 LCD 升级方案", ["FANUC", "A61L", "D9MM", "0i系统"]),
    ("mazak", "马扎克 Mazak / 夏普 Sharp 显示器替代方案", ["Mazak", "CD1472", "C5470", "DR5614", "Sharp"]),
    ("okuma", "大隈 Okuma 显示器替代方案", ["Okuma", "5000", "5020"]),
    ("haas", "哈斯 Haas 显示器替代方案", ["Haas"]),
    ("siemens", "西门子 Siemens 显示器替代方案", ["Siemens", "SM0901", "6FC3988"]),
    ("mitsu", "三菱 Mitsubishi 工业显示器替代方案", ["Mitsubishi", "MDT1283", "MDT962", "BM09DF", "FCUA", "三菱"]),
    ("ktv", "非标 KTV 系列 订制工业显示器", ["KTV"]),
    ("conv", "工业视频信号转换器", ["GBS", "KT809", "KT819"]),
    ("guide", "技术指南与方案", ["CGA", "EGA", "RGBHV", "工业数控", "工业显示器RGBHV",
     "工业视频显示在智能工厂", "工业视频信号转换器系列", "工业视频信号转换器在CNC",
     "江图科技工业视频显示产品目录"]),
    ("comp", "技术对比分析", ["comparison", "选购指南"]),
    ("faq", "常见问题 FAQ", ["faq"]),
    ("news", "新闻动态", ["press_release", "social"]),
]

EN_CATEGORIES = [
    ("fanuc", "FANUC CNC Display LCD Upgrade Solutions", ["FANUC", "A61L", "D9MM"]),
    ("mazak", "Mazak / Sharp / Mitsubishi Display Replacement", ["Mazak", "CD1472", "C5470", "DR5614", "Sharp", "MDT1283", "MDT962", "BM09DF", "FCUA", "Mitsubishi"]),
    ("okuma", "Okuma Display Replacement", ["Okuma"]),
    ("haas", "Haas Display Replacement", ["Haas"]),
    ("siemens", "Siemens Display Replacement", ["Siemens", "SM0901", "6FC3988"]),
    ("ktv", "Custom KTV Series Industrial Displays", ["KTV"]),
    ("conv", "Industrial Video Signal Converters", ["GBS", "KT809", "KT819"]),
    ("guide", "Technical Guides & Solutions", ["CGA", "EGA", "RGBHV", "Industrial_CNC", "Industrial_RGBHV",
     "Industrial_Video_Display_Smart", "Industrial_Video_Display_Color",
     "Kongto_Technology_Industrial", "Video_Signal_Conversion",
     "Video_Signal_Converters_in_CNC", "Video_Signal_Converter_Series",
     "How_to_Retrofit", "Custom_Industrial"]),
    ("comp", "Technical Comparisons", ["comparison", "Comparison", "FANUC_CRT_Maintenance", "FANUC_CRT_Repair"]),
    ("faq", "FAQ & Troubleshooting", ["faq", "FAQ", "Used_Display", "Used_Industrial"]),
    ("news", "News & Press Releases", ["press_release", "Beijing", "Nanjing", "Shenzhen_Zhongtu"]),
    ("guide2", "More Technical Guides", ["Industrial_Controller", "Industrial_Display_Market",
     "Industrial_Display_Procurement", "Industrial_Touchscreen",
     "Industrial_Video_Display_Color", "Video_Signal_Converter_Buying"]),
]

CN_ICONS = {"fanuc":"🔧","mazak":"🔧","okuma":"🔧","haas":"🔧","siemens":"🔧","mitsu":"🔧",
            "ktv":"📺","conv":"🔌","guide":"📚","comp":"⚖️","faq":"❓","news":"📰"}
EN_ICONS = {"fanuc":"🔧","mazak":"🔧","okuma":"🔧","haas":"🔧","siemens":"🔧",
            "ktv":"📺","conv":"🔌","guide":"📚","comp":"⚖️","faq":"❓","news":"📰","guide2":"📚"}

def extract_meta(filepath):
    """Extract title, description, date from article HTML."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        title_m = re.search(r'<title>(.*?)</title>', content)
        desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
        date_m = re.search(r'(\d{4}-\d{2}-\d{2})', content[:2000])
        title = title_m.group(1).strip() if title_m else os.path.basename(filepath)
        desc = desc_m.group(1).strip() if desc_m else ''
        date = date_m.group(1) if date_m else ''
        # Clean title - remove site name suffix
        for suffix in [' | 深圳市江图科技有限公司', ' | Kongto Technology', ' | 江图科技']:
            if suffix in title:
                title = title.replace(suffix, '')
        return title, desc, date
    except:
        return os.path.basename(filepath), '', ''

def classify(filename, categories):
    """Classify a file into a category."""
    fn = filename.lower()
    for cat_id, cat_name, keywords in categories:
        for kw in keywords:
            if kw.lower() in fn:
                return cat_id
    return 'guide'  # default

def generate_index(posts_dir, categories, icons, lang):
    """Generate an index.html for given posts directory."""
    # Collect and classify all articles
    files = [f for f in os.listdir(posts_dir)
             if f.endswith('.html') and f != 'index.html']

    classified = {}
    for f in files:
        cat = classify(f, categories)
        if cat not in classified:
            classified[cat] = []
        title, desc, date = extract_meta(os.path.join(posts_dir, f))
        classified[cat].append((f, title, desc, date))

    # Sort each category: newest first by filename date
    for cat in classified:
        classified[cat].sort(key=lambda x: x[0], reverse=True)

    # Build TOC
    toc_items = []
    for cat_id, cat_name, _ in categories:
        if cat_id in classified:
            count = len(classified[cat_id])
            icon = icons.get(cat_id, "📄")
            toc_items.append(f'<li><a href="#{cat_id}">{icon} {cat_name} ({count})</a></li>')

    # Build category sections
    sections = []
    for cat_id, cat_name, _ in categories:
        if cat_id not in classified:
            continue
        articles = classified[cat_id]
        icon = icons.get(cat_id, "📄")

        items = []
        for fname, title, desc, date in articles:
            if lang == 'cn':
                url = f'/posts/{fname}'
            else:
                url = f'/en/posts/{fname}'
            date_html = f'<time datetime="{date}">{date}</time>' if date else ''
            items.append(f'''<article class="post-item">
    <h3><a href="{url}">{title}</a></h3>
    {date_html}
    <p>{desc[:120]}</p>
</article>''')

        sections.append(f'''<section class="category-section" id="{cat_id}">
    <h2>{icon} {cat_name} <span class="article-count">({len(articles)}篇)</span></h2>
    <div class="post-list">
        {chr(10).join(items)}
    </div>
</section>''')

    # Determine site name and metadata
    if lang == 'cn':
        site_name = '深圳市江图科技有限公司'
        logo_text = '江图科技'
        footer_name = '江图科技'
        footer_desc = '专注工业视频显示解决方案'
        footer_copy = '© 2026 深圳市江图科技有限公司'
        page_title = f'文章列表 | {site_name}'
        page_desc = '工业视频显示技术文章，涵盖FANUC、三菱、西门子、Mazak、Okuma、Haas显示器升级、工业视频信号转换、CNC数控备件等专业内容。'
        hreflang_zh = 'https://cncdisplay.com/posts/index.html'
        hreflang_en = 'https://cncdisplay.com/en/posts/index.html'
        canonical = 'https://cncdisplay.com/posts/'
        nav_home = '首页'
        nav_articles = '文章'
        nav_downloads = '下载'
        nav_about = '关于'
        lang_zh = '中文'
        lang_en = 'English'
        all_articles = '全部文章'
        cat_nav = '文章分类导航'
        toc_heading = '文章分类导航'
    else:
        site_name = 'Kongto Technology'
        logo_text = 'Kongto Technology'
        footer_name = 'Kongto Technology'
        footer_desc = 'Industrial Video Display Solutions'
        footer_copy = '© 2026 Kongto Technology Co., Ltd.'
        page_title = f'Articles | {site_name}'
        page_desc = 'Industrial video display technical articles covering FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas display upgrades, signal converters, and CNC spare parts.'
        hreflang_zh = 'https://cncdisplay.com/posts/index.html'
        hreflang_en = 'https://cncdisplay.com/en/posts/index.html'
        canonical = 'https://cncdisplay.com/en/posts/'
        nav_home = 'Home'
        nav_articles = 'Articles'
        nav_downloads = 'Downloads'
        nav_about = 'About'
        lang_zh = '中文'
        lang_en = 'English'
        all_articles = 'All Articles'
        cat_nav = 'Category Navigation'
        toc_heading = 'Category Navigation'

    html = f'''<!DOCTYPE html>
<html lang="{'zh-CN' if lang == 'cn' else 'en'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{page_desc}">
    <link rel="stylesheet" href="/css/style.css?v=6">
    <link rel="alternate" hreflang="zh" href="{hreflang_zh}" />
    <link rel="alternate" hreflang="en" href="{hreflang_en}" />
    <link rel="canonical" href="{canonical}">
    <style>
        .category-section {{ margin: 2rem 0; padding: 1.5rem; background: #f8f9fa; border-radius: 8px; }}
        .category-section h2 {{ color: #1a1a2e; border-bottom: 2px solid #4cc9f0; padding-bottom: 0.5rem; }}
        .article-count {{ color: #666; font-size: 0.8em; }}
        .post-list {{ display: grid; gap: 1rem; margin-top: 1rem; }}
        .post-item {{ background: white; padding: 1rem; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .post-item h3 {{ margin: 0 0 0.5rem 0; font-size: 1rem; }}
        .post-item h3 a {{ color: #1a1a2e; text-decoration: none; }}
        .post-item h3 a:hover {{ color: #4cc9f0; }}
        .post-item time {{ color: #888; font-size: 0.85rem; }}
        .post-item p {{ color: #555; font-size: 0.9rem; margin: 0.5rem 0 0 0; }}
        .toc {{ background: white; padding: 1.5rem; border-radius: 8px; margin: 2rem 0; }}
        .toc h3 {{ margin-top: 0; }}
        .toc ul {{ columns: 2; column-gap: 2rem; }}
        .toc li {{ break-inside: avoid; margin-bottom: 0.3rem; }}
        @media (max-width: 768px) {{ .toc ul {{ columns: 1; }} }}
    </style>
</head>
<body>
    <header><nav>
        <a href="/{'en/' if lang == 'en' else ''}" class="logo">{logo_text}</a>
        <div class="nav-links">
            <a href="/{'en/' if lang == 'en' else ''}">{nav_home}</a>
            <a href="/{'en/' if lang == 'en' else ''}posts/">{nav_articles}</a>
            <a href="/{'en/' if lang == 'en' else ''}docs/">{nav_downloads}</a>
            <a href="/{'en/' if lang == 'en' else ''}about.html">{nav_about}</a>
        </div>
        <div class="lang-switch">
            <a href="/posts/" lang="zh" class="lang-zh">{lang_zh}</a>
            <span class="divider">|</span>
            <a href="/en/posts/" lang="en" class="lang-en">{lang_en}</a>
        </div>
    </nav></header>
    <main>
        <h1>{all_articles}</h1>
        <div class="toc">
            <h3>{toc_heading}</h3>
            <ul>
                {chr(10).join(toc_items)}
            </ul>
        </div>
        {chr(10).join(sections)}
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">{footer_name}</span>
                <p>{footer_desc}</p>
            </div>
            <div class="footer-links">
                <a href="/{'en/' if lang == 'en' else ''}posts/">技术文章</a>
                <a href="/{'en/' if lang == 'en' else ''}docs/">资料下载</a>
                <a href="/{'en/' if lang == 'en' else ''}about.html">关于我们</a>
            </div>
            <p class="footer-copy">{footer_copy}</p>
        </div>
    </footer>
</body>
</html>'''
    return html

# Generate CN index
cn_html = generate_index('posts', CN_CATEGORIES, CN_ICONS, 'cn')
with open('posts/index.html', 'w', encoding='utf-8') as f:
    f.write(cn_html)

# Count CN
cn_count = len([f for f in os.listdir('posts') if f.endswith('.html') and f != 'index.html'])
print(f'CN index: {cn_count} articles')

# Generate EN index
en_html = generate_index('en/posts', EN_CATEGORIES, EN_ICONS, 'en')
with open('en/posts/index.html', 'w', encoding='utf-8') as f:
    f.write(en_html)

en_count = len([f for f in os.listdir('en/posts') if f.endswith('.html') and f != 'index.html'])
print(f'EN index: {en_count} articles')
print('Done.')
