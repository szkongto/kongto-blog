# -*- coding: utf-8 -*-
"""反向语言切换检查 — EN 页的 zh hreflang 目标必须存在（与 check_lang_switch 互补）。
check_lang_switch.py 查 zh→en；本脚本查 en→zh。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SKIP = {'en_bak', '_archive_audit', '_templates', '.git', '__pycache__',
        'backlinks_daily', 'images', 'fonts', 'css', 'schema', 'data', 'workers'}

bad = []
total = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith('.html'):
            continue
        rel = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
        if rel.startswith('zh/') or rel.startswith('en_bak'):
            continue
        content = open(rel, encoding='utf-8', errors='ignore').read()
        if 'http-equiv="refresh"' in content:
            continue  # meta-refresh 壳页, 其元数据无害(会跳走), 不查
        total += 1
        for t in re.findall(r'hreflang="zh[^"]*" href="([^"]+)"', content):
            p = re.sub(r'https://cncdisplay\.com', '', t).lstrip('/')
            if p.endswith('.html') and not os.path.isfile(p):
                bad.append((rel, t))

print(f'EN页面 {total} 个, zh-hreflang 指向不存在的: {len(bad)}')
for b in bad[:20]:
    print(f'  {b[0]} → {b[1]}')
sys.exit(1 if bad else 0)
