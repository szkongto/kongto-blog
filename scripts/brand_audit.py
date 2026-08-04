#!/usr/bin/env python3
"""Check brand redirects for better targets."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = set(os.listdir(os.path.join(ROOT, 'posts')))

checks = [
    (92, 'press_release FANUC LCD', ['Beijing_Zhongbo_FANUC_LCD_Upgrade_Press_Release', 'press_release']),
    (101, 'FANUC CRT to LCD guide', ['FANUC_CRT_Maintenance_vs_LCD_Upgrade', 'fanuc-crt-to-lcd-step-by-step']),
    (102, 'FANUC CRT to LCD case', ['Beijing_Zhongbo_FANUC_LCD_Upgrade_Press_Release', 'FANUC_CRT_Maintenance']),
    (120, 'FANUC CRT vs LCD cost comparison', ['comparison_20260501_fanuc_crt_vs_lcd', 'fanuc_crt_vs_lcd']),
    (124, 'FANUC 0i FAQ solutions', ['fanuc-0i-display-faq', 'fanuc_0i_display_faq']),
    (234, 'FANUC CRT to LCD guide', ['FANUC_CRT_Maintenance_vs_LCD_Upgrade', 'fanuc-crt-to-lcd-step-by-step']),
    (235, 'FANUC CRT to LCD case', ['Beijing_Zhongbo_FANUC_LCD_Upgrade_Press_Release']),
    (239, 'FANUC CRT vs LCD comparison', ['comparison_20260501_fanuc_crt_vs_lcd']),
    (286, 'fanuc-om-d-display product', ['fanuc-om', 'fanuc-0m']),
    (290, 'fanuc-0m-0t product', ['fanuc-0m', 'fanuc-0t']),
    (291, 'fanuc-16i-18i-21i product', ['fanuc-16i', 'fanuc-18i', 'fanuc-21i']),
    (292, 'fanuc-a61l-0001-0077 product', ['fanuc-a61l-0001-0077']),
    (293, 'fanuc-a61l-0001-0078 product', ['fanuc-a61l-0001-0078']),
    (294, 'fanuc-a61l-0001-0087 product', ['fanuc-a61l-0001-0087']),
    (295, 'fanuc-a61l-0001-0136 product', ['fanuc-a61l-0001-0136']),
]

print('=== BRAND PAGE REDIRECTS WITH REAL TARGETS ===')
found = 0
for line, desc, search_terms in checks:
    matches = []
    for term in search_terms:
        for f in posts:
            if term.lower() in f.lower():
                matches.append(f)
                break
    if matches:
        found += 1
        print('  Line %d: %s -> FOUND: %s' % (line, desc, matches[0]))
    else:
        print('  Line %d: %s -> NO MATCH (brand redirect acceptable)' % (line, desc))
print()
print('Total brand redirects with better targets: %d' % found)

# Siemens ROI article check
print()
print('=== Siemens ROI article check ===')
siemens_files = [f for f in posts if 'siemens' in f.lower() and ('roi' in f.lower() or 'cost' in f.lower())]
print('  Siemens cost/ROI files: %s' % siemens_files)

# Check products directory for FANUC models that redirect to brand page
products = set(os.listdir(os.path.join(ROOT, 'products')))
print()
print('=== FANUC product pages that exist ===')
fanuc_products = sorted([f for f in products if 'fanuc-a61l' in f.lower()])
for f in fanuc_products:
    print('  %s' % f)

# Check okuma products
print()
print('=== Okuma product pages ===')
okuma_products = sorted([f for f in products if 'okuma' in f.lower()])
for f in okuma_products:
    print('  %s' % f)
