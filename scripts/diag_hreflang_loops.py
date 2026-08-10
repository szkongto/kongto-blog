# -*- coding: utf-8 -*-
"""诊断回环 hreflang: EN 文章的 zh-CN 指向 zh stub 且 stub 跳回 EN.
对每个这类案例, 查 site_map 是否有真实 zh 孪生, 并列出 zh/posts 同名候选.
"""
import re
import glob
import json

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
stub_refresh = {}
for fs in files:
    key = norm('/' + fs)
    index[key] = fs
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    m = re.search(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\'\s]+)', h, re.I)
    if m:
        stub_refresh[key] = norm(m.group(1).replace(BASE, ''))


def resolve(path, depth=0):
    """沿 stub 链解析到最终真实页; 循环或超深返回 None"""
    seen = set()
    while path in stub_refresh and depth < 10:
        if path in seen:
            return None
        seen.add(path)
        path = stub_refresh[path]
        depth += 1
    return path


sm = json.load(open('data/site_map.json', encoding='utf-8')).get('zh_en_pairs', {})

print('== EN 文章 zh-CN hreflang 指向 stub 的案例 ==')
for fs in sorted(files):
    key = norm('/' + fs)
    if key in stub_refresh or not fs.startswith('posts/'):
        continue
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for m in re.finditer(r'<link[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']zh[^"\']*["\'][^>]*href=["\']([^"\']+)', h, re.I):
        href = m.group(1)
        tgt = norm(href.replace(BASE, ''))
        if tgt in stub_refresh:
            final = resolve(tgt)
            loop = final == key
            # 查 site_map 是否有真实 zh 孪生
            pair = sm.get(key) or sm.get('zh/' + fs)
            print(f'EN: {fs}')
            print(f'  zh-CN -> {tgt}  stub跳转-> {stub_refresh[tgt]}  回环={loop}  最终={final}')
            # 找 zh/posts 里同名 basename 候选
            base = fs.split('/')[-1]
            cands = [x for x in files if x.startswith('zh/posts/') and base.lower() in x.lower()]
            if cands:
                print(f'  zh/posts 同名候选: {cands}')
            if pair:
                print(f'  site_map 孪生: {pair} (在index={pair in index}, 真实页={pair in index and norm(pair) not in stub_refresh})')
