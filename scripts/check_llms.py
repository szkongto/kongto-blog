"""校验 llms.txt / llms-full.txt 里每个 URL 都是真的活页。

背景（2026-09-11 实测）：
  - `llms-full.txt` 长期手工维护、没有生成器，漂移到 283 条（头写 241），
    385 条 sitemap URL 缺 244 条，反过来列了 103 条 sitemap 外的 URL，
    抽样 curl 多为 301 死链，还有 baidu 验证文件 —— 等于把死链喂给 AI 爬虫。
  - `llms.txt` 有两处指向 `https://cncdisplay.com/guides/`，该路径没有
    index.html，活站 404。

根因：`sitemap.xml` 有门禁约束，这两个文件没有。

本脚本是那道门禁。三条规则，全部离线可跑（不依赖网络）：

  规则 1  每个 cncdisplay.com URL 都要能映射到本地存在的文件
  规则 2  每个 URL 都要在 sitemap.xml 里（sitemap 是权威清单）
  规则 3  llms-full.txt 必须与 `gen_llms_full.py --check` 一致

规则 2 的例外写在 EXEMPT 里，必须逐条写理由。例外是有意为之，不是漏网。

用法：
    python scripts/check_llms.py          # 校验，有问题退出 1
    python scripts/check_llms.py -v       # 多打印一些过程信息
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://cncdisplay.com'

URL_RE = re.compile(r'https://cncdisplay\.com/[A-Za-z0-9._/#-]*')

TARGETS = [
    ROOT / 'llms.txt',
    ROOT / 'llms-full.txt',
]

# 规则 2 的例外：故意不进 sitemap 的页面。
# 判据 —— sitemap 的读者是 Google，llms.txt 的读者是 AI 爬虫，受众不同。
EXEMPT = {
    'https://cncdisplay.com/usa-cnc-monitor-replacement.html':
        'geo 门页，刻意 noindex 出 sitemap（给 Google 看会重复，给 AI 爬虫看是有效内容）',
    'https://cncdisplay.com/germany-cnc-display-retrofit.html':
        'geo 门页，同上',
    'https://cncdisplay.com/uk-cnc-monitor-replacement.html':
        'geo 门页，同上',
    'https://cncdisplay.com/japan-cnc-display-retrofit.html':
        'geo 门页，同上',
}


def load_sitemap_urls():
    text = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    return {u.strip() for u in re.findall(r'<loc>([^<]+)</loc>', text)}


def url_to_file(url: str):
    path = url[len(SITE):].split('#')[0].split('?')[0]
    path = path.lstrip('/')
    if path == '' or path.endswith('/'):
        path += 'index.html'
    return ROOT / path


def extract_urls(text: str):
    """取出文件里的所有站点 URL，去掉 fragment。"""
    out = []
    for m in URL_RE.finditer(text):
        u = m.group(0).rstrip('.,)')
        u = u.split('#')[0]
        if u not in out:
            out.append(u)
    return out


def main():
    verbose = '-v' in sys.argv
    sitemap = load_sitemap_urls()
    problems = []

    for target in TARGETS:
        if not target.exists():
            problems.append(f'{target.name}: 文件不存在')
            continue
        urls = extract_urls(target.read_text(encoding='utf-8'))
        print(f'{target.name}: {len(urls)} 个 URL')

        for u in urls:
            fp = url_to_file(u)

            # 规则 1：本地文件必须存在
            if not fp.exists():
                problems.append(
                    f'{target.name}: 映射不到本地文件 -> {u}  (期望 {fp.relative_to(ROOT)})')
                continue

            # 规则 2：必须在 sitemap 里，除非在 EXEMPT
            if u not in sitemap and u not in EXEMPT:
                problems.append(
                    f'{target.name}: 不在 sitemap 中 -> {u}  '
                    f'（若为有意为之，加进 check_llms.py 的 EXEMPT 并写理由）')

            elif verbose:
                mark = 'EXEMPT' if u in EXEMPT else 'in-sitemap'
                print(f'    ok [{mark}] {u}')

    # 规则 3：llms-full.txt 必须与生成器一致
    gen = ROOT / 'scripts' / 'gen_llms_full.py'
    if gen.exists():
        r = subprocess.run([sys.executable, str(gen), '--check'],
                           cwd=str(ROOT), capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            problems.append('llms-full.txt 与 gen_llms_full.py --check 结果不一致')

    if problems:
        print(f'\n[LLMS-CHECK] FAIL — {len(problems)} 个问题', file=sys.stderr)
        for p in problems:
            print(f'  - {p}', file=sys.stderr)
        print('\n修法：', file=sys.stderr)
        print('  llms-full.txt 漂移 -> python scripts/gen_llms_full.py --write', file=sys.stderr)
        print('  llms.txt 死链      -> 手工改成真实存在的页面 URL', file=sys.stderr)
        sys.exit(1)

    print('\n[LLMS-CHECK] OK — llms.txt / llms-full.txt 全部 URL 均为真实活页')


if __name__ == '__main__':
    main()
