# -*- coding: utf-8 -*-
"""找 GSC error 候选页: 所有 JSON-LD 中 Product 相关但可能缺 offers 的 + zh 产品页结构"""
import re, glob, json

files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)
         if not f.startswith(('en_bak/', 'node_modules/', '_archive_audit/'))]

print('=== zh/ 下 Product schema 页 ===')
for fs in files:
    if not fs.startswith('zh/'):
        continue
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
            if isinstance(b, dict) and b.get('@type') in ('Product', 'product'):
                has_offers = bool(b.get('offers'))
                print(f'  {fs} | offers={"Y" if has_offers else "N"} | '
                      f'keys={[k for k in b.keys() if k!="offers"][:10]}')

print()
print('=== offers 缺 price 的 3 页完整 offers 结构 ===')
for fs in ['products/flickering-screen.html', 'products/image-retention.html',
           'products/no-display.html']:
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        print('  MISS', fs)
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
            if isinstance(b, dict) and b.get('@type') in ('Product', 'product'):
                print(f'  === {fs} ===')
                print('   Product keys:', list(b.keys()))
                print('   offers:', json.dumps(b.get('offers'), ensure_ascii=False)[:300])

print()
print('=== 全站 JSON-LD @type 分布 ===')
import collections
types = collections.Counter()
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
            if isinstance(b, dict):
                t = b.get('@type')
                types[str(t)] += 1
for t, c in types.most_common():
    print(f'  {t}: {c}')
