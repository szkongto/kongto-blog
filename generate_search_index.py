"""Generate search-index.json for client-side search from all HTML articles."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

def strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_article_info(filepath):
    """Extract title, desc, category, keywords from a page."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    info = {}

    # Title
    m = re.search(r'<title>(.*?)</title>', content)
    title = strip_html(m.group(1)) if m else os.path.basename(filepath)
    # Clean title: remove site name suffix
    title = re.sub(r'\s*[|｜]\s*深圳市江图科技有限公司.*$', '', title)
    title = re.sub(r'\s*[|｜]\s*Kongto Technology.*$', '', title)
    info['title'] = title.strip()

    # Description
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', content)
    info['description'] = strip_html(m.group(1)) if m else ''

    # H1
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content)
    info['h1'] = strip_html(m.group(1)) if m else ''

    # Keywords
    m = re.search(r'<meta\s+name="keywords"\s+content="([^"]+)"', content)
    info['keywords'] = m.group(1) if m else ''

    # Category from path
    rel = os.path.relpath(filepath, ROOT).replace('\\', '/')
    if rel.startswith('posts/'):
        info['category'] = 'article'
        info['lang'] = 'zh'
    elif rel.startswith('en/posts/'):
        info['category'] = 'article'
        info['lang'] = 'en'
    elif rel.startswith('brands/'):
        info['category'] = 'brand'
        info['lang'] = 'zh'
    elif rel.startswith('en/brands/'):
        info['category'] = 'brand'
        info['lang'] = 'en'
    elif rel.startswith('docs/'):
        info['category'] = 'download'
        info['lang'] = 'zh'
    elif rel.startswith('en/docs/'):
        info['category'] = 'download'
        info['lang'] = 'en'
    else:
        info['category'] = 'page'
        info['lang'] = 'zh'

    # Date from filename
    m = re.search(r'article_(\d{8})_', filepath)
    info['date'] = m.group(1) if m else ''

    info['url'] = '/' + rel

    return info

def main():
    os.chdir(ROOT)
    entries = []
    seen = set()

    for root, dirs, files in os.walk('.'):
        # Skip non-content dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in (
            'node_modules', 'backlinks_daily', 'backlinks_output',
            'seo_backup', '__pycache__', 'fonts', 'images',
            'output', '_archive_audit', '_templates', 'patches',
            'screaming_frog_reports', 'en_bak'
        )]
        for fname in files:
            if not fname.endswith('.html'):
                continue
            fp = os.path.join(root, fname)
            rel = os.path.relpath(fp, '.').replace('\\', '/')

            # Skip index pages (not content pages)
            if fname == 'index.html' and rel in ('index.html', 'en/index.html', 'docs/index.html', 'en/docs/index.html'):
                # Include index pages as they describe the site
                pass
            elif fname == 'index.html':
                continue

            # Skip utility pages
            if fname in ('404.html', 'baidu_verify_codeva-MOcuLxbSCp.html'):
                continue

            # Skip 301'd guide/knowledge/product pages (P1 dedup Cluster 3/5, 2026-09-02) — redirect to authorities
            if rel in (
                'guides/fanuc-crt-to-lcd-guide.html',
                'guides/mazak-crt-to-lcd-guide.html',
                'guides/mitsubishi-crt-to-lcd-guide.html',
                'guides/siemens-crt-to-lcd-guide.html',
                'knowledge/fanuc-crt-to-lcd-replacement-guide.html',
                'knowledge/haas-crt-monitor-replacement-guide.html',
                'knowledge/mazak-crt-to-lcd-retrofit-guide.html',
                'knowledge/mitsubishi-cnc-display-replacement-guide.html',
                'knowledge/okuma-crt-to-lcd-replacement-guide.html',
                'knowledge/siemens-crt-to-lcd-upgrade-guide.html',
                'posts/siemens-sinumerik-cnc-display-upgrade-complete-guide.html',
                'posts/siemens-sinumerik-display-troubleshooting-guide.html',
                'products/mazak-mdt1283b-1a-lcd-upgrade.html',
                'posts/haas-crt-monitor-troubleshooting.html',
                'products/haas-9pin-mono-crt-lcd-upgrade.html',
                'posts/article_20260503_FANUC_A61L_0001_0093_LCD.html',
                'posts/FANUC_A61L_0001_0093_LCD_CNC_Upgrade_Replacement.html',
                'posts/fanuc-a61l-0001-0093-crt-lcd-upgrade.html',
            ):
                continue

            # Skip redirect pages
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(5000)
            if 'http-equiv="refresh"' in content.lower() and 'window.location.href' not in content.lower():
                continue

            url = '/' + rel
            if url in seen:
                continue
            seen.add(url)

            info = extract_article_info(fp)
            # Search text combining all fields
            info['search_text'] = f"{info['title']} {info['description']} {info['h1']} {info['keywords']}"
            info['url'] = url
            entries.append(info)

    # Write the index
    outpath = os.path.join(ROOT, 'search-index.json')
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    # search.html loads search-index.js (initSearchIndex(...)), keep it in sync
    js_path = os.path.join(ROOT, 'search-index.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('initSearchIndex(')
        json.dump(entries, f, ensure_ascii=False)
        f.write(');')

    print(f"Generated search-index.json with {len(entries)} entries")
    cats = {}
    for e in entries:
        cats[e['category']] = cats.get(e['category'], 0) + 1
    print(f"By category: {cats}")

if __name__ == '__main__':
    main()
