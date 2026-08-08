#!/usr/bin/env python3
"""Full on-page SEO audit."""
import os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

total = 0
has_article_schema = 0
has_breadcrumb = 0
has_org_schema = 0
has_faq_schema = 0
missing_meta_desc = 0
missing_canonical = 0
title_too_long = 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.')
               and d not in ('images_backup_compressed', '.git', 'images')]
    for f in files:
        if not f.endswith('.html') or f in ('404.html', 'baidu_verify_codeva-MOcuLxbSCp.html'):
            continue
        total += 1
        fpath = os.path.join(root, f)
        with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
            content = fh.read()

        if '"@type": "Article"' in content:
            has_article_schema += 1
        if 'BreadcrumbList' in content:
            has_breadcrumb += 1
        if '"@type": "Organization"' in content or '"@type": "LocalBusiness"' in content:
            has_org_schema += 1
        if 'FAQPage' in content:
            has_faq_schema += 1

        title_m = re.search(r'<title>(.*?)</title>', content)
        desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
        canonical_m = re.search(r'<link rel="canonical"', content)

        if not desc_m:
            missing_meta_desc += 1
        if not canonical_m:
            missing_canonical += 1
        if title_m and len(title_m.group(1)) > 70:
            title_too_long += 1

# Content stats
article_count = 0
total_chars = 0
for f in os.listdir('posts'):
    if f.endswith('.html') and f != 'index.html':
        article_count += 1
        with open(os.path.join('posts', f), 'r', encoding='utf-8', errors='replace') as fh:
            c = fh.read()
        body = re.search(r'<main>(.*?)</main>', c, re.DOTALL)
        if body:
            text = re.sub(r'<[^>]+>', ' ', body.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            total_chars += len(text)

# Brand page stats
brand_links = {}
for f in os.listdir('brands'):
    if f.endswith('.html'):
        with open(os.path.join('brands', f), 'r', encoding='utf-8', errors='replace') as fh:
            c = fh.read()
        links = re.findall(r'href="(/posts/article_[^"]+)"', c)
        brand_links[f] = len(links)

print("=" * 60)
print("TECHNICAL SEO AUDIT RESULTS")
print("=" * 60)
print(f"Total pages: {total}")
print(f"Pages with Article schema: {has_article_schema}")
print(f"Pages with Breadcrumb schema: {has_breadcrumb}")
print(f"Pages with Org/LocalBusiness schema: {has_org_schema}")
print(f"Pages with FAQ schema: {has_faq_schema}")
print(f"Missing meta description: {missing_meta_desc}")
print(f"Missing canonical: {missing_canonical}")
print(f"Title > 70 chars: {title_too_long}")

print(f"\n=== CONTENT ===")
print(f"CN articles: {article_count}")
print(f"Avg content length: {total_chars//article_count if article_count else 0} chars")

print(f"\n=== BRAND PAGE LINKS ===")
for brand, count in sorted(brand_links.items()):
    print(f"  {brand}: {count} article links")

print(f"\n=== SITEMAP ===")
with open('sitemap.xml', 'r', encoding='utf-8') as f:
    sitemap = f.read()
urls = re.findall(r'<loc>(https://[^<]+)</loc>', sitemap)
print(f"Sitemap URLs: {len(urls)}")

# Check for lastmod freshness
lastmods = re.findall(r'<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>', sitemap)
if lastmods:
    newest = max(lastmods)
    oldest = min(lastmods)
    print(f"Lastmod range: {oldest} to {newest}")

print("\nDone.")
