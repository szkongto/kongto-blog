"""Find and fix JSON-LD parse errors in product/brand pages."""
import os, re, json

ROOT = r'd:\code\seo_deploy'
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

print(f'\nFixed: {fixed}')
