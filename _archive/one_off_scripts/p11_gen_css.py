#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1-1 articles batch — regenerate CSS guard block from ACTUAL usage.

Scans converted real posts -> (class -> set of element tags). Emits:
  1. bare defs for every class that lacks one (incl. REUSED classes that have
     NO base def in style.css)
  2. guards spanning ALL wrapper scopes (.post / article / main / .container /
     none) with element+class compounds that beat element-bearing base rules
     (max base specificity = `.post .content figure img` = (0,3,1)).

Usage: python p11_gen_css.py > block.css   (then splice into style.css)
"""
import os, re, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from article_class_map import RANKMAP, REUSED, STANDALONE  # noqa: E402

SHELL_RE = re.compile(r'http-equiv=["\']\s*refresh', re.I)
ALL = set(RANKMAP[r][0] for r in RANKMAP) | set(STANDALONE)

def class_defs():
    d = {c: decl for _, (c, decl) in RANKMAP.items()}
    d.update(STANDALONE)
    return d

def base_css_has(cls):
    css = open(os.path.join(ROOT, 'css/style.css'), encoding='utf-8').read()
    base = css.split('/* P1-1 article batch')[0]
    return re.search(r'(?:^|[,}\s])\.' + re.escape(cls) + r'\s*\{', base) is not None

def scan_tags():
    """cls -> set of tags it appears on across converted real posts."""
    usage = collections.defaultdict(set)
    for sub in ('posts', 'zh/posts'):
        for p in glob.glob(os.path.join(ROOT, sub, '*.html')):
            if os.path.basename(p) == 'index.html':
                continue
            h = open(p, encoding='utf-8').read()
            if SHELL_RE.search(h):
                continue
            for m in re.finditer(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*\bclass="([^"]+)"', h):
                tag = m.group(1).lower()
                for c in m.group(2).split():
                    if c in ALL:
                        usage[c].add(tag)
    return usage

def guards_for(cls, tags):
    """Build full-scope guard selector list for class on given tags."""
    scopes = ['.post', 'article', 'main', '.container']
    sels = set()
    for t in tags:
        sels.add(f'{t}.{cls}')                      # (0,1,1)
        sels.add(f'.content {t}.{cls}')             # (0,2,1)
        for s in scopes:
            sels.add(f'{s} {t}.{cls}')              # (0,2,1)/(0,1,2)
            sels.add(f'{s} .content {t}.{cls}')     # (0,3,1)/(0,2,2)
        for ctx in ('.product-images', '.product-card', '.table-wrap',
                    '.table-responsive', '.img-comparison'):
            sels.add(f'{ctx} {t}.{cls}')            # (0,2,1)
            for s in scopes:
                sels.add(f'{s} {ctx} {t}.{cls}')
                sels.add(f'{s} .content {ctx} {t}.{cls}')
        if t == 'img':
            sels.add(f'figure {t}.{cls}')
            sels.add(f'.content figure {t}.{cls}')  # (0,3,1)
            for s in scopes:
                sels.add(f'{s} figure {t}.{cls}')
                sels.add(f'{s} .content figure {t}.{cls}')  # (0,4,1)
        if t == 'table':
            sels.add(f'.table-wrap {t}.{cls}')
            sels.add(f'.table-responsive {t}.{cls}')
    return ','.join(sorted(sels))

def main():
    decls = class_defs()
    usage = scan_tags()
    print('/* P1-1 article batch — utility classes + full-scope guards */')
    for rank in sorted(RANKMAP):
        cls, d = RANKMAP[rank]
        if cls in STANDALONE:
            continue
        if cls in REUSED and base_css_has(cls):
            continue  # base def exists, guard only
        print(f'.{cls} {{ {d} }}')
    for cls in sorted(STANDALONE):
        print(f'.{cls} {{ {decls[cls]} }}')
    print()
    for cls in sorted(decls):
        tags = usage.get(cls)
        if not tags:
            print(f'/* !! {cls}: no usage found, no guard */')
            continue
        print(f'{guards_for(cls, tags)} {{ {decls[cls]} }}')
    print('/* end P1-1 */')

if __name__ == '__main__':
    main()
