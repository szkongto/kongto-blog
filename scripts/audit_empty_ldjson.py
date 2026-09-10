"""扫描全站 HTML，找出空的或未闭合的 JSON-LD script 块。

背景：部分页面出现 `<script type="application/ld+json"></script>` 这种空块，
或连续的 `</script><script type="application/ld+json">` 空转，
Google 会把它当作无效结构化数据块，可能拖累整页 schema 解析。

用法：
    python scripts/audit_empty_ldjson.py
"""

import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'node_modules', '_templates'}

EMPTY_BLOCK = re.compile(
    r'<script\s+type="application/ld\+json"\s*>\s*</script>', re.I)
ADJACENT = re.compile(
    r'</script>\s*<script\s+type="application/ld\+json"\s*>\s*</script>', re.I)


def main():
    empty_files = []
    adjacent_files = []
    for p in sorted(ROOT.rglob('*.html')):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        rel = str(p.relative_to(ROOT)).replace('\\', '/')
        n_empty = len(EMPTY_BLOCK.findall(text))
        n_adj = len(ADJACENT.findall(text))
        if n_adj:
            adjacent_files.append((rel, n_adj))
        if n_empty:
            empty_files.append((rel, n_empty))
    print('=== 相邻空块 </script><script ...></script> ===')
    for rel, n in adjacent_files:
        print(f'{rel}: {n}')
    print(f'小计 {len(adjacent_files)} 文件')
    print('=== 空 JSON-LD 块 ===')
    for rel, n in empty_files:
        print(f'{rel}: {n}')
    print(f'小计 {len(empty_files)} 文件')


if __name__ == '__main__':
    main()
