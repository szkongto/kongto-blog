# -*- coding: utf-8 -*-
"""审计全站 hreflang 指向问题
1. hreflang 目标 = stub 文件(会 301) → 应指向 stub 的 refresh 目标
2. hreflang 目标本地不存在 → 404
3. 真文章(非 stub) 之间 hreflang 互指检查
输出: 问题列表
"""
import re
import glob

BASE = 'https://cncdisplay.com'


def norm(p):
    p = p.replace('\\', '/')
    if p.endswith('/index.html'):
        p = p[:-len('index.html')]
    elif p.endswith('index.html'):
        p = p[:-len('index.html')]
    return p or '/'


files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)
         if not f.replace('\\', '/').startswith(('en_bak/', 'node_modules/'))]

index = {}
stub_of = {}
for fs in files:
    key = norm('/' + fs)
    index[key] = fs
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    m = re.search(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\'\s]+)', h, re.I)
    if m:
        stub_of[key] = norm(m.group(1).replace(BASE, ''))

print('total files', len(files), '| stub files', len(stub_of))

issues = []
for fs in files:
    key = norm('/' + fs)
    if key in stub_of:
        continue  # 跳过 stub 页
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for m in re.finditer(r'<link[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)', h, re.I):
        lang, href = m.group(1), m.group(2)
        tgt = norm(href.replace(BASE, ''))
        if tgt == key:
            continue  # 自指是 EN-only 页面标准写法, 忽略
        if tgt in stub_of:
            issues.append((fs, lang, href, '->stub(301) 应指refresh目标', stub_of[tgt]))
        elif tgt not in index:
            issues.append((fs, lang, href, '->本地不存在(404)', ''))

print('total real issues', len(issues))
for fs, lang, href, reason, fix in issues:
    print(f'{fs} | {lang} -> {href}')
    print(f'    {reason} {fix}')
