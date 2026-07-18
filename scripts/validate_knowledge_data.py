"""Validate knowledge base articles against master product data.
Run: python scripts/validate_knowledge_data.py
If it prints errors, fix before committing.
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load master product specs
with open(os.path.join(BASE, 'scripts', 'product_specs.json'), 'r', encoding='utf-8') as f:
    specs = json.load(f)

# Knowledge articles with expected product references
ARTICLES = {
    'fanuc-crt-to-lcd-replacement-guide.html': [
        'fanuc-a61l-0001-0072-lcd-upgrade',
        'fanuc-a61l-0001-0074-lcd-upgrade',
        'fanuc-a61l-0001-0092-lcd-upgrade',
        'fanuc-a61l-0001-0093-lcd-upgrade',
        'fanuc-a61l-0001-0094-lcd-upgrade',
        'fanuc-a61l-0001-0096-lcd-upgrade',
        'fanuc-a61l-0001-0097-lcd-upgrade',
    ],
    'mitsubishi-cnc-display-replacement-guide.html': [
        'mitsubishi-mdt962b-lcd-upgrade',
        'mitsubishi-mdt925ps-lcd-upgrade',
        'mitsubishi-mdt947b-lcd-upgrade',
        'mitsubishi-fcua-ct100-lcd-upgrade',
        'mitsubishi-bm09df-lcd-upgrade',
    ],
    'mazak-crt-to-lcd-retrofit-guide.html': [
        'mazak-cd1472-lcd-upgrade',
        'mazak-mdt1283b-lcd-upgrade',
        'mazak-dr5614-lcd-upgrade',
        'mazak-aiqa8dsp40-lcd-upgrade',
        'mazak-c5470ns-lcd-upgrade',
    ],
    'siemens-crt-to-lcd-upgrade-guide.html': [
        'siemens-6fc3988-7fa20-lcd-upgrade',
        'siemens-6fc5103-lcd-upgrade',
        'siemens-sm0901-lcd-upgrade',
        'siemens-sm1200-lcd-upgrade',
    ],
    'haas-crt-monitor-replacement-guide.html': [
        'haas-9-pin-monochrome-lcd-upgrade',
        'haas-9pin-mono-crt-lcd-upgrade',
        'haas-12inch-9pin-crt-lcd-upgrade',
        'haas-28hm-nm4-lcd-upgrade',
    ],
    'okuma-crt-to-lcd-replacement-guide.html': [
        'okuma-osp5000-lcd-upgrade',
        'okuma-osp5020-lcd-upgrade',
        'okuma-osp7000-crt-lcd-upgrade',
    ],
}

errors = 0
for article, product_keys in ARTICLES.items():
    path = os.path.join(BASE, 'knowledge', article)
    if not os.path.exists(path):
        print(f'ERROR: {article} not found')
        errors += 1
        continue

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    for pk in product_keys:
        if pk not in specs:
            print(f'WARN: {pk} not in master specs')
            continue
        spec = specs[pk]
        # Check article mentions correct CRT size
        crt_keyword = spec['crt'].split()[0]  # e.g. "14-inch" from "14-inch Color CRT"
        lcd_keyword = spec['lcd'].split()[0]  # e.g. "12.1-inch" from "12.1-inch TFT-LCD"

        if crt_keyword not in html:
            print(f'ERROR: {article} missing CRT size "{crt_keyword}" for {pk}')
            errors += 1
        if lcd_keyword not in html:
            print(f'ERROR: {article} missing LCD size "{lcd_keyword}" for {pk}')
            errors += 1

if errors:
    print(f'\nFAILED: {errors} data errors found. Fix before commit.')
    sys.exit(1)
else:
    print('OK: All knowledge articles match master product specs.')
