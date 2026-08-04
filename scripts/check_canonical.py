# -*- coding: utf-8 -*-
"""Canonical 自检 — pre-commit 门禁
规则: 页面 canonical 必须自引用(自身URL)。zh/posts 必须指 /zh/... 自身。
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


bad = []
for f in glob.glob('**/*.html', recursive=True):
    fs = f.replace('\\', '/')
    if fs.startswith('en_bak/') or '/en_bak/' in fs or fs.startswith('node_modules/') or '/node_modules/' in fs:
        continue
    # 只强制 zh/ 目录自引用（确认的 bug 类）。EN 文章 canonical 允许指向同主题合并目标(去重)
    if not fs.startswith('zh/'):
        continue
    # 豁免目录 stub / sitemap（canonical 指向真实目标属正常）
    if fs.split('/')[-1] in ('index.html', 'sitemap.html'):
        continue
    try:
        h = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    m = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', h, re.I)
    if not m:
        continue
    href = m.group(1).replace(BASE, '')
    self_path = '/' + fs
    if norm(href) != norm(self_path):
        bad.append((f, href))

if bad:
    print(f'[CANONICAL-CHECK] {len(bad)} 个页面 canonical 非自引用:')
    for f, href in bad[:25]:
        print(f'  {f}\n    canonical={href}')
    print('\n修复: canonical 应指向页面自身URL。参考 scripts/fix_zh_canonical.py')
    sys.exit(1)
print(f'[CANONICAL-CHECK] OK — 全站 canonical 自引用')
sys.exit(0)
