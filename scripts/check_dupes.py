"""Check which article duplicates are missing redirect rules"""
import os, re
from collections import defaultdict

posts = [f for f in os.listdir('posts') if f.endswith('.html') and f != 'index.html']
en_posts = [f for f in os.listdir('en/posts') if f.endswith('.html') and f != 'index.html']

def extract_title(filepath):
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read(5000)
            m = re.search(r'<title>(.*?)</title>', content)
            if m:
                return m.group(1).strip()
    except: pass
    return None

titles = defaultdict(list)
for f in posts:
    t = extract_title(f'posts/{f}')
    if t: titles[t].append(f'posts/{f}')
for f in en_posts:
    t = extract_title(f'en/posts/{f}')
    if t: titles[t].append(f'en/posts/{f}')

with open('_redirects', encoding='utf-8') as f:
    redirects = f.read()

dupes = {t: files for t, files in titles.items() if len(files) > 1}
print(f'Duplicate title groups: {len(dupes)}')

for t, files in sorted(dupes.items(), key=lambda x: -len(x[1])):
    not_redirected = [f for f in files if f.split('/')[-1] not in redirects]
    if len(not_redirected) > 1:
        print(f'\n  Title: {t[:70]}')
        for f in not_redirected:
            print(f'    MISSING redirect: {f}')
