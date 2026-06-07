"""Generate search-index.json for client-side search from all HTML articles."""
import json, os, re, sys

ROOT = "d:/code/seo_deploy"

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
        if 'seo_fix_package' in root or 'output' in root:
            continue
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

    print(f"Generated search-index.json with {len(entries)} entries")
    cats = {}
    for e in entries:
        cats[e['category']] = cats.get(e['category'], 0) + 1
    print(f"By category: {cats}")

if __name__ == '__main__':
    main()
