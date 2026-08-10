# -*- coding: utf-8 -*-
"""GSC修复 活站验证: stub 301 落点 + 权威页 canonical/hreflang
用法: PYTHONIOENCODING=utf-8 python scripts/verify_live_fix.py
"""
import re, sys, subprocess, concurrent.futures

BASE = 'https://cncdisplay.com'
# (路径, 期望: 跳转落点 或 'canonical-self')
CASES = [
    # M1/M5: zh stub -> EN/zh 权威 (worker 301 或 200+refresh)
    ('/zh/posts/fanuc-cnc-display-troubleshooting-decision-tree.html',
     'https://cncdisplay.com/posts/fanuc-cnc-display-troubleshooting-decision-tree.html'),
    ('/zh/posts/fanuc-display-compatibility-complete-guide.html',
     'https://cncdisplay.com/posts/fanuc-display-compatibility-complete-guide.html'),
    # M3: worker 错配修复
    ('/posts/used-display-recycling-faq-top10-zh.html',
     'https://cncdisplay.com/zh/posts/faq_20260501_CNC_display_replacement_FAQ.html'),
    ('/zh/posts/used-display-recycling-faq-top10-zh.html',
     'https://cncdisplay.com/zh/posts/faq_20260501_CNC_display_replacement_FAQ.html'),
    # 双slug合并: zh stub -> zh权威
    ('/zh/posts/Used_Industrial_Display_Recycling_FAQ_TOP10.html',
     'https://cncdisplay.com/zh/posts/faq_20260501_CNC_display_replacement_FAQ.html'),
    ('/zh/posts/used-display-recycling-faq-top10-zh.html',
     'https://cncdisplay.com/zh/posts/faq_20260501_CNC_display_replacement_FAQ.html'),
    # 权威页: 200 + canonical 自引用
    ('/posts/Used_Industrial_Display_Recycling_FAQ_TOP10.html', 'canonical-self'),
    ('/zh/posts/faq_20260501_CNC_display_replacement_FAQ.html', 'canonical-self'),
    ('/zh/posts/fanuc-0i-display-faq-zh.html', 'canonical-self'),
]

def check(c):
    path, expect = c
    r = subprocess.run(['curl', '-s', '-o', 'NUL', '-w', '%{http_code}', '-L', '--max-redirs', '0',
                        BASE + path], capture_output=True, text=True)
    code = r.stdout.strip()
    if expect == 'canonical-self':
        # 200 + canonical == self
        body = subprocess.run(['curl', '-s', BASE + path], capture_output=True, text=True,
                               encoding='utf-8', errors='replace').stdout
        m = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', body, re.I)
        ok = code == '200' and m and m.group(1).rstrip('/') == (BASE + path).rstrip('/')
        return f'{path}: {code} canonical={m and m.group(1)} {"OK" if ok else "FAIL"}'
    # 301 Location 落点
    loc = subprocess.run(['curl', '-s', '-I', BASE + path], capture_output=True, text=True).stdout
    l = re.search(r'^Location: (.+)$', loc, re.I | re.M)
    locv = l.group(1).strip().rstrip('/') if l else '(none)'
    ok = locv == expect.rstrip('/')
    return f'{path}: {code} -> {locv} {"OK" if ok else f"FAIL(期望 {expect})"}'

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for line in ex.map(check, CASES):
        print(line)
