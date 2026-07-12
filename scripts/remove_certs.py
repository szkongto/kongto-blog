"""Remove all certification mentions, replace with reliability testing statement."""
import os, re

SITE = r'd:\code\seo_deploy'
SKIP_DIRS = {'.git', 'en_bak', 'worktrees', '__pycache__', 'seo_backup', '_archive_audit', 'node_modules', '.claude'}

# Reliability statement to ADD where certs were removed
RELIABILITY_EN = 'All units undergo 100% factory testing: 48-hour high-temperature aging (55°C) and vibration test before shipment. Proven reliability with thousands of customer deployments. Every display uses brand-new industrial-grade LCD panels. 2-year warranty, lifetime support.'
RELIABILITY_ZH = '出厂前100%经过48小时高温老化（55°C）及振动测试，确保长期运行稳定。方案成熟，累积大量客户实战案例，所有显示器均为全新工业液晶屏，二年质保，售后无忧！'

# Patterns to remove (certification/qualification related)
CERT_PATTERNS = [
    # Full certification table/sections
    (r'<h2[^>]*>资质与认证</h2>.*?(?=<h2|</section>|</main>|$)', ''),
    (r'<h2[^>]*>Certifications[^<]*</h2>.*?(?=<h2|</section>|</main>|$)', ''),
    (r'<h3[^>]*>资质与认证</h3>.*?(?=<h3|<h2|</section>|</main>|$)', ''),
    (r'<h3[^>]*>Certifications[^<]*</h3>.*?(?=<h3|<h2|</section>|</main>|$)', ''),
    # Certification tables
    (r'<table[^>]*>.*?(CE.*?RoHS.*?FCC.*?ISO.*?IP65).*?</table>', ''),
    (r'<table[^>]*>.*?(CE.*?质量管理体系).*?</table>', ''),
    # Specific cert mentions in paragraphs/lists
    (r'<li>[^<]*CE[^<]*认证[^<]*</li>', ''),
    (r'<li>[^<]*RoHS[^<]*</li>', ''),
    (r'<li>[^<]*FCC[^<]*</li>', ''),
    (r'<li>[^<]*ISO 9001[^<]*</li>', ''),
    (r'<li>[^<]*IP65[^<]*</li>', ''),
    (r'<li>[^<]*防护等级[^<]*</li>', ''),
    (r'<li>[^<]*industrial protection[^<]*</li>', ''),
    # CE/RoHS/FCC/ISO inline mentions
    (r'CE（欧盟强制性安全认证）[^<]*', ''),
    (r'CE\s*\(?European\)?[^)]*\)?\s*(certification|认证)', ''),
    (r'RoHS（有害物质限制指令）[^<]*', ''),
    (r'RoHS[^<]*(?:compliant|directive|有害物质)', ''),
    (r'FCC（美国联邦通信委员会）[^<]*', ''),
    (r'FCC[^<]*(?:certification|认证|compliance)', ''),
    (r'ISO 9001[^:]*:[^<]*质量管理体系[^<]*', ''),
    (r'ISO 9001[^<]*(?:certification|quality)', ''),
    (r'IP65[^<]*防护[^<]*', ''),
    (r'前面板 IP65[^<]*', ''),
    # General cert/qualification mentions
    (r'产品符合欧盟[^。]*。', ''),
    (r'符合[^。]*RoHS[^。]*。', ''),
    (r'通过[^。]*认证[^。]*。', ''),
    (r'已通过[^。]*认证[^。]*。', ''),
]

# Also remove common cert table structures
CERT_HTML_BLOCKS = [
    'CE（欧盟强制性安全认证）',
    'RoHS（有害物质限制指令）',
    'FCC（美国联邦通信委员会）',
    'ISO 9001:2015',
    '工业防护等级',
    '前面板 IP65',
]

# Specific ZH cert phrases to find and remove
ZH_CERT_PATTERNS = [
    '资质与认证',
    '产品认证',
    '认证标准',
    'CE认证',
    'FCC认证',
    'RoHS认证',
    'ISO9001',
    'ISO 9001',
    'IP65防护等级',
    '防护等级IP65',
    'European safety certification',
    '有害物质限制',
    '电磁兼容',
]

def has_cert_content(text):
    """Quick check if file likely has cert content"""
    text_lower = text.lower()
    cert_keywords = ['ce ', ' rohs', 'fcc ', 'iso 9001', 'ip65', '资质', '认证', '防护等级']
    return any(kw in text_lower for kw in cert_keywords)

count = 0
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()

        if not has_cert_content(content):
            continue

        orig = content

        # Remove certification table rows
        # Pattern: Certification/standard table with CE/RoHS/FCC/ISO rows
        content = re.sub(r'<tr[^>]*>\s*<td[^>]*>(?:CE|RoHS|FCC|ISO 9001|工业防护等级|前面板 IP65)[^<]*</td>.*?</tr>', '', content, flags=re.DOTALL)

        # Remove full cert tables
        content = re.sub(r'<table[^>]*certif[^>]*>.*?</table>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<table[^>]*认证[^>]*>.*?</table>', '', content, flags=re.DOTALL)
        content = re.sub(r'<table[^>]*qualif[^>]*>.*?</table>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Remove cert list items
        for pattern, _ in CERT_PATTERNS:
            if pattern:
                content = re.sub(pattern, '', content, flags=re.DOTALL)

        # Remove cert section headings + their content
        for heading in ['资质与认证', 'Certifications', '产品认证', '认证标准']:
            # Remove <h2>heading</h2>... up to next <h2> or end
            content = re.sub(
                rf'<h[23][^>]*>{heading}</h[23]>.*?(?=<h[23]|</section>|</main>|$)',
                '', content, flags=re.DOTALL
            )

        # Remove individual cert mention paragraphs
        cert_paragraphs = [
            r'产品符合欧盟健康、安全与环保标准[^<]*',
            r'无铅焊接工艺[^<]*',
            r'电磁兼容性[^<]*',
            r'规范化来料检验[^<]*',
            r'前面板 IP65 防尘防水[^<]*',
        ]
        for p in cert_paragraphs:
            content = re.sub(p, '', content)

        # Clean up empty lines and excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        if content != orig:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            rel = os.path.relpath(fp, SITE)
            print(f'FIXED: {rel}')

print(f'\nTotal files modified: {count}')

# Now add reliability statement to about.html and author.html only (main cert pages)
print('\nAdding reliability statements...')
for rel in ['about.html', 'zh/about.html']:
    fp = os.path.join(SITE, rel)
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    orig = c
    is_zh = '/zh/' in rel

    # Add reliability section before warranty/service section
    reliability_text = RELIABILITY_ZH if is_zh else RELIABILITY_EN
    # Find a good insertion point - before footer or warranty
    insert_before = '</main>'

    rel_section = f'''<section style="background:#f0f7ff;padding:24px;border-radius:12px;margin:2rem 0;">
    <h2>{"可靠性测试" if is_zh else "Reliability Testing"}</h2>
    <p>{reliability_text}</p>
</section>
    </main>'''

    c = c.replace(insert_before, rel_section)
    if c != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'ADDED reliability: {rel}')
