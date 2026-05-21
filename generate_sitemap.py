#!/usr/bin/env python3
"""Generate comprehensive sitemap.xml for cncdisplay.com"""
import os
import glob
from datetime import datetime
from urllib.parse import quote

BASE = r"C:\Users\Administrator\.qclaw\workspace\kongto-blog"
DOMAIN = "https://cncdisplay.com"

EXCLUDE = [
    "404.html",
    "baidu_verify_",
    "index.html",  # handled as /
    ".bak",
    "test.txt",
]

def url_encode(path):
    """URL-encode the path, preserving slashes"""
    parts = path.split('/')
    encoded = [quote(p, safe='') for p in parts]
    return '/'.join(encoded)

def get_priority(filepath, rel_path):
    """Assign priority based on path depth and type"""
    parts = rel_path.replace('\\', '/').split('/')
    
    if rel_path in ('index.html', '/'):
        return "1.0"
    if 'en/' in rel_path and len(parts) == 2 and parts[-1] in ('index.html', ''):
        return "0.8"  # en homepage
    if 'about.html' in rel_path or 'author.html' in rel_path:
        return "0.8" if 'en/' not in rel_path else "0.7"
    if 'brands/' in rel_path or 'brands\\' in rel_path:
        return "0.8" if 'en/' not in rel_path else "0.7"
    if 'posts/' in rel_path or 'posts\\' in rel_path:
        return "0.7" if 'en/' not in rel_path else "0.6"
    if 'docs/' in rel_path or 'docs\\' in rel_path:
        return "0.6"
    # Root-level articles, FAQ, comparison, etc.
    return "0.7"

def get_changefreq(filepath, rel_path):
    """Assign changefreq"""
    parts = rel_path.replace('\\', '/').split('/')
    
    if rel_path in ('index.html', '/'):
        return "daily"
    if 'about.html' in rel_path or 'author.html' in rel_path:
        return "monthly"
    if 'posts/' in rel_path or 'posts\\' in rel_path:
        return "weekly"
    if 'brands/' in rel_path or 'brands\\' in rel_path:
        return "weekly"
    if 'docs/' in rel_path or 'docs\\' in rel_path:
        return "monthly"
    # Root articles, FAQ, etc.
    return "weekly"

def should_include(rel_path):
    """Filter out pages that shouldn't be in sitemap"""
    for ex in EXCLUDE:
        if ex in rel_path:
            return False
    return True

def main():
    html_files = []
    
    # Walk all HTML files
    for root, dirs, files in os.walk(BASE):
        # Skip backup folders
        if 'images_backup' in root:
            continue
        
        for f in files:
            if not f.endswith('.html'):
                continue
            
            fullpath = os.path.join(root, f)
            rel = os.path.relpath(fullpath, BASE)
            
            if not should_include(rel):
                continue
            
            # Get last modified
            mtime = os.path.getmtime(fullpath)
            lastmod = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            # Convert to URL path
            url_path = rel.replace('\\', '/')
            
            # Handle index.html files specially
            if f == 'index.html':
                if 'en/' in url_path or url_path == 'en\\index.html':
                    url_path = 'en/'
                else:
                    continue  # skip root index.html, will add manually
            
            html_files.append({
                'url': url_encode(url_path),
                'lastmod': lastmod,
                'priority': get_priority(fullpath, rel),
                'changefreq': get_changefreq(fullpath, rel),
            })
    
    # Sort: root first, then by path depth, then alphabetically
    def sort_key(item):
        url = item['url']
        depth = url.count('/')
        # Root pages first, then subdirectories
        if url == 'en/' or not '/' in url.strip('/'):
            return (0, url)
        elif url.startswith('en/'):
            return (2, depth, url)
        else:
            return (1, depth, url)
    
    html_files.sort(key=sort_key)
    
    # Generate XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    
    # Add homepage manually
    lines.append('  <url>')
    lines.append(f'    <loc>{DOMAIN}/</loc>')
    lines.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
    lines.append('    <changefreq>daily</changefreq>')
    lines.append('    <priority>1.0</priority>')
    lines.append('  </url>')
    
    for page in html_files:
        lines.append('  <url>')
        lines.append(f'    <loc>{DOMAIN}/{page["url"]}</loc>')
        lines.append(f'    <lastmod>{page["lastmod"]}</lastmod>')
        lines.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        lines.append(f'    <priority>{page["priority"]}</priority>')
        lines.append('  </url>')
    
    lines.append('</urlset>')
    
    output_path = os.path.join(BASE, 'sitemap.xml')
    content = '\n'.join(lines) + '\n'
    
    # Write with UTF-8 encoding (no BOM)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated sitemap.xml with {len(html_files) + 1} URLs")
    print(f"Output: {output_path}")
    
    # Verify encoding
    with open(output_path, 'r', encoding='utf-8') as f:
        test = f.read()
    has_garbled = any(c in test for c in ['æ', 'ç', 'è', 'ä', 'ö', 'ü', 'Å', '°', '±', 'â', 'ê', 'î', 'ô', 'û', 'ë', 'ï'])
    if has_garbled:
        print("WARNING: Possible encoding issue!")
    else:
        print("Encoding: OK (UTF-8)")
    
    # Print summary
    categories = {}
    for p in html_files:
        cat = p['url'].split('/')[0] if '/' in p['url'] else 'root'
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print(f"\nBreakdown: {categories}")

if __name__ == '__main__':
    main()