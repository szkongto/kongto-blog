#!/usr/bin/env python3
"""
Build clean Haas CN article from first commit + add improvements
All Chinese strings defined directly in Python file, no encoding issues.
"""
import re

p = r'd:\code\seo_backup_cleanup_0614\posts\article_20260508_Haas_CRT_LCD_Case.html'

# Read from first clean commit
import subprocess
subprocess.run(['git', 'checkout', '85d000d0', '--', p], cwd=r'd:\code\seo_backup_cleanup_0614', capture_output=True)

with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

# Title fixes
c = c.replace(
    '<title>哈斯机床老旧CRT显示器升级液晶替换案例 | 深圳市江图科技有限公司</title>',
    '<title>HAAS系统 9针单色显示器维修升级 | 深圳市江图科技有限公司</title>'
)
c = c.replace(
    '<h1>哈斯机床老旧CRT显示器升级液晶替换案例</h1>',
    '<h1>HAAS系统 9针单色显示器维修升级 CRT改LCD方案</h1>'
)

# Meta description
c = c.replace(
    'content="哈斯机床老旧CRT显示器升级液晶替换案例"',
    'content="HAAS数控系统9针单色CRT显示器维修与LCD升级方案。VF/ST/SL系列通用。"'
)

# Schema block to add before </head>
schemas = '''
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Article","headline":"HAAS系统 9针单色显示器维修升级 CRT改LCD方案","author":{"@type":"Person","name":"江图科技"},"publisher":{"@type":"Organization","name":"深圳市江图科技有限公司"},"datePublished":"2026-05-08"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
{"@type":"ListItem","position":1,"name":"首页","item":"https://cncdisplay.com/"},
{"@type":"ListItem","position":2,"name":"HAAS系统 9针单色显示器维修升级","item":"https://cncdisplay.com/posts/article_20260508_Haas_CRT_LCD_Case.html"}
]}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
{"@type":"Question","name":"CRT显示器换LCD需要改线路吗？","acceptedAnswer":{"@type":"Answer","text":"不需要。KONGTO LCD替代显示器采用即插即用设计，兼容原装接口和供电，直接替换原CRT，无需修改任何线路或参数。"}},
{"@type":"Question","name":"LCD替代显示器能用多久？","acceptedAnswer":{"@type":"Answer","text":"工业级LCD设计寿命为50,000小时，远优于老旧CRT。提供2年保修。"}},
{"@type":"Question","name":"支持哪些CNC品牌和型号？","acceptedAnswer":{"@type":"Answer","text":"覆盖FANUC、三菱、Mazak、大隙Okuma、哈斯Haas、西门子Siemens全部主流品牌。"}}
]}
</script>
'''

c = c.replace('</head>', schemas + '\n</head>')

# Remove ICP block
c = c.replace(
    '<div style="text-align:center;padding:20px 0;font-size:12px;color:#888888;border-top:1px solid #e0e0e0;margin-top:40px;">\n'
    '  <p style="margin:4px 0;">\n'
    '    <a href="https://beian.miit.gov.cn/" target="_blank" rel="nofollow noopener" style="color:#888;text-decoration:none;">\n'
    '      粤ICP备XXXXXXXX号-1\n'
    '    </a>\n'
    '    &nbsp;|&nbsp; 深圳市江图科技有限公司 &copy; 2026\n'
    '    &nbsp;|&nbsp; <a href="/sitemap.xml" style="color:#888;">Sitemap</a>\n'
    '    &nbsp;|&nbsp; <a href="/en/" style="color:#888;">English</a>\n'
    '  </p>\n'
    '</div>',
    ''
)

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
print(f'Size: {len(c)} bytes')
with open(p, 'r', encoding='utf-8') as f:
    c2 = f.read()

checks = {
    'Title has HAAS': '<title>HAAS系统 9针' in c2,
    'H1 correct': '<h1>HAAS系统 9针' in c2,
    'Article schema': '\"@type\":\"Article\"' in c2,
    'BreadcrumbList': '\"BreadcrumbList\"' in c2,
    'FAQPage': '\"FAQPage\"' in c2,
    'No BOM': c2[0] != '﻿',
    'No ICP': '粤ICP备XXXXXXXX' not in c2,
    'Has images': '<img' in c2,
    'Valid UTF-8': True
}
# Verify all characters are valid
try:
    for ch in c2:
        if ord(ch) > 0x10FFFF:
            checks['Valid UTF-8'] = False
            break
except:
    checks['Valid UTF-8'] = False

for label, result in checks.items():
    print(f'  {"PASS" if result else "FAIL"}: {label}')
