#!/usr/bin/env python3
"""Add language switch link to article pages that lack one."""
import os, re

BASE = r"D:\code\seo_deploy"

def add_lang_switch_if_missing(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    relpath = os.path.relpath(filepath, BASE)

    # Skip non-articles and index pages
    if 'posts' not in relpath:
        return False
    if relpath.endswith('index.html'):
        return False

    # Skip if already has visible lang-switch link (class-based, not hreflang)
    if 'class="lang-zh"' in content or 'class="lang-en"' in content:
        return False

    # Extract hreflang URLs
    hreflang_pattern = r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"\s*/>'
    hreflangs = {}
    for m in re.finditer(hreflang_pattern, content):
        hreflangs[m.group(1)] = m.group(2)

    zh_url = hreflangs.get('zh-CN', '')
    en_url = hreflangs.get('en', '')
    if not zh_url or not en_url:
        return False

    zh_relative = zh_url.replace('https://cncdisplay.com', '')
    en_relative = en_url.replace('https://cncdisplay.com', '')

    is_english = relpath.startswith('en')

    # Find the nav element and add lang-switch before its closing tag
    nav_pattern = r'(<nav[^>]*>.*?)(</nav>)'
    nav_match = re.search(nav_pattern, content, re.DOTALL)
    if not nav_match:
        return False

    nav_content = nav_match.group(1)

    if is_english:
        lang_switch = f'\n        <a href="{zh_relative}" lang="zh" style="margin-left:10px;color:#888;text-decoration:none;">中文</a>'
    else:
        lang_switch = f'\n        <a href="{en_relative}" lang="en" style="margin-left:10px;color:#2563eb;text-decoration:none;">English</a>'

    new_nav = nav_content + lang_switch + nav_match.group(2)
    content = content.replace(nav_match.group(0), new_nav)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    files = []
    for root, dirs, fnames in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in ('.github', '.well-known', 'backlinks_daily', 'backlinks_output', '_archive_audit', '_templates')]
        for f in fnames:
            if f.endswith('.html'):
                files.append(os.path.join(root, f))

    fixed = 0
    for fp in files:
        if add_lang_switch_if_missing(fp):
            rel = os.path.relpath(fp, BASE)
            print(f"  ADDED: {rel}")
            fixed += 1

    print(f"\nAdded lang-switch to {fixed} files")

if __name__ == '__main__':
    main()
