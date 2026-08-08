#!/usr/bin/env python3
"""
Unify navigation and footer across all cncdisplay.com HTML pages.
Phase 1: Standard nav with correct lang-switch URLs
Phase 6: Standard footer
"""
import os, re, sys

BASE = r'd:\code\seo_deploy'

# ---- Standard Nav Templates ----
ZH_NAV = '''    <header>
        <nav>
            <a href="/" class="logo">江图科技</a>
            <div class="nav-links">
                <a href="/">首页</a><a href="/compatibility-matrix.html">兼容查询</a>
                <a href="/posts/">文章</a>
                <a href="/case-studies.html">案例</a>
                <a href="/docs/">下载</a>
                <a href="/about.html">关于</a>
                <a href="/quote.html" style="color:#ff9800;font-weight:700;">获取报价</a>
            </div>
            <a href="/search.html" class="nav-search">🔍 搜索</a>
            <div class="lang-switch">
                <a href="{zh_url}" lang="zh" class="lang-zh">中文</a>
                <span class="divider">|</span>
                <a href="{en_url}" lang="en" class="lang-en">English</a>
            </div>
        </nav>
    </header>'''

EN_NAV = '''    <header>
        <nav>
            <a href="/en/" class="logo">Kongto Technology</a>
            <div class="nav-links">
                <a href="/en/">Home</a><a href="/en/compatibility-matrix.html">Compatibility</a>
                <a href="/en/posts/">Articles</a>
                <a href="/en/case-studies.html">Cases</a>
                <a href="/en/docs/">Downloads</a>
                <a href="/en/about.html">About</a>
                <a href="/en/quote.html" style="color:#ff9800;font-weight:700;">Get Quote</a>
            </div>
            <a href="/en/search.html" class="nav-search">🔍 Search</a>
            <div class="lang-switch">
                <a href="{zh_url}" lang="zh" class="lang-zh">中文</a>
                <span class="divider">|</span>
                <a href="{en_url}" lang="en" class="lang-en">English</a>
            </div>
        </nav>
    </header>'''

# ---- Standard Footer Templates ----
ZH_FOOTER = '''    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">江图科技 Kongto Technology</span>
                <p>专注工业视频显示解决方案 — CNC显示器CRT转LCD升级、工业视频信号转换器、非标定制工控显示器</p>
            </div>
            <div class="footer-links">
                <a href="/posts/">📄 技术文章</a>
                <a href="/brands/FANUC.html">FANUC方案</a>
                <a href="/brands/Mitsubishi.html">三菱方案</a>
                <a href="/brands/Siemens.html">西门子方案</a>
                <a href="/docs/">资料下载</a>
                <a href="/about.html">关于我们</a>
            </div>
            <p class="footer-copy">© 2013-2026 深圳市江图科技有限公司 | 龙岗区横岗街道深坑综合楼2号楼C栋4楼 | 13686889647 | szkongto01@foxmail.com</p>
        </div>
    </footer>'''

EN_FOOTER = '''    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">Kongto Technology 江图科技</span>
                <p>Industrial Video Display Solutions — CNC CRT-to-LCD Retrofit, Video Signal Converters, Custom Industrial Displays</p>
            </div>
            <div class="footer-links">
                <a href="/en/posts/">📄 Articles</a>
                <a href="/en/brands/FANUC.html">FANUC</a>
                <a href="/en/brands/Mitsubishi.html">Mitsubishi</a>
                <a href="/en/brands/Siemens.html">Siemens</a>
                <a href="/en/docs/">Downloads</a>
                <a href="/en/about.html">About Us</a>
            </div>
            <p class="footer-copy">© 2013-2026 Kongto Technology | Shenzhen, Guangdong, China | +86-13686889647 | szkongto01@foxmail.com</p>
        </div>
    </footer>'''


def get_urls(filepath):
    """Calculate correct zh-CN and en URLs for lang-switch based on file path."""
    rel = os.path.relpath(filepath, BASE).replace('\\', '/')
    is_en = rel.startswith('en/')

    if is_en:
        # en/ page: zh-CN = strip en/ prefix
        zh_path = '/' + rel[3:]  # remove 'en/'
        en_path = '/' + rel
    else:
        # zh-CN page: en = add en/ prefix
        zh_path = '/' + rel
        en_path = '/en/' + rel

    # Clean up index.html references
    if zh_path.endswith('/index.html'):
        zh_path = zh_path[:-10]  # strip 'index.html'
    if en_path.endswith('/index.html'):
        en_path = en_path[:-10]

    # Handle special case: root index
    if zh_path == '/index.html':
        zh_path = '/'
    if en_path == '/en/index.html':
        en_path = '/en/'

    return zh_path, en_path


def replace_nav(content, filepath):
    """Replace the navigation header in content."""
    zh_url, en_url = get_urls(filepath)
    is_en = os.path.relpath(filepath, BASE).replace('\\', '/').startswith('en/')
    nav_template = EN_NAV if is_en else ZH_NAV
    new_nav = nav_template.format(zh_url=zh_url, en_url=en_url)

    # Strategy: Find the <header> or first <nav> and replace everything
    # up to </header> or the <main> tag

    # Pattern 1: <header>...</header> exists
    header_pattern = re.compile(r'(\s*)<header>.*?</header>', re.DOTALL)
    match = header_pattern.search(content)
    if match:
        return content[:match.start()] + new_nav + content[match.end():]

    # Pattern 2: <nav>...</nav> without header wrapper
    nav_pattern = re.compile(r'(\s*)<nav>.*?</nav>', re.DOTALL)
    match = nav_pattern.search(content)
    if match:
        return content[:match.start()] + new_nav + content[match.end():]

    # Pattern 3: No recognizable nav - insert before <main> or first <section>
    main_match = re.search(r'(\s*)<main', content)
    if main_match:
        return content[:main_match.start()] + new_nav + '\n' + content[main_match.start():]

    # Pattern 4: Insert after <body>
    body_match = re.search(r'(<body[^>]*>)', content)
    if body_match:
        return content[:body_match.end()] + '\n' + new_nav + content[body_match.end():]

    return content


def replace_footer(content, filepath):
    """Replace the footer in content."""
    is_en = os.path.relpath(filepath, BASE).replace('\\', '/').startswith('en/')
    footer_template = EN_FOOTER if is_en else ZH_FOOTER

    # Find <footer>...</footer>
    footer_pattern = re.compile(r'(\s*)<footer>.*?</footer>', re.DOTALL)
    match = footer_pattern.search(content)
    if match:
        return content[:match.start()] + footer_template + content[match.end():]

    # If no footer, insert before </body>
    body_close = re.search(r'(\s*)(</body>)', content)
    if body_close:
        return content[:body_close.start()] + '\n' + footer_template + '\n' + content[body_close.start():]

    return content


def process_file(filepath, fix_nav=True, fix_footer=False):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    if fix_nav:
        content = replace_nav(content, filepath)

    if fix_footer:
        content = replace_footer(content, filepath)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def find_html_files():
    """Find all HTML files to process."""
    html_files = []
    for root, dirs, files in os.walk(BASE):
        # Skip special dirs
        dirs[:] = [d for d in dirs if d not in ('.git', '_archive_audit', '_archive_seo_backup_0613_0329', '_archive_seo_backup_cleanup_0614', 'node_modules', 'backlinks_daily', 'backlinks_output')]
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    return html_files


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--nav', action='store_true', help='Fix navigation')
    parser.add_argument('--footer', action='store_true', help='Fix footer')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change')
    parser.add_argument('--files', nargs='*', help='Specific files to process')
    args = parser.parse_args()

    if not args.nav and not args.footer:
        args.nav = True  # default: fix nav

    if args.files:
        html_files = [os.path.join(BASE, f) for f in args.files]
    else:
        html_files = find_html_files()

    changed = 0
    for fpath in sorted(html_files):
        if not os.path.exists(fpath):
            print(f"  SKIP (not found): {fpath}")
            continue
        try:
            if process_file(fpath, fix_nav=args.nav, fix_footer=args.footer):
                rel = os.path.relpath(fpath, BASE)
                print(f"  FIXED: {rel}")
                changed += 1
        except Exception as e:
            print(f"  ERROR: {fpath}: {e}")

    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {changed} files")


if __name__ == '__main__':
    main()
