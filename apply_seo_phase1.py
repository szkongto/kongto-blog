#!/usr/bin/env python3
"""Phase 1 SEO fixes: canonicals, meta desc, title lengths, FAQ schema."""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

fixes = 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.')
               and d not in ('images_backup_compressed', '.git', 'images')]
    for f in files:
        if not f.endswith('.html') or f == 'baidu_verify_codeva-MOcuLxbSCp.html':
            continue
        fpath = os.path.join(root, f)
        rel = fpath.replace('\\', '/').lstrip('./')
        with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
            content = fh.read()
        original = content
        changes = []

        # Fix 1: Add canonical if missing
        if '<link rel="canonical"' not in content and f != '404.html':
            if f == 'index.html' and root == '.':
                canonical = '<link rel="canonical" href="https://cncdisplay.com/">'
            elif f == 'index.html':
                dir_path = rel.replace('/index.html', '').replace('index.html', '')
                canonical = f'<link rel="canonical" href="https://cncdisplay.com/{dir_path}/">'
            else:
                canonical = f'<link rel="canonical" href="https://cncdisplay.com/{rel}">'
            # Insert after charset or viewport meta
            insert_after = '<meta name="viewport"'
            idx = content.find(insert_after)
            if idx > 0:
                end = content.find('>', idx) + 1
                content = content[:end] + '\n    ' + canonical + content[end:]
                changes.append('added canonical')

        # Fix 2: Add meta description if missing (404 page excluded)
        if '<meta name="description"' not in content and f != '404.html' and 'baidu_verify' not in f:
            title_m = re.search(r'<title>(.*?)</title>', content)
            if title_m:
                desc = title_m.group(1)[:160]
                meta_desc = f'<meta name="description" content="{desc}">'
                idx = content.find('<meta name="viewport"')
                if idx > 0:
                    end = content.find('>', idx) + 1
                    content = content[:end] + '\n    ' + meta_desc + content[end:]
                    changes.append('added meta description')

        # Fix 3: Shorten titles > 70 chars
        title_m = re.search(r'<title>(.*?)</title>', content)
        if title_m:
            old_title = title_m.group(1)
            if len(old_title) > 70:
                # Remove Kongto Technology / 江图科技 suffix
                new_title = old_title
                for suffix in [' | Kongto Technology', ' | Kongto Technology Co., Ltd.',
                               ' | 深圳市江图科技有限公司', ' | 江图科技',
                               ' | Shenzhen Kongto Technology Co., Ltd.']:
                    new_title = new_title.replace(suffix, '')
                # If still too long, truncate
                if len(new_title) > 65:
                    new_title = new_title[:62] + '...'
                if new_title != old_title:
                    content = content.replace(f'<title>{old_title}</title>',
                                              f'<title>{new_title}</title>')
                    changes.append(f'title: {len(old_title)}->{len(new_title)}')

        # Fix 4: Add FAQ schema to FAQ pages
        if 'faq_20' in f and 'FAQPage' not in content:
            faq_schema = '''<script type="application/ld+json">
    {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[]}
    </script>'''
            idx = content.find('</head>')
            if idx > 0:
                content = content[:idx] + '\n' + faq_schema + '\n' + content[idx:]
                changes.append('added FAQ schema stub')

        if changes:
            with open(fpath, 'w', encoding='utf-8') as fh:
                fh.write(content)
            fixes += 1
            print(f'{rel}: {", ".join(changes)}')

print(f'\nTotal files fixed: {fixes}')
