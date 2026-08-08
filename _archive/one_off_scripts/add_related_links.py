#!/usr/bin/env python3
"""Add related-article cross-links to improve internal linking for SEO."""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

# Brand/topic keywords for matching
BRANDS = {
    'FANUC': ['fanuc', 'a61l', 'd9mm', '0i系统'],
    'Mitsubishi': ['mitsubishi', 'mdt962', 'bm09df', 'fcua', '三菱'],
    'Siemens': ['siemens', '6fc3988', 'sm0901', '西门子'],
    'Mazak': ['mazak', 'cd1472', 'c5470', 'dr5614', '马扎克'],
    'Okuma': ['okuma', '5000', '5020', '大隈'],
    'Haas': ['haas', '哈斯'],
    'KTV': ['ktv104', 'ktv148', 'ktv800', 'ktv804'],
    'Converter': ['gbs', 'kt809', 'kt819', '转换器', 'converter'],
    'Guide': ['cga', 'ega', 'rgbhv', 'guide', '指南', 'difference'],
}

def get_brands(filename_lower, title_lower):
    """Determine which brands this article belongs to."""
    matches = set()
    for brand, keywords in BRANDS.items():
        for kw in keywords:
            if kw in filename_lower or kw in title_lower:
                matches.add(brand)
    return matches

def find_related(current_file, current_brands, all_articles, max_links=3):
    """Find related articles by matching brand/topic."""
    related = []
    for art_file, art_title, art_brands in all_articles:
        if art_file == current_file:
            continue
        # Score by brand overlap
        overlap = len(current_brands & art_brands)
        if overlap > 0:
            related.append((overlap, art_file, art_title))
    # Sort by overlap (most related first), then take top N
    related.sort(key=lambda x: -x[0])
    return related[:max_links]

# Build article database
def build_articles(posts_dir):
    articles = []
    for f in sorted(os.listdir(posts_dir)):
        if not f.endswith('.html') or f == 'index.html':
            continue
        fpath = os.path.join(posts_dir, f)
        with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
            content = fh.read()
        title_m = re.search(r'<title>(.*?)</title>', content)
        title = title_m.group(1) if title_m else f
        brands = get_brands(f.lower(), title.lower())
        articles.append((f, title, brands))
    return articles

# Process CN articles
cnt = 0
cn_articles = build_articles('posts')
for root_f, root_title, root_brands in cn_articles:
    if not root_brands:
        continue
    fpath = os.path.join('posts', root_f)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
        content = fh.read()

    if 'Related Articles' in content or '相关文章' in content:
        continue  # already has related links

    related = find_related(root_f, root_brands, cn_articles, 3)
    if not related:
        continue

    links_html = ''.join(
        f'<li><a href="/posts/{f}">{t[:80]}</a></li>'
        for _, f, t in related
    )

    related_block = f'''
<section class="related-articles" style="margin:3rem 0;padding:1.5rem;background:#f8f9fa;border-radius:8px;">
    <h3 style="margin-top:0;">相关文章</h3>
    <ul style="display:grid;gap:0.5rem;">{links_html}</ul>
</section>'''

    # Insert before footer
    footer_idx = content.rfind('<footer')
    if footer_idx > 0:
        content = content[:footer_idx] + related_block + '\n' + content[footer_idx:]
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(content)
        cnt += 1

print(f'CN articles with related links added: {cnt}')

# Process EN articles
en_cnt = 0
en_articles = build_articles('en/posts')
for root_f, root_title, root_brands in en_articles:
    if not root_brands:
        continue
    fpath = os.path.join('en/posts', root_f)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
        content = fh.read()

    if 'Related Articles' in content:
        continue

    related = find_related(root_f, root_brands, en_articles, 3)
    if not related:
        continue

    links_html = ''.join(
        f'<li><a href="/en/posts/{f}">{t[:80]}</a></li>'
        for _, f, t in related
    )

    related_block = f'''
<section class="related-articles" style="margin:3rem 0;padding:1.5rem;background:#f8f9fa;border-radius:8px;">
    <h3 style="margin-top:0;">Related Articles</h3>
    <ul style="display:grid;gap:0.5rem;">{links_html}</ul>
</section>'''

    footer_idx = content.rfind('<footer')
    if footer_idx > 0:
        content = content[:footer_idx] + related_block + '\n' + content[footer_idx:]
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(content)
        en_cnt += 1

print(f'EN articles with related links added: {en_cnt}')
print('Done.')
