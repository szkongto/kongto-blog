# -*- coding: utf-8 -*-
"""新页面脚手架 — 从标准模板生成，创建即合规。
用法:
  python scripts/scaffold_page.py --path posts/my-article.html --title "My Title" [--lang en|zh]
  python scripts/scaffold_page.py --path products/x.html --title "X" --lang zh

生成标准骨架(UTF-8/canonical目录形式/hreflang中英/样式/导航占位)。建完跑 full_gate 校验。
"""
import os, sys, argparse, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TPL = os.path.join(ROOT, '_templates', 'page-template.html')


def twin_path(path):
    """返回另一语言孪生路径: zh/x → x, x → zh/x"""
    if path.startswith('zh/'):
        return path[3:]
    return 'zh/' + path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', required=True, help='页面路径，如 posts/x.html 或 zh/posts/x.html')
    ap.add_argument('--title', required=True, help='页面标题')
    ap.add_argument('--desc', default='', help='meta description')
    ap.add_argument('--lang', default='auto', choices=['en', 'zh', 'auto'], help='语言')
    args = ap.parse_args()

    path = args.path.lstrip('/')
    if not path.endswith('.html'):
        path += '.html'
    lang = args.lang
    if lang == 'auto':
        lang = 'zh' if path.startswith('zh/') else 'en'

    abs_path = os.path.join(ROOT, path)
    if os.path.exists(abs_path):
        print(f'[ERR] 已存在: {path}')
        sys.exit(1)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    canon = 'https://cncdisplay.com/' + path
    if path.endswith('/index.html'):
        canon = canon.replace('/index.html', '/')
    tpl = open(TPL, encoding='utf-8').read()
    alt_lang = 'zh-CN' if lang == 'en' else 'en'
    alt_url = 'https://cncdisplay.com/' + twin_path(path)
    alt_url = alt_url.replace('/index.html', '/')

    page = (tpl.replace('__LANG__', lang if lang == 'en' else 'zh-CN')
               .replace('__TITLE__', args.title)
               .replace('__DESCRIPTION__', args.desc)
               .replace('__CANONICAL__', canon)
               .replace('__ALT_LANG__', alt_lang)
               .replace('__ALT_URL__', alt_url)
               .replace('__H1__', args.title))
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'✓ 生成: {path} ({lang})')
    print(f'  canonical: {canon}')
    print(f'  孪生 hreflang: {alt_lang} {alt_url}')
    print('\n下一步:')
    print('  1. 填 __CONTENT__ / 导航栏')
    print('  2. 建中英孪生: python scripts/scaffold_page.py --path <twin> --title ...')
    print('  3. 补 5 入口 (posts index/brand/products)')
    print('  4. python scripts/full_gate.py --quick')
    print('  5. curl 活站验证')


if __name__ == '__main__':
    main()
