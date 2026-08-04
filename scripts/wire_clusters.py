# -*- coding: utf-8 -*-
"""Topic Cluster 编织 — MDT962B / CD1472 / DR5614（同 0093 模式）
支柱=产品页；卫星首段插精准锚文本 CTA 指支柱；支柱尾部加 Related Resources
"""
import os

SIG = 'class="cluster-cta"'


def cta(pillar, anchor):
    return ('<p class="cluster-cta" style="margin:1.2rem 0;padding:0.9rem 1rem;'
            'background:#f0f7ff;border-left:4px solid #2a5298;border-radius:6px;font-size:0.95em">'
            'Looking for the complete solution? See our <a href="' + pillar + '" '
            'style="color:#1e3c72;font-weight:600">' + anchor + '</a> '
            '— plug-and-play, no rewiring, 2-year warranty.</p>\n')


def related_block(title, items):
    lis = '\n'.join('<li><a href="%s">%s</a></li>' % (href, label) for href, label in items)
    return ('<div id="related-resources" style="background:#f8fafc;border:1px solid #e1e8ed;'
            'border-radius:8px;padding:1.2rem 1.4rem;margin:1.5rem 0">\n'
            '<h2 style="border:none;margin-bottom:0.8rem">%s</h2>\n<ul style="line-height:1.9">\n%s\n</ul>\n</div>\n'
            % (title, lis))


CLUSTERS = [
    {
        'name': 'MDT962B',
        'pillar': '/products/mitsubishi-mdt962b-lcd-upgrade.html',
        'sats': [
            ('posts/article_20260506_mitsubishi_mdt962b_crt_lcd_replacement.html',
             'Mitsubishi MDT962B LCD replacement'),
            ('posts/article_20260506_Mitsubishi_MDT962B_Industrial_LCD_CRT_Replacement.html',
             'Mitsubishi MDT962B CRT to LCD replacement'),
            ('posts/article_20260523_Mitsubishi_MDT962B_Series_CRT_LCD_Upgrade_Solution.html',
             'Mitsubishi MDT962B LCD upgrade solution'),
            ('posts/mitsubishi-mdt962b-cnc-crt-to-lcd-upgrade-guide.html',
             'Mitsubishi MDT962B CNC LCD upgrade guide'),
        ],
        'related_title': 'Mitsubishi MDT962B — Related Resources',
        'related': [
            ('/posts/article_20260506_Mitsubishi_MDT962B_Industrial_LCD_CRT_Replacement.html',
             'Mitsubishi MDT962B CRT to LCD Replacement Guide'),
            ('/posts/article_20260523_Mitsubishi_MDT962B_Series_CRT_LCD_Upgrade_Solution.html',
             'Mitsubishi MDT962B Series CRT to LCD Upgrade Solution'),
            ('/posts/article_20260506_mitsubishi_mdt962b_crt_lcd_replacement.html',
             'Mitsubishi MDT962B CRT Replacement'),
            ('/posts/mitsubishi-mdt962b-cnc-crt-to-lcd-upgrade-guide.html',
             'Mitsubishi MDT962B CNC Upgrade Guide'),
        ],
    },
    {
        'name': 'CD1472',
        'pillar': '/products/mazak-cd1472-lcd-upgrade.html',
        'sats': [
            ('posts/article_20260507_Mazak_CD1472D1M_LCD_Replacement.html',
             'MAZAK CD1472-D1M LCD replacement'),
        ],
        'related_title': 'MAZAK CD1472-D1M — Related Resources',
        'related': [
            ('/posts/article_20260507_Mazak_CD1472D1M_LCD_Replacement.html',
             'MAZAK CD1472-D1M LCD Replacement'),
            ('/docs/mazak-cd1472-crt-lcd-display.pdf',
             'Download MAZAK CD1472 CRT to LCD PDF Guide'),
        ],
    },
    {
        'name': 'DR5614',
        'pillar': '/products/mazak-dr5614-lcd-upgrade.html',
        'sats': [
            ('posts/Mazak_DR5614_LCD_CNC_CRT_Replacement.html',
             'MAZAK DR5614 LCD replacement'),
        ],
        'related_title': 'MAZAK DR5614 — Related Resources',
        'related': [
            ('/posts/Mazak_DR5614_LCD_CNC_CRT_Replacement.html',
             'MAZAK DR5614 LCD CNC CRT Replacement'),
        ],
    },
]

for c in CLUSTERS:
    # 卫星 → 支柱
    for sat, anchor in c['sats']:
        if not os.path.isfile(sat):
            print('MISS:', sat)
            continue
        h = open(sat, encoding='utf-8', errors='ignore').read()
        if SIG in h:
            print('SKIP 已有CTA:', sat)
            continue
        if '</header>' in h:
            h = h.replace('</header>', '</header>\n' + cta(c['pillar'], anchor), 1)
            open(sat, 'w', encoding='utf-8', newline='\n').write(h)
            print('CTA:', sat)
        else:
            print('FAIL 无header:', sat)
    # 支柱 → 卫星
    if not os.path.isfile(c['pillar']):
        print('MISS pillar:', c['pillar'])
        continue
    hp = open(c['pillar'], encoding='utf-8', errors='ignore').read()
    if 'id="related-resources"' in hp:
        print('SKIP 已有Related:', c['pillar'])
        continue
    if '</main>' in hp:
        hp = hp.replace('</main>', related_block(c['related_title'], c['related']) + '</main>', 1)
        open(c['pillar'], 'w', encoding='utf-8', newline='\n').write(hp)
        print('Related:', c['pillar'])
    else:
        print('FAIL 无</main>:', c['pillar'])
