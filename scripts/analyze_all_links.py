# -*- coding: utf-8 -*-
"""全站链接悬空分析 — 复现审计工具的 155 条死链（含被站内门禁排除的类别）
扫描所有 HTML 的 href/src 全类型链接（内部相对 + 站内绝对 + 外部 http），
判定目标是否存在（本地文件 / _redirects 转发 / 站内已部署），
按引用次数排序输出悬空目标。用于 P1-4 批量处理。

用法: python scripts/analyze_all_links.py
"""
import os, re, io, sys, glob
from collections import defaultdict, Counter
from urllib.parse import urlparse, unquote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BASE = 'https://cncdisplay.com'
SKIP_DIRS = {'en_bak', '_archive', '_archive_audit', '_templates', '__pycache__',
             'backlinks_daily', 'backlinks_output', 'node_modules', '.git',
             '.github', 'screaming_frog_reports', 'output'}

# ---------- 目标集合 ----------
real_files = set()   # 站内实际文件 (相对仓库根)
for dirpath, dirnames, filenames in os.walk('.'):
    dp = dirpath.replace('\\', '/').rstrip('/').lstrip('./')
    if any(part in SKIP_DIRS for part in dp.split('/') if part):
        continue
    for fn in filenames:
        real_files.add((dp + '/' + fn).lstrip('/'))

# _redirects: 源 → 目标
redir = {}
for line in open('_redirects', encoding='utf-8'):
    m = re.match(r'^(\S+)\s+(\S+)\s+30[12]\s*$', line.strip())
    if m:
        redir[m.group(1)] = m.group(2).replace(BASE, '')

def resolve_internal(url, page_dir):
    """相对/站内绝对 → 仓库相对路径(去 query/hash, 解码)"""
    u = unquote(url.split('#')[0].split('?')[0])
    if u.startswith('/'):
        p = u.lstrip('/')
    else:
        p = (page_dir + '/' + u).lstrip('/')
    return p

# ---------- 扫描 ----------
# target → [(引用页面, 锚文本/原始url)]
refs = defaultdict(list)
ext_count = Counter()
ext_hosts = Counter()

html_files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)]
html_files = [f for f in html_files if not any(
    f.startswith(s + '/') or '/node_modules/' in f for s in SKIP_DIRS)]

for f in html_files:
    page_dir = os.path.dirname(f)
    h = open(f, encoding='utf-8', errors='ignore').read()
    # a[href]
    for m in re.finditer(r'<a[^>]*href="([^"]+)"', h):
        url = m.group(1).strip()
        if not url or url.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')):
            continue
        if '${' in url or url.startswith('//') or url.startswith('/cdn-cgi'):
            continue
        # JS 字符串拼接误扫 (如 href="' + qrUrl + '")
        if url.strip().startswith("' + ") or ' + "' in url or "' + " in url:
            continue
        if url.startswith('http'):
            host = urlparse(url).netloc
            if host and host != urlparse(BASE).netloc and not host.endswith('.cncdisplay.com'):
                ext_hosts[host] += 1
                ext_count[url] += 1
            continue
        p = resolve_internal(url, page_dir)
        refs['/' + p].append((f, url))

    # img[src], srcset
    for m in re.finditer(r'<img[^>]*src="([^"]+)"', h):
        url = m.group(1).strip()
        if url.startswith(('http', 'data:', '//')):
            continue
        if "' + " in url or url.strip().startswith("' + "):
            continue
        p = resolve_internal(url, page_dir)
        refs['/' + p].append((f, url))

    # link[href] (css/icon/etc), script[src], video/source
    for m in re.finditer(r'<link[^>]*href="([^"]+)"', h):
        url = m.group(1).strip()
        if url.startswith(('http', 'data:', '//', '#')):
            continue
        p = resolve_internal(url, page_dir)
        refs['/' + p].append((f, url))
    for m in re.finditer(r'<script[^>]*src="([^"]+)"', h):
        url = m.group(1).strip()
        if url.startswith(('http', 'data:', '//')):
            continue
        p = resolve_internal(url, page_dir)
        refs['/' + p].append((f, url))

# ---------- 判定 ----------
dead = []   # (目标, 引用次数, [引用])
for target, rlist in refs.items():
    p = target.lstrip('/')
    # 根路径 = 首页, 有效
    if p in ('', 'index.html'):
        continue
    # Cloudflare 注入脚本 / email-decode, 运行时存在, 豁免
    if p.startswith('cdn-cgi/'):
        continue
    # 目录形式
    exists = (p in real_files) or (p.rstrip('/') + '/index.html' in real_files)
    if not exists:
        # 重定向源也算通(功能可用), 但提示
        if p in redir:
            continue
        if p + '/' in real_files or (p + '/index.html') in real_files:
            exists = True
    if not exists:
        dead.append((target, len(rlist), rlist))

dead.sort(key=lambda x: -x[1])
print(f'== 全站 {len(html_files)} 个 HTML ==')
print(f'== 悬空目标: {len(dead)} 个 ==')
print(f'== 站内引用总量: {sum(len(r) for r in refs.values())} ==')
print()
for target, n, rlist in dead:
    print(f'[{n}] {target}')
    for f, u in rlist[:5]:
        print(f'      {f}  →  {u}')
    if n > 5:
        print(f'      ... 共 {n} 处引用')

print()
print(f'== 外部链接: {sum(ext_count.values())} 个, 去重 {len(ext_count)} ==')
for host, n in ext_hosts.most_common(15):
    print(f'  {n}  {host}')
