"""从 sitemap.xml 重新生成 llms-full.txt。

背景：llms-full.txt 此前靠手工维护，没有生成器，已经严重漂移——
头部声明 241 页，实际 283 条（含 39 条重复），且 385 条 sitemap URL 里有
244 条缺失；反过来它列出的 103 条 URL 不在 sitemap 中，抽样实测多为
301 重定向（如 article_20260501_*.html、heidenhain-be211 等），
另有 baidu 验证文件。等于把死链喂给 AI 爬虫，属于 GEO 负资产。

sitemap.xml 是已被门禁约束的权威清单，因此以它为唯一数据源重建。

用法：
    python scripts/gen_llms_full.py            # 预览统计，不写文件
    python scripts/gen_llms_full.py --write    # 写入 llms-full.txt
    python scripts/gen_llms_full.py --check    # 门禁用：与重新生成结果不一致则退出 1
"""

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITEMAP = ROOT / 'sitemap.xml'
OUT = ROOT / 'llms-full.txt'
SITE = 'https://cncdisplay.com'

TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)

HEADER = """# cncdisplay.com - Full Site Content Index

## Kongto Technology (Jiangtu Technology)
Industrial Video Display Solutions - CNC CRT-to-LCD Retrofit, Video Signal Converters, Custom Industrial Displays
Total indexed pages: {count}
"""

# 顶层路径段 -> 小节标题
EN_SECTIONS = [
    ('', 'Main Pages'),
    ('brands', 'Brand Pages'),
    ('products', 'Product Pages'),
    ('posts', 'Articles'),
    ('docs', 'Documentation'),
    ('guides', 'Guides'),
    ('knowledge', 'Knowledge Base'),
    ('hub', 'Hub Pages'),
]
SECTION_ORDER = [name for _, name in EN_SECTIONS]


def url_to_file(url: str):
    """把 sitemap URL 映射到本地文件路径。"""
    path = url[len(SITE):]
    if path.startswith('/'):
        path = path[1:]
    if path == '' or path.endswith('/'):
        path += 'index.html'
    return ROOT / path


def read_title(fp: pathlib.Path, fallback: str) -> str:
    try:
        text = fp.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return fallback
    m = TITLE_RE.search(text)
    if not m:
        return fallback
    title = html.unescape(m.group(1)).strip()
    title = re.sub(r'\s+', ' ', title)
    return title or fallback


def classify(url: str):
    """返回 (小节标题, 排序键)。中文页归到同名小节但排在英文之后。"""
    path = url[len(SITE):].strip('/')
    if not path:
        return 'Main Pages', 0
    parts = path.split('/')
    is_zh = parts[0] == 'zh'
    if is_zh:
        parts = parts[1:]
    seg = parts[0] if len(parts) > 1 else ''
    if seg == '' or len(parts) == 1:
        base = 'Main Pages'
    else:
        base = dict(EN_SECTIONS).get(seg, 'Other Pages')
    if base == 'Other Pages' and seg:
        base = seg.replace('-', ' ').title()
    return base, (1 if is_zh else 0)


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    text = SITEMAP.read_text(encoding='utf-8')
    urls = re.findall(r'<loc>([^<]+)</loc>', text)
    urls = [u.strip() for u in urls]
    urls = list(dict.fromkeys(urls))  # 去重且保序

    buckets = {}
    missing_file = []
    for u in urls:
        sec, lang = classify(u)
        fp = url_to_file(u)
        if not fp.exists():
            missing_file.append((u, str(fp.relative_to(ROOT))))
        title = read_title(fp, u)
        buckets.setdefault((sec, lang), []).append((title, u))

    lines = [HEADER.format(count=len(urls)).rstrip('\n'), '']
    for sec in SECTION_ORDER + sorted(set(k[0] for k in buckets) - set(SECTION_ORDER)):
        for lang in (0, 1):
            items = buckets.get((sec, lang))
            if not items:
                continue
            label = sec if lang == 0 else f'{sec} (中文)'
            lines.append(f'## {label} ({len(items)})')
            for title, u in items:
                lines.append(f'- [{title}]({u})')
            lines.append('')

    out = '\n'.join(lines).rstrip('\n') + '\n'

    print(f'sitemap URL: {len(urls)}')
    print(f'分节: {len([k for k in buckets])}')
    for (sec, lang), items in sorted(buckets.items()):
        print(f'  {sec}{" (中文)" if lang else ""}: {len(items)}')
    if missing_file:
        print(f'\n!! 映射不到本地文件 ({len(missing_file)}):')
        for u, f in missing_file[:20]:
            print(f'  {u}  ->  {f}')

    if write:
        OUT.write_text(out, encoding='utf-8')
        print(f'\n已写入 {OUT.relative_to(ROOT)} ({len(out)} 字节)')
        return

    if check:
        # 门禁用：文件必须与「以 sitemap 为源重新生成」的结果逐字节一致。
        # 不一致说明有人在手工改它，或者 sitemap 变了没重新生成 —— 两种都要拦。
        current = OUT.read_text(encoding='utf-8') if OUT.exists() else ''
        if current == out:
            print(f'[LLMS-FULL] OK — 与 sitemap 重新生成的结果一致（{len(urls)} 条）')
            return
        cur_urls = set(re.findall(r'\((https://cncdisplay\.com[^)]*)\)', current))
        new_urls = set(re.findall(r'\((https://cncdisplay\.com[^)]*)\)', out))
        print('[LLMS-FULL] FAIL — llms-full.txt 与 sitemap 不同步', file=sys.stderr)
        print(f'  磁盘条目 {len(cur_urls)} 条 / 重新生成 {len(new_urls)} 条', file=sys.stderr)
        stale = sorted(cur_urls - new_urls)
        missing = sorted(new_urls - cur_urls)
        if stale:
            print(f'  应删除的陈旧 URL {len(stale)} 条:', file=sys.stderr)
            for u in stale[:15]:
                print(f'    - {u}', file=sys.stderr)
            if len(stale) > 15:
                print(f'    ... 另有 {len(stale) - 15} 条', file=sys.stderr)
        if missing:
            print(f'  应补充的 URL {len(missing)} 条:', file=sys.stderr)
            for u in missing[:15]:
                print(f'    + {u}', file=sys.stderr)
            if len(missing) > 15:
                print(f'    ... 另有 {len(missing) - 15} 条', file=sys.stderr)
        print('  修法：python scripts/gen_llms_full.py --write', file=sys.stderr)
        sys.exit(1)

    print('\n预览模式，未写文件。加 --write 落盘，加 --check 做门禁校验。')


if __name__ == '__main__':
    main()
