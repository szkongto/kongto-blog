"""核验 llms-full.txt 的计数头与实际条目数、以及与 sitemap.xml 的覆盖差。

背景：llms-full.txt 头部写 "Total indexed pages: 241"，但实际 `- [` 条目 283 条；
同时它可能整体过期，漏掉 sitemap 里已有的页面。AI 爬虫读计数头判断站点规模，
写错会直接误导 GEO 抓取策略。

用法：
    python scripts/audit_llms_full.py
"""

import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LLMS = ROOT / 'llms-full.txt'
SITEMAP = ROOT / 'sitemap.xml'

ENTRY = re.compile(r'^- \[([^\]]*)\]\((https://cncdisplay\.com[^)]*)\)', re.M)
HEADER_COUNT = re.compile(r'Total indexed pages:\s*(\d+)')
SECTION = re.compile(r'^## (.+?)(?:\s*\((\d+)\))?$', re.M)


def main():
    text = LLMS.read_text(encoding='utf-8')
    entries = ENTRY.findall(text)
    urls = [u for _, u in entries]

    m = HEADER_COUNT.search(text)
    header_n = int(m.group(1)) if m else None

    print(f'llms-full.txt 实际条目: {len(entries)}')
    print(f'llms-full.txt 头部声明: {header_n}')
    print(f'差值: {len(entries) - (header_n or 0)}')

    # 小节标题里括号声明的条数 vs 该节实际条数
    print('\n=== 小节声明数 vs 实际数 ===')
    lines = text.splitlines()
    sec = None
    sec_start = 0
    bounds = []
    for i, ln in enumerate(lines):
        if ln.startswith('## '):
            if sec is not None:
                bounds.append((sec, sec_start, i))
            sm = re.match(r'## (.+?)(?:\s*\((\d+)\))?$', ln)
            sec = (sm.group(1), int(sm.group(2)) if sm.group(2) else None)
            sec_start = i
    if sec is not None:
        bounds.append((sec, sec_start, len(lines)))
    for (name, declared), s, e in bounds:
        n = sum(1 for ln in lines[s:e] if ENTRY.match(ln))
        flag = '' if declared is None or declared == n else '  <== 不一致'
        print(f'{name}: 声明={declared} 实际={n}{flag}')

    # sitemap 差集
    sm_text = SITEMAP.read_text(encoding='utf-8')
    sm_urls = set(re.findall(r'<loc>([^<]+)</loc>', sm_text))
    llms_urls = set(urls)

    print(f'\nsitemap locs: {len(sm_urls)}')
    print(f'llms-full 去重 URL: {len(llms_urls)}')

    missing = sorted(sm_urls - llms_urls)
    extra = sorted(llms_urls - sm_urls)
    print(f'\n=== sitemap 有、llms-full 缺 ({len(missing)}) ===')
    for u in missing[:80]:
        print(f'  {u}')
    if len(missing) > 80:
        print(f'  ... 另 {len(missing) - 80} 条')
    print(f'\n=== llms-full 有、sitemap 无 ({len(extra)}) ===')
    for u in extra[:40]:
        print(f'  {u}')
    if len(extra) > 40:
        print(f'  ... 另 {len(extra) - 40} 条')


if __name__ == '__main__':
    main()
