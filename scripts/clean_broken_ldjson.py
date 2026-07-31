#!/usr/bin/env python3
"""Clean remaining broken JSON-LD blocks.
- FAQPage / TechArticle blocks that fail JSON parse -> delete (enhancement only).
- Product blocks that fail -> regenerate clean Product (name/desc/price from page).
"""

import re, json, glob, os

BASE = os.path.dirname(os.path.dirname(__file__))
OPEN = '<script type="application/ld+json">'

def parse_ok(b):
    try:
        json.loads(b.strip())
        return True
    except Exception:
        return False

def block_type(b):
    m = re.search(r'"@type"\s*:\s*"([^"]+)"', b)
    return m.group(1) if m else '?'

def extract_title(content):
    m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    if m:
        t = re.sub(r'\s+', ' ', m.group(1)).strip()
        return t.strip()
    return ''

def extract_desc(content):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
    return m.group(1).strip() if m else ''

def extract_price(content):
    m = re.search(r'<span class="price">\$(\d+)', content)
    if m:
        return m.group(1)
    m = re.search(r'<span class="price">[^$]*\$(\d+)', content)
    return m.group(1) if m else None

def regenerate_product(content, page_url):
    title = extract_title(content)
    desc = extract_desc(content)
    price = extract_price(content)
    mpn = ''
    m = re.search(r'<h1[^>]*>\s*([^<]+?)\s*(?:<|$)', content)
    name = title
    prod = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': name,
        'description': desc,
        'url': page_url,
    }
    if price:
        prod['offers'] = {
            '@type': 'Offer',
            'priceCurrency': 'USD',
            'price': price,
            'availability': 'https://schema.org/InStock',
            'url': page_url,
        }
    return '<script type="application/ld+json">\n' + json.dumps(prod, ensure_ascii=False, indent=2) + '\n</script>'

def clean_file(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    changed = False
    # Loop until no bad blocks remain
    while True:
        found = False
        for m in re.finditer(re.escape(OPEN), content):
            pos = m.start()
            close = content.find('</script>', pos)
            if close == -1:
                break
            block = content[pos:close]
            if not parse_ok(block):
                typ = block_type(block)
                full_script = content[pos:close + len('</script>')]
                if typ == 'Product':
                    # regenerate
                    page_url = None
                    cm = re.search(r'<link rel="canonical" href="([^"]+)"', content)
                    if cm:
                        page_url = cm.group(1)
                    if not page_url:
                        page_url = 'https://cncdisplay.com/' + os.path.relpath(fp, BASE).replace('\\', '/')
                    new_script = regenerate_product(content, page_url)
                    content = content[:pos] + new_script + content[close + len('</script>'):]
                    print(f'  REGEN {typ}: {fp}')
                else:
                    # delete FAQPage / TechArticle / other broken blocks
                    content = content[:pos] + content[close + len('</script>'):]
                    print(f'  DELETE {typ}: {fp}')
                changed = True
                found = True
                break
        if not found:
            break
    if changed:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def main():
    files = (glob.glob(os.path.join(BASE, 'posts', '*.html'))
             + glob.glob(os.path.join(BASE, 'zh', 'posts', '*.html'))
             + glob.glob(os.path.join(BASE, 'products', '*.html')))
    total = 0
    for fp in files:
        if clean_file(fp):
            total += 1
    print(f'\nCleaned {total} files.')

if __name__ == '__main__':
    main()
