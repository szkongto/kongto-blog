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
