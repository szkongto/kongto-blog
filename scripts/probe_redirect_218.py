# -*- coding: utf-8 -*-
"""GSC「网页会自动重定向」218条 实证: 抽样检查 301 状态+落点+目标有效性"""
import subprocess, urllib.parse, sys

BASE = 'https://cncdisplay.com'
SAMPLE = [
    '/en/docs',
    '/en/terms.html',
    '/en/posts/fanuc-0i-display-faq-solutions-zh.html',
    '/en/posts/article_20260501_工业视频信号转换器在CNC数控系统中的应用.html',
    '/en/products/fanuc-a61l-0001-0078-lcd-upgrade.html',
    '/en/brands/FANUC.html',
    '/brands/FANUC',
    '/posts/fanuc-0i-display-faq-solutions-zh.html',
    '/zh/products/9mvb3-0a/',
    '/posts/Custom_Industrial_Display_Series.htmlarticle_20260508_KTV148_Custom_Industrial_Display.html',
    '/posts/article_20260506_三菱MDT962B工业液晶显示器CRT替代方案.html',
    '/docs/CNC_to_LCD_Model_List.docx',
    '/posts/非标订制显示器系列.html',
    '/posts/video-signal-converter-buying-guide-zh.html',
    '/posts/article_20260507_Mazak_CD1472D1M_LCD.html',
    '/zh/posts/article_20260507_Mazak_CD1472D1M_LCD_Replacement.html',
    '/en/posts/article_20260507_Mazak_CD1472D1M_LCD_upgrade.html',
    '/posts/article_20260507_Mazak_CD1472D1M_LCD_upgrade.html',
]


def curl(url, follow=False, head=False):
    cmd = ['curl', '-s', '-o', 'NUL', '-w', '%{http_code}',
           '-L' if follow else '--max-redirs', '0' if not follow else '',
           url]
    if head:
        cmd = ['curl', '-s', '-I', '--max-redirs', '0', url]
    # build clean command
    cmd = ['curl', '-s', '-o', 'NUL', '-w', '%{http_code}']
    if follow:
        cmd += ['-L']
    else:
        cmd += ['--max-redirs', '0']
    r = subprocess.run(cmd + [url], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r.stdout.strip()


def location(url):
    r = subprocess.run(['curl', '-s', '-I', '--max-redirs', '0', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    for line in r.stdout.splitlines():
        if line.lower().startswith('location:'):
            return line.split(':', 1)[1].strip()
    return '(no Location)'


for p in SAMPLE:
    url = BASE + p
    code = curl(url)
    loc = location(url) if code in ('301', '302', '307', '308') else '-'
    final = ''
    if code in ('301', '302', '307', '308'):
        dest = loc if loc.startswith('http') else BASE + loc
        final = curl(dest, follow=True)
    print(f'{code} | {p}\n       -> {loc} [final={final}]')
