# -*- coding: utf-8 -*-
"""语言切换按钮审计 — pre-commit 门禁
规则: 每个 zh 页的 lang-en 按钮 href 必须:
  1. 指向非 zh/ 路径(英文版)
  2. 目标文件真实存在
退出码: 0=通过, 1=有错
"""
import re
import glob
import os
import sys


def main():
    bad = []
    for f in glob.glob('zh/**/*.html', recursive=True):
        fs = f.replace('\\', '/')
        h = open(f, encoding='utf-8', errors='ignore').read()
        # 找 lang-en 按钮 href (顺序无关)
        m = re.search(r'<a[^>]*href="([^"]+)"[^>]*lang="en"[^>]*>', h) or \
            re.search(r'<a[^>]*lang="en"[^>]*href="([^"]+)"[^>]*>', h)
        if not m:
            continue  # 无按钮, 由注入脚本处理
        url = m.group(1)
        if url.startswith(('http', '/images')):
            continue
        p = url.lstrip('/').split('?')[0]
        # 1) 指向自身或 zh/ → 错
        if url.startswith('/zh/') or url == '/zh':
            bad.append((fs, url, '指向zh/自身'))
            continue
        # 2) 目标不存在 → 错
        if p and not p.endswith('/') and not os.path.isfile(p):
            bad.append((fs, url, '目标文件不存在'))
    if bad:
        print(f'[LANG-SWITCH-CHECK] {len(bad)} 个中文页英文按钮错误:')
        for fs, url, why in bad[:25]:
            print(f'  {fs}\n    {why}: {url}')
        print('\n修复: 让可见 lang-en 按钮照抄 hreflang="en" 目标。参考 scripts/fix_lang_btn.py')
        sys.exit(1)
    print('[LANG-SWITCH-CHECK] OK — 全站中文页英文按钮正确')
    sys.exit(0)


if __name__ == '__main__':
    main()
