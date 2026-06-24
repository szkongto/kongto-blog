#!/usr/bin/env python3
"""Batch SEO fixes for cncdisplay.com"""
import os, re

BASE = r"D:\code\seo_deploy"
SKIP_LOADING = {r"D:\code\seo_deploy\index.html", r"D:\code\seo_deploy\en\index.html"}

def fix_lazy_loading(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    count = 0
    def add_loading(m):
        tag = m.group(0)
        if 'loading=' in tag:
            return tag
        tag = tag.rstrip()
        if tag.endswith('/>'):
            tag = tag[:-2] + ' loading="lazy" />'
        elif tag.endswith('>'):
            tag = tag[:-1] + ' loading="lazy">'
        nonlocal count
        count += 1
        return tag
    new_content = re.sub(r'(?i)<img\s[^>]*/?>', add_loading, content)
    if count:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    return count

def fix_tech_article(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'application/ld+json' not in content:
        return False
    count = 0
    def replace_type(m):
        block = m.group(0)
        if '"@type": "Article"' in block:
            nonlocal count
            count += 1
            block = block.replace('"@type": "Article"', '"@type": "TechArticle"')
        return block
    new_content = re.sub(r'<script type="application/ld\+json">.*?</script>', replace_type, content, flags=re.DOTALL)
    if count:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    return True

def get_html_files():
    files = []
    for root, dirs, fnames in os.walk(BASE):
        dirs[:] = [d for d in dirs if not d.startswith('_') and d not in ('.github', '.well-known', 'backlinks_daily', 'backlinks_output', '_archive_audit', '_templates')]
        for fname in fnames:
            if fname.endswith('.html'):
                files.append(os.path.join(root, fname))
    return files

def main():
    files = get_html_files()
    print(f"Found {len(files)} HTML files")
    print("\n=== STEP 1: Lazy Loading ===")
    img_count = 0
    for fpath in files:
        if fpath in SKIP_LOADING:
            continue
        c = fix_lazy_loading(fpath)
        if c:
            img_count += c
    print(f"Added loading=lazy to {img_count} images total")
    print("\n=== STEP 2: TechArticle Schema ===")
    schema_count = 0
    for fpath in files:
        if fix_tech_article(fpath):
            schema_count += 1
    print(f"Changed Article->TechArticle in {schema_count} files")
    print("\nDone!")

if __name__ == '__main__':
    main()
