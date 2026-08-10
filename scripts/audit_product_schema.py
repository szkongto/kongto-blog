# -*- coding: utf-8 -*-
"""GSC 富媒体结果 Product schema 审计
扫描: Product schema 缺 offers/review/aggregateRating、空 aggregateRating、空 review、offers 缺 price
用法: PYTHONIOENCODING=utf-8 python scripts/audit_product_schema.py
"""
import re, glob, json, sys

files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)
         if not f.startswith(('en_bak/', 'node_modules/', '_archive_audit/'))]

err_no_offers = {}      # 三无: 无 offers 且无 review 且无 aggregateRating
warn_empty_rating = {}  # aggregateRating 存在但空/缺 ratingValue
warn_empty_review = {}  # review 存在但空
warn_offers_no_price = {}  # offers 存在但缺 price
prod_count = 0

for fs in files:
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for m in re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                         h, re.S | re.I):
        raw = m.group(1).strip()
        # 去掉 CDATA
        raw = raw.replace('//<![CDATA[', '').replace('//]]>', '')
        try:
            data = json.loads(raw)
        except Exception:
            continue
        blocks = data if isinstance(data, list) else [data]
        for b in blocks:
            if not isinstance(b, dict):
                continue
            t = b.get('@type')
            if t not in ('Product', 'product'):
                continue
            prod_count += 1
            has_offers = bool(b.get('offers'))
            has_review = bool(b.get('review'))
            has_rating = bool(b.get('aggregateRating'))
            if not has_offers and not has_review and not has_rating:
                err_no_offers[fs] = b
            if 'aggregateRating' in b:
                ar = b['aggregateRating']
                if isinstance(ar, dict) and not ar.get('ratingValue'):
                    warn_empty_rating[fs] = ar
            if 'review' in b:
                rv = b['review']
                if isinstance(rv, list):
                    rv = rv[0] if rv else None
                if isinstance(rv, dict) and not rv.get('reviewBody') and not rv.get('name'):
                    warn_empty_review[fs] = rv
            # offers 缺 price
            off = b.get('offers')
            if isinstance(off, dict):
                price = off.get('price') or (off.get('priceSpecification') or {}).get('price')
                if price in (None, '', '0'):
                    warn_offers_no_price[fs] = off
            elif isinstance(off, list) and off:
                for o in off:
                    if isinstance(o, dict):
                        price = o.get('price') or (o.get('priceSpecification') or {}).get('price')
                        if price in (None, '', '0'):
                            warn_offers_no_price.setdefault(fs, o)

print(f'Product schema 页面总数: {prod_count}')
print(f'\n=== ERROR 三无(无offers/review/aggregateRating): {len(err_no_offers)} ===')
for f in sorted(err_no_offers):
    b = err_no_offers[f]
    print(f'  {f} | @type={b.get("@type")} keys={list(b.keys())[:12]}')
print(f'\n=== WARN aggregateRating空: {len(warn_empty_rating)} ===')
for f in sorted(warn_empty_rating):
    print(f'  {f} | {json.dumps(warn_empty_rating[f], ensure_ascii=False)[:150]}')
print(f'\n=== WARN review空: {len(warn_empty_review)} ===')
for f in sorted(warn_empty_review):
    print(f'  {f} | {json.dumps(warn_empty_review[f], ensure_ascii=False)[:150]}')
print(f'\n=== WARN offers缺price: {len(warn_offers_no_price)} ===')
for f in sorted(warn_offers_no_price):
    print(f'  {f} | {json.dumps(warn_offers_no_price[f], ensure_ascii=False)[:150]}')
