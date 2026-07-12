"""Remove return policy text from all visible HTML content."""
import os, re

SITE = r'd:\code\seo_deploy'
SKIP_DIRS = {'.git', 'en_bak', 'worktrees', '__pycache__', 'seo_backup', '_archive_audit', 'node_modules', '.claude'}

# Exact text replacements
REPLACEMENTS = [
    # EN full return lines
    ('<li><strong>30-Day No-Questions-Asked Returns:</strong> Full refund if not satisfied.</li>\n', ''),
    ('<li><strong>30-Day No-Questions-Asked Returns:</strong> Full refund if not satisfied.</li>', ''),
    ('<li>Returns: 30-day no-questions-asked</li>\n', ''),
    ('<li>Returns: 30-day no-questions-asked</li>', ''),

    # ZH full return lines
    ('<li><strong>7天无理由退换：</strong>不满意全额退款。</li>\n', ''),
    ('<li><strong>7天无理由退换：</strong>不满意全额退款。</li>', ''),
    ('<li>退货政策：30天无理由退货</li>\n', ''),
    ('<li>退货政策：30天无理由退货</li>', ''),

    # Article table return rows
    ('<tr><td>Return Policy</td><td>30-Day no-questions-asked return (resaleable condition)</td></tr>', ''),
    ('<tr><td>Return Policy</td><td>30-Day no-questions-asked return —full refund if unsatisfied</td></tr>', ''),
    ('<tr><td>退换政策</td><td>30 天无理由退换，不满意全额退款</td></tr>', ''),

    # Article list items
    ('<li>7天无理由退换 — 不满意全额退款</li>', ''),

    # Article tagline
    ('<p style="font-size:0.95em;margin-top:12px"><strong>500+ Enterprises Worldwide &nbsp;·&nbsp; 18-Month Warranty &nbsp;·&nbsp; 30-Day Return &nbsp;·&nbsp; Lifetime Support</strong></p>', ''),
]

# Table row with 30-Day no-reason return
RE_TABLE_ROW = re.compile(r'<tr><td>\s*30-Day No-Reason Return\s*</td><td>\s*Full Refund if Not Satisfied\s*</td></tr>', re.IGNORECASE)

# ZH FAQ about return/refund
ZH_RETURN_QA = re.compile(
    r'<div class="faq-item">\s*<div class="faq-q"><strong>Q:\s*如果买回去发现不兼容，可以退货吗？</strong></div>\s*<div class="faq-a">.*?</div>\s*</div>',
    re.DOTALL
)

count = 0
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()
        orig = content

        # Exact text replacements
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)

        # Regex table row
        content = RE_TABLE_ROW.sub('', content)

        # Clean up empty table rows after removal
        content = re.sub(r'<tr>\s*<td[^>]*></td>\s*<td[^>]*></td>\s*</tr>', '', content)

        if content != orig:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            rel = os.path.relpath(fp, SITE)
            print(f'FIXED: {rel}')

print(f'\nTotal: {count} files modified')
