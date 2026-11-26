# -*- coding: utf-8 -*-
"""页头 Get Quote 按页面型号指向对应产品价格页。

标准:
  - 文章标题含明确型号 -> 页头 Get Quote 指向该型号 /products/<slug>.html
  - 系列/通用文章       -> /quote.html
  - 只改 <header> 内的那一个 Get Quote; 正文与页脚的 /quote.html 不动
  - 只处理英文 posts/*.html, 中文页不动
  - 页头若缺 Get Quote（老页面的短导航）, 补进 .nav-links, 不改其它导航项

映射来源: scripts/build_article_product_map.py 的 build()（不读 data/ CSV,
因为 data/ 被 .gitignore 排除, CI 上不存在该文件）。

注意: 部署时 .github/scripts/sync_templates.py 会用模板重写所有带
lang-switch 的页头。那里的同名逻辑必须与本脚本一致, 否则本脚本的改动
在部署时被静默回滚。

用法: python scripts/fix_nav_quote.py [--apply]
"""
import os
import re
import sys

# 用 reconfigure 而不是重新包 TextIOWrapper: build_article_product_map
# 在导入时也会重包 stdout, 两次重包会把底层 buffer 关掉。
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

import build_article_product_map as apm  # noqa: E402

HEADER_RE = re.compile(r'<header>.*?</header>', re.DOTALL)
QUOTE_RE = re.compile(r'<a href="[^"]*" class="text-accent">Get Quote</a>')
NAVLINKS_RE = re.compile(r'(<div class="nav-links">)(.*?)(</div>)', re.DOTALL)
ANCHOR = '<a href="%s" class="text-accent">Get Quote</a>'


def main():
    apply = '--apply' in sys.argv
    changed = same = inserted = 0
    problems = []
    for rel, url, match_type, _note in apm.build():
        want = url if match_type == 'model' else '/quote.html'
        text = open(rel, encoding='utf-8').read()
        m = HEADER_RE.search(text)
        if not m:
            problems.append(rel + ' (no <header>)')
            continue
        header = m.group(0)
        new_header, n = QUOTE_RE.subn(ANCHOR % want, header)
        if n == 0:
            # 老短导航没有 Get Quote: 补进 .nav-links 末尾, 其它导航项不动
            new_header, n = NAVLINKS_RE.subn(
                lambda mm: mm.group(1) + mm.group(2) + ANCHOR % want + mm.group(3),
                header)
            if n == 0:
                # `.nav-links` 未闭合的页面（mazak 页如此）: 放在 </nav> 前,
                # 不顺手补 </div> —— 结构修复不属本次范围
                new_header, n = re.subn(r'</nav>', ANCHOR % want + '</nav>',
                                        header, count=1)
            if n == 0:
                problems.append(rel + ' (no .nav-links)')
                continue
            inserted += 1
        if new_header == header:
            same += 1
            continue
        changed += 1
        if apply:
            text = text[:m.start()] + new_header + text[m.end():]
            with open(rel, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
    print(f"{'APPLIED' if apply else 'DRY-RUN'}: changed={changed} already-ok={same} "
          f"inserted={inserted} problems={len(problems)}")
    for p in problems:
        print('  ! ' + p)
    if problems:
        sys.exit(1)


if __name__ == '__main__':
    main()
