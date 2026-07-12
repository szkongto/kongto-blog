"""Remove ALL return/refund policy text from visible HTML content."""
import os, re

SITE = r'd:\code\seo_deploy'
SKIP_DIRS = {'.git', 'en_bak', 'worktrees', '__pycache__', 'seo_backup', '_archive_audit', 'node_modules', '.claude'}

REPLACEMENTS = [
    # EN
    ('<td>30-Day No-Reason Return, Full Refund if Not Satisfied</td>', '<td>2-Year Warranty</td>'),
    # ZH visible lines
    ('7天无理由退换', '2年质保'),
    ('不满意7天无理由退换', '2年质保'),
    ('退货政策：30天无理由退货', '质保：2年'),
    # Full ZH warranty lines containing return policy
    ('<strong>2年质保</strong> - 终身技术支持 - 7天无理由退换 - 全球免运费', '<strong>2年质保</strong> - 终身技术支持 - 全球免运费'),
    ('<strong>2年质保</strong> &mdash; 终身技术支持 &mdash; 7天无理由退换 &mdash; 全球免运费', '<strong>2年质保</strong> &mdash; 终身技术支持 &mdash; 全球免运费'),
    # ZH tagline
    ('2年超长质保 · 7天无理由退换 · 终身技术支持', '2年超长质保 · 终身技术支持'),
    # ZH article warranty section
    ('提供<strong>2年免费质保</strong>（行业最长），非人为损坏免费换新。终身免费电话和远程视频指导，7天无理由退换。如遇质量问题，联系客服后即可安排换新。',
     '提供<strong>2年免费质保</strong>（行业最长），非人为损坏免费换新。终身免费电话和远程视频指导。如遇质量问题，联系客服后即可安排换新。'),
    ('✅ 1年免费质保 | ✅ 7×24小时技术响应 | ✅ 不满意7天无理由退换 | ✅ 全国包邮',
     '✅ 1年免费质保 | ✅ 7×24小时技术响应 | ✅ 全国包邮'),
    # ZH HAAS brand FAQ
    ('<strong>7天无理由退换</strong>', '<strong>2年质保</strong>'),
    # ZH quote FAQ
    ('我们提供7天无理由退换货保障。如果因产品本身质量问题或不兼容导致无法使用，可申请全额退款或免费更换合适型号。退货产生的运费由买家承担（质量问题除外）。',
     '我们提供2年质保，非人为损坏免费换新。'),
]

count = 0
files_touched = set()
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()
        orig = content
        for old, new in REPLACEMENTS:
            if old in content:
                content = content.replace(old, new)
        if content != orig:
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(content)
            files_touched.add(fp)
            count += 1

print(f'Files modified: {count}')
for fp in sorted(files_touched):
    rel = os.path.relpath(fp, SITE)
    print(f'  {rel}')
