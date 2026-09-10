"""扫描全站 HTML，找出 JSON-LD 里 URL 被写成双反斜杠的文件。

背景：部分页面 /zh/posts/* 的 JSON-LD `"url"` 字段误把路径分隔符写成 `\\`
（例如 https://cncdisplay.com/zh/posts\\article_xxx.html），
爬虫解析后拿到的是非法 URL，结构化数据等于失效。

用法：
    python scripts/audit_backslash_urls.py           # 只报告
    python scripts/audit_backslash_urls.py --fix     # 就地修复并打印改动
"""

import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'node_modules', '_templates'}
# 匹配 cncdisplay.com 之后任一位置出现两个连续反斜杠的 URL
PATTERN = re.compile(r'cncdisplay\.com[^\s"]*\\\\[^\s"]*')


def iter_html():
    for p in ROOT.rglob('*.html'):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def main():
    fix = '--fix' in sys.argv
    total_files = 0
    total_hits = 0
    for p in sorted(iter_html()):
        try:
            text = p.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        hits = PATTERN.findall(text)
        if not hits:
            continue
        total_files += 1
        total_hits += len(hits)
        rel = str(p.relative_to(ROOT)).replace('\\', '/')
        print(f'{rel}: {len(hits)}')
        for h in hits:
            print(f'    {h}')
        if fix:
            new = PATTERN.sub(lambda m: m.group(0).replace('\\\\', '/'), text)
            p.write_text(new, encoding='utf-8')
    print(f'--- files: {total_files}, hits: {total_hits} ---')
    if fix:
        print('已就地修复')


if __name__ == '__main__':
    main()
