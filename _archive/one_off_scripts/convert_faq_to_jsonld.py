r"""已归档，勿运行（2026-09-11 从 scripts/ 移入 _archive/one_off_scripts/）。

归档原因：
  1. 路径硬编码 d:\code\seo_deploy —— 同一 remote 的另一份陈旧克隆，不是本
     仓库。今天跑它读写都在那边，对本仓库无影响；但一旦有人把路径改指本仓库，
     它会按下面这些过时内容整体覆写线上页面
  2. 全仓库零引用（含 .github/ 与 scripts/full_gate.py）
  3. 属一次性生成脚本，产物早已上线并被后续修改取代，重跑即回退

  4. 把页面里的 microdata FAQPage 转成 JSON-LD。全站转换早已完成，重跑无事可做
"""

"""Convert microdata FAQPage to JSON-LD on all pages."""
import os, re, json

SITE_DIR = r'd:\code\seo_deploy'
SKIP = ['.ts', '.git', '.claude', 'en_bak', 'seo_backup', '__pycache__', '_archive_audit', 'worktrees', 'backlinks_daily']

count = 0
for root, dirs, files in os.walk(SITE_DIR):
    dirs[:] = [d for d in dirs if not any(s in d for s in SKIP)]
    for f in files:
        if not f.endswith('.html'): continue
        fp = os.path.join(root, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            c = fh.read()

        # Check if it has microdata FAQ but no JSON-LD FAQ
        if 'itemtype="https://schema.org/FAQPage"' not in c:
            continue
        if '"@type": "FAQPage"' in c:
            continue  # already has JSON-LD

        # Extract all Q&A pairs from microdata
        qa_pairs = []
        # Find each Question block
        q_starts = [m.start() for m in re.finditer(r'itemprop="mainEntity"\s+itemtype="https://schema.org/Question"', c)]

        for qs in q_starts:
            block_end = c.find('</div>', c.find('</div>', qs) + 6) + 6
            block = c[qs:block_end]

            q_match = re.search(r'itemprop="name"[^>]*>(.*?)</h3>', block, re.DOTALL)
            a_match = re.search(r'itemprop="text"[^>]*>(.*?)</div>', block, re.DOTALL)

            if q_match and a_match:
                q_text = q_match.group(1).strip()
                a_text = a_match.group(1).strip()
                # Clean HTML tags
                q_text = re.sub(r'<[^>]+>', '', q_text)
                a_text = re.sub(r'<[^>]+>', '', a_text)
                qa_pairs.append((q_text, a_text))

        if not qa_pairs:
            continue

        # Build JSON-LD
        main_entity = []
        for q_text, a_text in qa_pairs:
            main_entity.append({
                "@type": "Question",
                "name": q_text,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a_text
                }
            })

        faq_json = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entity
        }

        json_ld = '\n<script type="application/ld+json">\n' + json.dumps(faq_json, indent=2, ensure_ascii=False) + '\n</script>\n'

        # Add before </head>
        c = c.replace('</head>', json_ld + '</head>')

        with open(fp, 'w', encoding='utf-8') as fh:
            fh.write(c)
        count += 1
        rel = os.path.relpath(fp, SITE_DIR)
        print(f'CONVERTED: {rel} ({len(qa_pairs)} Q&A pairs)')

print(f'\nTotal converted: {count}')
