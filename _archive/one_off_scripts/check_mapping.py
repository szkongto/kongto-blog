import json
d = json.load(open(r'D:\code\seo_deploy\article_mapping.json', encoding='utf-8'))
for i, p in enumerate(d):
    print(f"{i+1}. {p['zh']}")
    print(f"   <-> {p['en']} (score: {p['score']})")
