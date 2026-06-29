"""Debug corruption detection"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

f = 'd:/code/seo_deploy/en/posts/article_20260508_Haas_CRT_LCD_Case.html'
with open(f, encoding='utf-8') as fh:
    content = fh.read()

CORRUPT = set('鍙戦偅绉鏄剧ず鍣崌绾柟妗娣卞湷甯傛睙浘绉戞妧鏈夐檺鍏稿凡涓嬭浇彇鎶ヤ环棰樼殑鎴戜滑')

title_m = re.search(r'<title>(.*?)</title>', content)
if title_m:
    title = title_m.group(1)
    cn = [c for c in title if '一' <= c <= '鿿']
    if cn:
        bad = sum(1 for c in cn if c in CORRUPT)
        print(f'TITLE: {bad}/{len(cn)} corrupted ({bad/len(cn)*100:.1f}%)')

# Nav text between > and <
for nt in re.findall(r'>([^<]{2,30})<', content):
    cn = [c for c in nt if '一' <= c <= '鿿']
    if cn and len(cn) >= 2:
        bad = sum(1 for c in cn if c in CORRUPT)
        if bad/len(cn) > 0.2:
            print(f'NAV: {bad}/{len(cn)} corrupted: {nt[:30]}')

# Schema blocks
for m in re.finditer(r'<script[^>]+type=(.+?)</script>', content, re.DOTALL):
    tp = m.group(1)
    if 'ld+json' in tp:
        block = m.group(0)
        start = block.index('>') + 1
        end = block.rindex('<')
        js = block[start:end].strip()
        cn = [c for c in js if '一' <= c <= '鿿']
        if cn:
            bad = sum(1 for c in cn if c in CORRUPT)
            ratio = bad/len(cn)*100
            if ratio > 5:
                print(f'SCHEMA: {bad}/{len(cn)} corrupted ({ratio:.1f}%)')
                for i, c in enumerate(js):
                    if c in CORRUPT:
                        print(f'  eg: ...{js[max(0,i-5):i+15]}...')
                        break
