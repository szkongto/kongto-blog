"""Generate search-index.json for client-side search from all HTML articles."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def load_redirect_map():
    """读 _redirects，返回 源URL -> 目标URL。

    以前这里是一份手写元组，每次做去重只把当次收口的那几个页面补进去，
    之后新加的规则全部漏登记，索引里于是长期留着已 301 的 URL
    （2026-09-11 实测 16 条）。改为以 _redirects 为唯一事实源。
    """
    rmap = {}
    path = os.path.join(ROOT, '_redirects')
    if not os.path.exists(path):
        return rmap
    with open(path, encoding='utf-8') as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith('#'):
                continue
            parts = raw.split()
            if len(parts) >= 2:
                rmap[parts[0]] = parts[1]
    return rmap


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

            # 301 收口页不在这里判，统一放到末尾按 load_redirect_map() 处理，
            # 因为「跳过」还是「改写目标」要看目标页有没有自己的索引条目。

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

    # 301 收口：索引里不该留已重定向的 URL。分两种处理：
    #   目标页自己也是索引条目（去重合并场景）→ 源页整条丢弃，否则同一页面
    #     会出现两条，且旧条目的 title/description 与目标页不符
    #   目标页没有条目（/index.html -> /、/docs/index.html -> /docs/ 这类
    #     目录规范化）→ 把 URL 改写成目标，否则首页和下载页会从站内搜索消失
    rmap = load_redirect_map()
    entry_urls = {e['url'] for e in entries}
    final, kept_urls, dropped, rewritten = [], set(), [], []
    for e in entries:
        url = e['url']
        if url in rmap:
            tgt = rmap[url]
            if tgt in entry_urls:
                dropped.append(url)
                continue
            e['url'] = tgt
            rewritten.append((url, tgt))
            url = tgt
        if url in kept_urls:
            continue
        kept_urls.add(url)
        final.append(e)
    entries = final

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
    print(f"301 丢弃 {len(dropped)} 条, URL 改写 {len(rewritten)} 条")
    for u, t in rewritten:
        print(f"  改写 {u} -> {t}")
    cats = {}
    for e in entries:
        cats[e['category']] = cats.get(e['category'], 0) + 1
    print(f"By category: {cats}")

if __name__ == '__main__':
    main()
