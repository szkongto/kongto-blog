r"""已归档，勿运行（2026-09-11 从 scripts/ 移入 _archive/one_off_scripts/）。

归档原因：
  1. 路径硬编码 d:\code\seo_deploy —— 同一 remote 的另一份陈旧克隆，不是本
     仓库。今天跑它读写都在那边，对本仓库无影响；但一旦有人把路径改指本仓库，
     它会按下面这些过时内容整体覆写线上页面
  2. 全仓库零引用（含 .github/ 与 scripts/full_gate.py）
  3. 属一次性生成脚本，产物早已上线并被后续修改取代，重跑即回退

  4. 遍历全站 HTML，给缺 Organization schema 的页面插入 schema。该批处理早已
     完成，现在全站页面都带 Organization，重跑无事可做；若判据判断有偏差，
     则会重复插入
"""

"""Add Organization Schema to all pages missing it."""
import os, re

SITE_DIR = r'd:\code\seo_deploy'
SKIP_DIRS = ['.ts', '_templates', '_includes', '.git', '.claude', 'en_bak', 'seo_backup', '__pycache__', '_archive_audit', 'workers']

ORG_SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Kongto Technology",
  "alternateName": ["深圳市江图科技有限公司", "Kongto Technology", "江图科技"],
  "url": "https://cncdisplay.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://cncdisplay.com/images/logo_256.png"
  },
  "foundingDate": "2013",
  "description": "Manufacturer of industrial CNC display CRT-to-LCD retrofit solutions, video signal converters, and custom industrial displays",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Shenzhen",
    "addressRegion": "Guangdong",
    "addressCountry": "CN"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+86-13686889647",
    "email": "info@cncdisplay.com",
    "contactType": "sales",
    "availableLanguage": ["Chinese", "English"]
  }
}
</script>'''

def inject_org_schema(content):
    """Inject Organization Schema before </head>."""
    if 'Organization' in content:
        return None
    # Insert before </head>
    if '</head>' in content:
        pos = content.index('</head>')
        return content[:pos] + '\n' + ORG_SCHEMA + '\n' + content[pos:]
    return None

count = 0
for root, dirs, files in os.walk(SITE_DIR):
    dirs[:] = [d for d in dirs if not any(s in d for s in SKIP_DIRS)]
    for f in files:
        if not f.endswith('.html'): continue
        if any(s in f for s in ['baidu', 'google', 'sitemap']): continue
        fp = os.path.join(root, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()
        result = inject_org_schema(content)
        if result:
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(result)
            count += 1
            print(f'  ADDED: {os.path.relpath(fp, SITE_DIR)}')

print(f'\nTotal Organization Schema added: {count}')
