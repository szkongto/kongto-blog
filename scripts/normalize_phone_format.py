# -*- coding: utf-8 -*-
"""一次性脚本：全站统一联系电话格式为 +86-13686889647（数据源 data/company-info.json）。
仅处理 HTML 文件；wa.me/8613686889647 的 WhatsApp 数字格式保持不动。
用法: python scripts/normalize_phone_format.py [--dry-run]
"""
import os, re, sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CANON = "+86-13686889647"
SKIP_DIRS = {'en_bak', '_archive_audit', '_templates', '__pycache__',
             'backlinks_daily', 'backlinks_output', 'node_modules',
             'fonts', 'images', 'output', 'data', '.git', '.github', 'seo_reports'}

# 按从长到短替换（互斥，防二次包装）
RULES = [
    (re.compile(r'\+86-136-8688-9647'), CANON),        # 连字符分组展示(带+86)
    (re.compile(r'86-136-8688-9647'), CANON),          # 连字符分组展示(无+86)
    (re.compile(r'\+86\s+136\s+8688\s+9647'), CANON),  # 空格分组展示
    (re.compile(r'\+8613686889647'), CANON),           # tel:/展示 无连字符
    (re.compile(r'\+86\s+13686889647'), CANON),        # 单个空格
    (re.compile(r'(?<![\d])136-8688-9647'), CANON),    # 裸连字符展示
    (re.compile(r'(?<![\d-])13686889647(?!\d)'), CANON),  # 裸号(地址块)加前缀; 前有数字/-则跳过(wa.me/idempotent)
]

def scan():
    files = []
    for root, dirs, names in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP_DIRS]
        for n in names:
            if n.endswith('.html'):
                files.append(os.path.relpath(os.path.join(root, n), '.').replace('\\', '/'))
    return files

def main():
    dry = '--dry-run' in sys.argv
    total = changed = 0
    for rel in scan():
        total += 1
        with open(rel, encoding='utf-8') as f:
            txt = f.read()
        new = txt
        hits = 0
        for rx, rep in RULES:
            new, n = rx.subn(rep, new)
            hits += n
        if new != txt:
            if not dry:
                with open(rel, 'w', encoding='utf-8') as f:
                    f.write(new)
            changed += 1
            print(f'{rel}: {hits} 处')
    print(f'\nscanned {total} html, changed {changed}{" (dry-run)" if dry else ""}')

if __name__ == '__main__':
    main()
