import json
with open(r'D:\code\seo_deploy\article_mapping.json', encoding='utf-8') as f:
    data = json.load(f)
for p in data:
    if 'DR5614' in p.get('zh', '') or 'DR5614' in p.get('en', ''):
        print('ZH:', p['zh'])
        print('EN:', p['en'])
        print('Score:', p['score'])
