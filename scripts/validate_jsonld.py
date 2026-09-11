"""Find and fix JSON-LD parse errors in product/brand pages.

仓库根目录由脚本自身位置推导（scripts/ 的父目录），不写死绝对路径。
旧版本硬编码 ROOT = d:\\code\\seo_deploy，扫的是另一个陈旧克隆，
本仓库的页面根本没被检查到，于是永远输出 Fixed: 0。
"""
import os, re, json, sys

sys.stdout.reconfigure(encoding='utf-8')

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
# 兼容旧布局：若仓库根下存在 seo_deploy/ 子目录，则以它为站点根
ROOT = os.path.join(_REPO, 'seo_deploy') if os.path.isdir(os.path.join(_REPO, 'seo_deploy')) else _REPO
DIRS = ['products', 'en/products', 'zh/products', 'brands', 'en/brands', 'zh/brands']

errors = []
for root, dirs, files in os.walk(ROOT):
    rel = os.path.relpath(root, ROOT).replace(os.sep, '/')
    if not any(rel.startswith(p) for p in DIRS):
        continue
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            html = fh.read()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        for i, b in enumerate(blocks):
            try:
                json.loads(b.strip())
            except json.JSONDecodeError:
                short = os.path.relpath(fp, ROOT).replace(os.sep, '/')
                errors.append((short, b.strip()))
                break

print(f'Pages with JSON errors: {len(errors)}')
# Fix: add missing comma before shippingDetails when offer is inline
fixed = 0
unfixed = []
for short, content in errors:
    fp = os.path.join(ROOT, *short.split('/'))
    with open(fp, 'r', encoding='utf-8') as fh:
        html = fh.read()
    # Fix missing comma: '}"shippingDetails"' -> '},\n    "shippingDetails"'
    new_html = html.replace(
        '"availability": "https://schema.org/InStock"}\n        "shippingDetails"',
        '"availability": "https://schema.org/InStock"},\n        "shippingDetails"'
    )
    # Also fix inline multi-line variant
    new_html = new_html.replace(
        '"availability": "https://schema.org/InStock"\n        "shippingDetails"',
        '"availability": "https://schema.org/InStock",\n        "shippingDetails"'
    )
    if new_html != html:
        with open(fp, 'w', encoding='utf-8') as fh:
            fh.write(new_html)
        print(f'  FIXED: {short}')
        fixed += 1
    else:
        print(f'  NO MATCH: {short}')
        unfixed.append(short)

print(f'\nFixed: {fixed}')
if unfixed:
    print(f'Unfixed: {len(unfixed)} — 需人工修，勿忽略')
    sys.exit(1)
sys.exit(0)
