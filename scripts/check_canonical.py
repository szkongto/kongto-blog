# -*- coding: utf-8 -*-
"""Canonical 自检 — pre-commit 门禁
规则:
1. stub 页(有 meta refresh): canonical 必须 = refresh 目标; 禁止带 hreflang
2. 非 stub 的 zh/ 页面: canonical 必须自引用(自身URL)
3. 非 stub 的 EN 页面: canonical 允许指向同主题合并目标(去重)
退出码: 0=通过, 1=有错
"""
import re
import glob
import sys

BASE = 'https://cncdisplay.com'


def norm(p):
    """路径归一化: /index.html → / , X/index.html → X/"""
    p = p.replace('\\', '/')
    if p.endswith('/index.html'):
        p = p[:-len('index.html')]
    if p.endswith('index.html'):
        p = p[:-len('index.html')]
    return p or '/'


def get_refresh_target(h):
    """有 meta refresh 返回跳转 URL, 无则 None"""
    m = re.search(
        r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\'\s]+)',
        h, re.I)
    return m.group(1).replace(BASE, '') if m else None


def get_canonical(h):
    m = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', h, re.I)
    return m.group(1).replace(BASE, '') if m else None


def count_hreflang(h):
    return len(re.findall(r'<link[^>]*rel=["\']alternate["\'][^>]*hreflang=', h, re.I))


bad = []
for f in glob.glob('**/*.html', recursive=True):
    fs = f.replace('\\', '/')
    if fs.startswith('en_bak/') or '/en_bak/' in fs or fs.startswith('node_modules/') or '/node_modules/' in fs:
        continue
    # 豁免特殊文件名(目录页/站点地图)
    if fs.split('/')[-1] in ('index.html', 'sitemap.html'):
        continue
    try:
        h = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue

    self_path = '/' + fs
    target = get_refresh_target(h)
    canonical = get_canonical(h)
    n_hreflang = count_hreflang(h)

    if target:
        # stub 页: canonical 必须 = refresh 目标; 禁止 hreflang
        if canonical and norm(canonical) != norm(target):
            bad.append((fs, f'stub canonical != refresh 目标 (canonical={canonical}, refresh={target})'))
        if n_hreflang > 0:
            bad.append((fs, f'stub 页禁止带 hreflang (残留 {n_hreflang} 条)'))
    else:
        # 非 stub 的 zh/ 页面: canonical 必须自引用
        if fs.startswith('zh/') and canonical and norm(canonical) != norm(self_path):
            bad.append((fs, f'zh 真文章 canonical 非自引用: {canonical}'))

if bad:
    print(f'[CANONICAL-CHECK] {len(bad)} 处问题:')
    for f, msg in bad[:40]:
        print(f'  {f}\n    {msg}')
    print('\n修复: 真文章 canonical 自引用; stub canonical 指向 refresh 目标且不带 hreflang')
    sys.exit(1)
print('[CANONICAL-CHECK] OK — 真文章自引用, stub 指向 refresh 目标且无 hreflang')
sys.exit(0)
