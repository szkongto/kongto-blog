#!/usr/bin/env python3
"""Add Product JSON-LD (no price) to zh product pages that lack it.
Chinese product pages don't show prices — schema omits Offer.
Model/brand derived from filename; title/description from page.
"""

import os, re, glob

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ZH_PRODUCTS = os.path.join(BASE_DIR, 'zh', 'products')

# filename-prefix -> display brand
BRAND_MAP = {
    'fanuc': 'FANUC',
    'mitsubishi': 'Mitsubishi',
    'mazak': 'Mazak',
    'siemens': 'Siemens',
    'haas': 'Haas',
    'okuma': 'Okuma',
    'toshiba': 'Toshiba',
    'heidenhain': 'Heidenhain',
    'matsushita': 'Matsushita',
    'sharp': 'Sharp',
}

def extract_title(content):
    m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    if m:
        title = re.sub(r'\s+', ' ', m.group(1)).strip()
        # Strip trailing brand suffix
        title = re.sub(r'\s*[|｜]\s*(深圳市?江图科技有限公司|Kongto|Kongto Technology|江图科技).*$', '', title)
        return title.strip()
    return ''

def extract_description(content):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
    return m.group(1).strip() if m else ''

def extract_brand_mpn(filename):
    base = filename.replace('-lcd-upgrade.html', '').replace('.html', '')
    for prefix in sorted(BRAND_MAP, key=len, reverse=True):
        if base == prefix or base.startswith(prefix + '-'):
            brand = BRAND_MAP[prefix]
            rest = base[len(prefix):].lstrip('-')
            # mpn = rest upper-cased (e.g. a61l-0001-0074 -> A61L-0001-0074)
            mpn = re.sub(r'([a-zA-Z]+)', lambda m: m.group(1).upper(), rest)
            return brand, mpn
    # fallback: whole base as mpn, brand unknown
    return '', base.upper()

def build_product_ld(title, brand, mpn, description, page_url):
    name = title if title else mpn
    d = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': name,
        'brand': {'@type': 'Brand', 'name': brand} if brand else {'@type': 'Brand', 'name': 'Kongto Technology'},
        'mpn': mpn,
        'description': description,
        'url': page_url,
    }
    return '    <script type="application/ld+json">\n' + json_dumps_pretty(d) + '    </script>\n'

def json_dumps_pretty(d):
    import json
    return json.dumps(d, ensure_ascii=False, indent=2) + '\n'

def main():
    files = sorted(glob.glob(os.path.join(ZH_PRODUCTS, '*.html')))
    changed = 0
    for fp in files:
        fname = os.path.basename(fp)
        if fname == 'index.html':
            continue
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if already has Product JSON-LD
        if '"Product"' in content:
            continue

        title = extract_title(content)
        desc = extract_description(content)
        brand, mpn = extract_brand_mpn(fname)
        page_url = 'https://cncdisplay.com/zh/products/' + fname

        ld = build_product_ld(title, brand, mpn, desc, page_url)

        # Insert before </head>
        if '</head>' in content:
            content = content.replace('</head>', ld + '</head>', 1)
        else:
            print(f'SKIP (no </head>): {fname}')
            continue

        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'ADDED: {fname} (brand={brand}, mpn={mpn})')
        changed += 1

    print(f'\nDone. Added Product JSON-LD to {changed} pages.')

if __name__ == '__main__':
    main()
