# -*- coding: utf-8 -*-
"""重建 by-size 尺寸页 — 按 spec/产品页正确 LCD 尺寸归类
修正 10.4/12.1 页大量错配
"""
import re
import glob
import os
import json

d = json.load(open('scripts/product_specs.json', encoding='utf-8'))
spec_size = {}
for k, v in d.items():
    m = re.search(r'([\d.]+)[- ]?inch', str(v.get('lcd', '')))
    if m:
        spec_size[k] = m.group(1)


def short_name(pf, fallback):
    """产品页 H1 简称(取前60)或 fallback"""
    try:
        h = open('products/' + pf, encoding='utf-8', errors='ignore').read()
        h1 = re.search(r'<h1>([^<]+)</h1>', h)
        if h1:
            n = re.sub(r'\s+', ' ', h1.group(1)).strip()
            # 截断到第一个 | 或 - 前 55 字符
            n = n.split('|')[0].strip()
            return n[:55]
    except Exception:
        pass
    return fallback


# 收集现有行 (product_file → name, compat, page)
rows = {}
for page in ['8-inch', '10.4-inch', '12.1-inch']:
    f = f'guides/by-size/{page}.html'
    if not os.path.isfile(f):
        continue
    h = open(f, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r'<tr><td><a href="/products/([^"]+)">([^<]+)</a></td><td>([^<]+)</td><td>([^<]*)</td></tr>', h):
        rows[m.group(1)] = {'name': m.group(2), 'compat': m.group(4), 'page': page}

# 归属
size_rows = {}
for k, sz in spec_size.items():
    pf = k + '-lcd-upgrade.html' if not k.endswith('-lcd-upgrade') else k + '.html'
    if not os.path.isfile('products/' + pf):
        continue
    r = rows.get(pf, {})
    name = r.get('name') or short_name(pf, k)
    compat = r.get('compat', '')
    size_rows.setdefault(sz, []).append((pf, name, compat))
# None 产品保持原页
for pf, r in rows.items():
    if pf[:-5] in spec_size:
        continue
    sz = r['page'].split('-')[0]
    size_rows.setdefault(sz, []).append((pf, r['name'], r['compat']))

# 生成行 HTML
def rows_html(prods):
    out = []
    for pf, name, compat in sorted(prods, key=lambda x: x[1]):
        out.append(f'<tr><td><a href="/products/{pf}">{name}</a></td><td>&quot;</td><td>{compat}</td></tr>')
    return '\n'.join(out)


# 重建每页(替换 model-table tbody)
def rebuild_page(page_file, title, intro, prods):
    if not os.path.isfile(page_file):
        print('新建:', page_file)
        return
    h = open(page_file, encoding='utf-8', errors='ignore').read()
    # 替换 h1 和 tbody
    h2 = re.sub(r'<h1>[^<]*</h1>', f'<h1>{title}</h1>', h, count=1)
    h2 = re.sub(r'(<tbody>)(.*?)(</tbody>)', lambda m: m.group(1) + rows_html(prods) + m.group(3), h2, flags=re.S)
    if h2 != h:
        open(page_file, 'w', encoding='utf-8', newline='\n').write(h2)
        print('重建:', page_file)


rebuild_page('guides/by-size/8-inch.html',
             '8 Inch LCD Replacement — CNC CRT to 8" LCD Upgrade Guide',
             '', size_rows.get('8', []))
rebuild_page('guides/by-size/10.4-inch.html',
             '10.4 Inch LCD Replacement — CNC CRT to 10.4" LCD Upgrade Guide',
             '', size_rows.get('10.4', []))
rebuild_page('guides/by-size/12.1-inch.html',
             '12.1 Inch LCD Replacement — CNC CRT to 12.1" LCD Upgrade Guide',
             '', size_rows.get('12.1', []))
print('15寸产品(无页,需新建):', len(size_rows.get('15', [])))
for p in size_rows.get('15', []):
    print('  ', p[1])
