import re

files = [
    (r'D:\code\seo_deploy\en\posts\article_20260508_Haas_CRT_LCD.html', 'EN'),
    (r'D:\code\seo_deploy\en\posts\article_20260508_Haas_CRT_LCD_Case.html', 'EN-Case'),
    (r'D:\code\seo_deploy\posts\article_20260508_Haas_CRT_LCD.html', 'ZH'),
    (r'D:\code\seo_deploy\posts\article_20260508_Haas_CRT_LCD_Case.html', 'ZH-Case'),
]

for path, label in files:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        c = f.read()
    title = re.search(r'<title>(.*?)</title>', c, re.DOTALL)
    print(f'{label}: {title.group(1)[:70] if title else "N/A"}')
    imgs = re.findall(r'(?i)src="([^"]*Haas[^"]*)"', c)
    for img in imgs:
        print(f'  Image: {img}')
    # lang links
    zh_btn = re.search(r'(?i)<a\s+href="([^"]*)"\s+lang="zh"', c)
    en_btn = re.search(r'(?i)<a\s+href="([^"]*)"\s+lang="en"', c)
    if zh_btn:
        print(f'  ZH btn: {zh_btn.group(1)}')
    if en_btn:
        print(f'  EN btn: {en_btn.group(1)}')
    print()
