import re

with open(r'D:\code\seo_deploy\posts\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

count = 0
for m in re.finditer(r'href="(/posts/[^"]+)"', content):
    url = m.group(1)
    if any(ord(c) > 127 for c in url):
        count += 1
        title_match = re.search(r'>([^<]+)</a>', content[m.end():m.end()+200])
        title = title_match.group(1) if title_match else '?'
        print(f'BROKEN: {url}')
        print(f'  Title: {title}')
        # Find correct URL - replace Chinese chars with transliterated URL
        correct = re.sub(r'[一-鿿]+', '', url)
        print(f'  Should be: {correct}')
        print()

print(f'Total broken links with Chinese chars: {count}')
