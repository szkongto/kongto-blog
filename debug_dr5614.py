import re

with open(r'D:\code\seo_deploy\posts\article_20260522_Mazak_DR5614_LCD_CRT.html', 'r', encoding='utf-8', errors='replace') as f:
    zh = f.read()

with open(r'D:\code\seo_deploy\en\posts\Mazak_DR5614_LCD_CNC_CRT_Replacement.html', 'r', encoding='utf-8', errors='replace') as f:
    en = f.read()

for label, content in [('ZH', zh), ('EN', en)]:
    title = re.search(r'<title>(.*?)</title>', content)
    print(f'{label} title: {title.group(1)[:60] if title else "N/A"}')

    models = set()
    for m in re.finditer(r'[A-Z0-9]+-[0-9]{4}-[0-9]{4}', content[:3000]):
        models.add(m.group(0))
    print(f'{label} full models: {models}')

    partial = set()
    for m in re.finditer(r'[A-Z0-9]{3,10}-[0-9]{2,5}', content[:3000]):
        if not re.match(r'^[A-Z0-9]+-[0-9]{4}-[0-9]{4}$', m.group(0)):
            partial.add(m.group(0))
    print(f'{label} partial models: {partial}')
    print()
