# -*- coding: utf-8 -*-
"""GSC富媒体修复 活站验证: 6 症状页 TechArticle schema + 无 offers + 无 Technologynology
用法: PYTHONIOENCODING=utf-8 python scripts/verify_live_diag_schema.py
"""
import re, json, subprocess, concurrent.futures

URLS = [
    'https://cncdisplay.com/products/flickering-screen.html',
    'https://cncdisplay.com/products/image-retention.html',
    'https://cncdisplay.com/products/no-display.html',
    'https://cncdisplay.com/zh/products/flickering-screen.html',
    'https://cncdisplay.com/zh/products/image-retention.html',
    'https://cncdisplay.com/zh/products/no-display.html',
]


def check(url):
    r = subprocess.run(['curl', '-s', '-o', 'NUL', '-w', '%{http_code}', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    code = r.stdout.strip()
    if code != '200':
        return f'{url}: HTTP {code} FAIL'
    body = subprocess.run(['curl', '-s', url], capture_output=True, text=True,
                          encoding='utf-8', errors='replace').stdout
    probs = []
    if 'Technologynology' in body:
        probs.append('Technologynology 残留')
    has_tech = False
    for m in re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                         body, re.S | re.I):
        try:
            d = json.loads(m.group(1).strip())
        except Exception:
            continue
        for b in (d if isinstance(d, list) else [d]):
            if not isinstance(b, dict):
                continue
            if b.get('@type') == 'TechArticle':
                has_tech = True
                if 'offers' in b:
                    probs.append('TechArticle 残留 offers')
                if not b.get('headline') or not b.get('author') or not b.get('publisher'):
                    probs.append('TechArticle 缺字段')
            if b.get('@type') == 'Product':
                probs.append('Product schema 残留')
    if not has_tech:
        probs.append('缺 TechArticle')
    status = 'OK' if not probs else 'FAIL: ' + '; '.join(probs)
    return f'{url}: HTTP {code} {status}'


with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for line in ex.map(check, URLS):
        print(line)
