"""Add Related Articles sections to EN posts missing them."""
import os, re

ROOT = r"d:\code\seo_deploy"
POSTS_DIR = os.path.join(ROOT, "en", "posts")

# Topic/keyword mapping: filename pattern -> topics
TOPIC_MAP = {
    'FANUC': ['FANUC', 'fanuc', 'a61l'],
    'Mitsubishi': ['Mitsubishi', 'mitsubishi', 'bm09df', 'fcua', 'mdt962b'],
    'Siemens': ['Siemens', 'siemens', 'sinumerik', 'sm0901'],
    'Mazak': ['Mazak', 'mazak', 'mdt1283b', 'cd1472', 'c5470ns', 'dr5614'],
    'Haas': ['Haas', 'haas'],
    'Okuma': ['Okuma', 'okuma'],
    'Sharp': ['Sharp', 'sharp'],
    'Converter': ['converter', 'Converter', 'CGA', 'EGA', 'RGB', 'rgbhv', 'signal'],
    'KTV': ['KTV', 'ktv'],
    'Guide': ['Guide', 'guide', 'guide'],
}

# Build article index: filename -> {topics, lines, h1}
articles = {}
topics_by_brand = {}

for fname in os.listdir(POSTS_DIR):
    if not fname.endswith('.html') or fname == 'index.html':
        continue
    fp = os.path.join(POSTS_DIR, fname)
    lines = sum(1 for _ in open(fp, 'rb'))
    if lines < 100:  # skip redirect shells
        continue

    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get title
    h1 = ''
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        h1 = re.sub(r'<[^>]+>', '', m.group(1)).strip()

    # Detect topics
    topics = set()
    fname_lower = fname.lower()
    for brand, keywords in TOPIC_MAP.items():
        for kw in keywords:
            if kw.lower() in fname_lower:
                topics.add(brand)
                break

    article_info = {
        'file': fname,
        'title': h1 or fname.replace('.html', ''),
        'topics': topics,
        'url': f'/en/posts/{fname}',
        'lines': lines,
        'has_related': 'related-articles' in content or 'Related Articles' in content,
    }
    articles[fname] = article_info

    for t in topics:
        if t not in topics_by_brand:
            topics_by_brand[t] = []
        topics_by_brand[t].append(article_info)

def find_related(article, max_links=4):
    """Find related articles for a given article."""
    related = []
    for fname, other in articles.items():
        if fname == article['file']:
            continue

        # Check topic overlap
        common = article['topics'] & other['topics']
        if common:
            score = len(common) * 2
            # Bonus for similar line count (similar depth)
            score += 1 if abs(article['lines'] - other['lines']) < 200 else 0
            related.append((score, other))

    # Sort by score descending
    related.sort(key=lambda x: -x[0])
    return [r[1] for r in related[:max_links]]

# Process posts missing related articles
fixed = 0
for fname, article in sorted(articles.items()):
    if article['has_related']:
        continue

    related_articles = find_related(article)
    if not related_articles:
        continue

    # Build HTML
    links_html = '\n'.join(
        f'            <li><a href="{ra["url"]}">{ra["title"]}</a></li>'
        for ra in related_articles
    )

    related_section = f'''
    <div class="related-articles" style="background:#f0f7ff;padding:20px;border-radius:8px;margin:2rem 0;">
        <h3 style="margin-top:0;color:#1e40af;">Related Articles</h3>
        <ul style="margin-bottom:0;">
{links_html}
        </ul>
    </div>'''

    fp = os.path.join(POSTS_DIR, fname)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # Insert before </main> or </body>
    if '</main>' in content:
        content = content.replace('</main>', related_section + '\n\n    </main>', 1)
    elif '</body>' in content:
        content = content.replace('</body>', related_section + '\n\n</body>', 1)
    else:
        continue

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)

    topics_str = ','.join(sorted(article['topics']))
    print(f"ADDED: {fname} [{topics_str}] -> {', '.join(r['file'].replace('.html','')[:30] for r in related_articles)}")
    fixed += 1

print(f"\nTotal related-articles added: {fixed}")
