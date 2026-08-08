# -*- coding: utf-8 -*-
"""全站活站扫描 — 对线上 cncdisplay.com 全 URL 逐页 curl 实证（不漏任何页面）。
URL 清单 = 本地 html + sitemap + _redirects 源，去重。
输出 live_scan_report.txt：200正常 / 异常状态 / 404 / 预期301 / 异常301。

用法: python scripts/live_scan.py [--limit N] [--concurrency C]
"""
import os, sys, re, json, io, concurrent.futures, urllib.request, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
BASE = 'https://cncdisplay.com'

SKIP_DIRS = {'en_bak', '_archive_audit', '_templates', '__pycache__',
             'backlinks_daily', 'backlinks_output', 'node_modules',
             'fonts', 'images', 'output', 'screaming_frog_reports',
             'data', '.git', '.github', 'schema', 'css', 'patches', 'docs',
             'workers'}


def build_url_list():
    urls = set()

    # 1. 本地 html 文件 → URL
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP_DIRS]
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
            url = '/' + p
            if f == 'index.html':
                url = '/' + p.replace('/index.html', '/')
            if url != '/':
                url = url.rstrip('/') if url.endswith('/') and url != '/' else url
            urls.add(url)

    # 2. _redirects 源
    redirect_sources = set()
    for line in open('_redirects', encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if parts:
            s = parts[0]
            if s.startswith('http'):
                from urllib.parse import urlparse
                s = urlparse(s).path
            redirect_sources.add(s)
    urls |= redirect_sources

    # 3. sitemap URL
    try:
        sm = open('sitemap.xml', encoding='utf-8').read()
        for m in re.findall(r'<loc>([^<]+)</loc>', sm):
            from urllib.parse import urlparse
            urls.add(urlparse(m).path)
    except Exception:
        pass

    return sorted(urls), redirect_sources


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # 不跟随，捕获首跳状态 + Location


def check(url):
    # 中文路径需百分号编码（已编码的 ascii URL 不动）
    from urllib.parse import quote
    if any(ord(c) > 127 for c in url):
        url = quote(url, safe='/%')
    full = BASE + url
    opener = urllib.request.build_opener(NoRedirect)
    try:
        req = urllib.request.Request(full, headers={'User-Agent': 'cncdisplay-audit/1.0'})
        r = opener.open(req, timeout=20)
        return url, r.status, r.geturl()
    except urllib.error.HTTPError as e:
        loc = e.headers.get('Location', '') if e.headers else ''
        return url, e.code, loc
    except Exception as e:
        return url, 'ERR', str(e)[:60]


def main():
    args = sys.argv[1:]
    limit = None
    cc = 20
    if '--limit' in args:
        limit = int(args[args.index('--limit') + 1])
    if '--concurrency' in args:
        cc = int(args[args.index('--concurrency') + 1])

    urls, redirect_sources = build_url_list()
    if limit:
        urls = urls[:limit]
    print(f'扫描 {len(urls)} 个 URL，并发 {cc}')

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=cc) as ex:
        for r in ex.map(check, urls):
            results.append(r)

    # 分类
    ok, redirect, notfound, err, other = [], [], [], [], []
    for url, code, loc in results:
        if code == 200:
            ok.append((url, loc))
        elif code in (301, 302, 303, 307, 308):
            redirect.append((url, code, loc))
        elif code == 404:
            notfound.append(url)
        elif code == 'ERR':
            err.append((url, loc))
        else:
            other.append((url, code, loc))

    # 写报告
    out = []
    out.append(f'共 {len(results)} URL: 200={len(ok)}, 重定向={len(redirect)}, 404={len(notfound)}, 异常={len(err)}, 其他={len(other)}\n')

    out.append('=== 404（需判断：本地有文件=部署问题；_redirects源=断链）===')
    local_files = set()
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.html'):
                p = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
                u = '/' + p.replace('/index.html', '/').rstrip('/')
                local_files.add(u)
    for url in notfound:
        tag = '本地有文件!' if url in local_files else ('redirect源' if url in redirect_sources else '仅索引')
        out.append(f'  {url}  [{tag}]')

    out.append('\n=== 异常重定向(非预期) ===')
    # 预期 301 = redirect_sources；本地文件不应 301
    for url, code, loc in redirect:
        if url in redirect_sources:
            continue  # 预期
        if url in local_files:
            out.append(f'  {url} {code}→{loc}  [本地有文件却重定向!]')
        else:
            out.append(f'  {url} {code}→{loc}')

    out.append('\n=== 异常(ERR/其他) ===')
    for url, msg in err:
        out.append(f'  {url}  [{msg}]')
    for url, code, loc in other:
        out.append(f'  {url} {code}→{loc}')

    report = '\n'.join(out)
    open('live_scan_report.txt', 'w', encoding='utf-8').write(report)
    print(report[:3000])
    print(f'\n完整报告: live_scan_report.txt')


if __name__ == '__main__':
    main()
