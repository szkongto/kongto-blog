#!/usr/bin/env python3
"""
Generate sitemap.xml with accurate lastmod from git history.
Uses `git log -1 --format=%cd` for each file's actual last commit date.
"""
import os
import subprocess
from datetime import datetime
from urllib.parse import quote
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://cncdisplay.com"

EXCLUDE = [
    "404.html",
    "baidu_verify_",
    "test.txt",
    "_archive_",
    "audit-verification",
    "workers/",
    "_templates/",
    "no-display.html",
    "flickering-screen.html",
    "image-retention.html",
    "posts/fanuc-a61l-0001-0093-display-faq-en.html",  # replaced by 301 redirect
]

def get_git_lastmod(filepath):
    """
    Get the last commit date for a file from git history.
    Returns YYYY-MM-DD string, or today's date if git fails.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d", "--", os.path.basename(filepath)],
            capture_output=True, text=True, cwd=os.path.dirname(filepath)
        )
        date_str = result.stdout.strip()
        if date_str and len(date_str) == 10:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
    except Exception:
        pass
    # Fallback: file mtime
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")

def get_priority(rel_path):
    if rel_path.endswith('index.html'):
        return "1.0"
    if 'about.html' in rel_path or 'author.html' in rel_path:
        return "0.8" if 'zh/' not in rel_path else "0.7"
    if 'brands/' in rel_path:
        return "0.8" if 'zh/' not in rel_path else "0.7"
    if 'posts/' in rel_path:
        return "0.7" if 'zh/' not in rel_path else "0.6"
    if 'docs/' in rel_path:
        return "0.6"
    return "0.7"

def get_changefreq(rel_path):
    if rel_path.endswith('index.html') or rel_path == 'index.html':
        return "daily"
    if 'posts/' in rel_path:
        return "weekly"
    if 'brands/' in rel_path:
        return "weekly"
    return "monthly"

def should_include(rel_path, fullpath=None):
    for ex in EXCLUDE:
        if ex in rel_path:
            return False
    # Skip redirect stubs (meta-refresh pages)
    if fullpath and os.path.isfile(fullpath):
        try:
            with open(fullpath, 'r', encoding='utf-8', errors='ignore') as f:
                first = f.read(500)
            if 'http-equiv="refresh"' in first:
                return False
        except Exception:
            pass
    return True

def main():
    html_files = []

    for root, dirs, files in os.walk(BASE):
        # Skip backup / hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('images_backup', '__pycache__', 'en_bak', '_archive_audit', '_templates')]

        for f in files:
            if not f.endswith('.html'):
                continue

            fullpath = os.path.join(root, f)
            rel = os.path.relpath(fullpath, BASE).replace('\\', '/')

            if not should_include(rel, fullpath):
                continue

            # Get accurate lastmod from git (using full path)
            try:
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d", "--", rel],
                    capture_output=True, text=True, cwd=BASE
                )
                date_str = result.stdout.strip()
                if date_str and len(date_str) == 10:
                    lastmod = date_str
                else:
                    mtime = os.path.getmtime(fullpath)
                    lastmod = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            except Exception:
                lastmod = datetime.now().strftime("%Y-%m-%d")

            # Convert to URL path
            url_path = rel
            if f == 'index.html':
                url_path = url_path.replace('/index.html', '/')

            html_files.append({
                'url': url_path,
                'lastmod': lastmod,
                'priority': get_priority(rel),
                'changefreq': get_changefreq(rel),
            })

    # Sort
    def sort_key(item):
        url = item['url']
        if url == 'index.html' or url == '':
            return (0, '')
        if url.startswith('zh/'):
            return (2, url)
        return (1, url)

    html_files.sort(key=sort_key)

    # Generate XML
    today = datetime.now().strftime("%Y-%m-%d")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')

    # Homepage
    lines.append('  <url>')
    lines.append('    <loc>%s/</loc>' % DOMAIN)
    lines.append('    <lastmod>%s</lastmod>' % today)
    lines.append('    <changefreq>daily</changefreq>')
    lines.append('    <priority>1.0</priority>')
    lines.append('  </url>')

    for page in html_files:
        url = page['url']
        if url == 'index.html':
            continue
        loc = '%s/%s' % (DOMAIN, url) if url else '%s/' % DOMAIN
        loc = loc.replace('//', '/').replace('https:/', 'https://')

        lines.append('  <url>')
        lines.append('    <loc>%s</loc>' % loc)
        lines.append('    <lastmod>%s</lastmod>' % page['lastmod'])
        lines.append('    <changefreq>%s</changefreq>' % page['changefreq'])
        lines.append('    <priority>%s</priority>' % page['priority'])
        lines.append('  </url>')

    lines.append('</urlset>')

    output_path = os.path.join(BASE, 'sitemap.xml')
    content = '\n'.join(lines) + '\n'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print('Generated sitemap.xml with %d URLs' % (len(html_files) + 1))
    print('Output: %s' % output_path)

    # Show lastmod date distribution
    dates = Counter(p['lastmod'] for p in html_files)
    print('\nlastmod distribution (top 10):')
    for date, count in dates.most_common(10):
        print('   %s: %d URLs' % (date, count))

    # Show category breakdown
    categories = {}
    for p in html_files:
        cat = p['url'].split('/')[0] if '/' in p['url'] else 'root'
        categories[cat] = categories.get(cat, 0) + 1
    print('\nCategory breakdown:')
    for cat, count in sorted(categories.items()):
        print('   %s: %d' % (cat, count))

if __name__ == '__main__':
    main()
