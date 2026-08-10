# -*- coding: utf-8 -*-
"""详情: 有 aggregateRating / review 的产品页结构"""
import re, glob, json

files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)
         if not f.startswith(('en_bak/', 'node_modules/', '_archive_audit/'))]
has_aggr = []
has_rev = []
for fs in files:
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for m in re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                         h, re.S | re.I):
        raw = m.group(1).strip().replace('//<![CDATA[', '').replace('//]]>', '')
        try:
            data = json.loads(raw)
        except Exception:
            continue
        blocks = data if isinstance(data, list) else [data]
        for b in blocks:
            if not isinstance(b, dict) or b.get('@type') not in ('Product', 'product'):
                continue
            if b.get('aggregateRating'):
                has_aggr.append((fs, b['aggregateRating']))
            if b.get('review'):
                has_rev.append((fs, b['review']))

print(f'=== 有 aggregateRating: {len(has_aggr)} 页 ===')
for f, ar in has_aggr:
    if isinstance(ar, dict):
        print(f'  {f} | keys={list(ar.keys())} ratingValue={ar.get("ratingValue")!r} '
              f'ratingCount={ar.get("ratingCount")!r} bestRating={ar.get("bestRating")!r}')
    else:
        print(f'  {f} | TYPE={type(ar).__name__}')
print()
print(f'=== 有 review: {len(has_rev)} 页 ===')
for f, rv in has_rev:
    if isinstance(rv, list):
        rv = rv[0] if rv else None
    if isinstance(rv, dict):
        print(f'  {f} | keys={list(rv.keys())} reviewBody={"Y" if rv.get("reviewBody") else "N"} '
              f'ratingValue={rv.get("reviewRating", {}).get("ratingValue") if isinstance(rv.get("reviewRating"), dict) else None!r}')
    else:
        print(f'  {f} | TYPE={type(rv).__name__} value={rv!r}')
