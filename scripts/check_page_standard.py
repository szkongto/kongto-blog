# -*- coding: utf-8 -*-
"""页面建设标准校验 — docs/site-standards.md 的机器强制。
校验所有 .html：UTF-8 合法性 + 乱码/内码 + 必备 head 元素 + canonical 目录形式 + 语言匹配。
用法: python scripts/check_page_standard.py [--fix] [--quiet]
"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SKIP_DIRS = {'en_bak', '_archive_audit', '_templates', '__pycache__',
             'backlinks_daily', 'backlinks_output', 'node_modules',
             'fonts', 'images', 'output', 'screaming_frog_reports',
             'data', '.git', '.github', 'schema', 'css', 'patches', 'docs', 'workers'}

# 已知 mojibake 模式（Latin-1 误读 UTF-8 的特征序列）
MOJIBAKE_RE = re.compile(r'Ã[\x80-\xbf]|Â[\x80-\xbf]|â€[™"œ]|æ\x80|å\x9c|é\x9a|æ²')

# 非内容页（工件/模板片段，跳过标准校验）
SKIP_PATTERNS = ('audit-verification', 'redirect_audit_report', '-content.html',
                 '_content', 'template-', '-fragment',
                 'google7478b8e743977291', 'baidu_verify', 'BingSiteAuth',
                 'favicon', 'robots.txt', 'indexnow-key')

# HARD(正确性, 门禁拦) / WARN(增强债, 容忍)
HARD = [
    ('charset utf-8', re.compile(r'charset=["\']?utf-8', re.I)),
    ('title', re.compile(r'<title>[^<]+</title>')),
    ('canonical', re.compile(r'rel=["\']canonical["\']')),
]
WARN = [
    ('viewport', re.compile(r'name=["\']viewport')),
    ('description', re.compile(r'name=["\']description')),
    ('hreflang alt', re.compile(r'hreflang=["\']')),
    ('x-default', re.compile(r'hreflang=["\']x-default')),
]


def norm_url(u):
    """规范化 URL 为站点相对路径（去 protocol/host/query/fragment），用于比较。
    如 https://cncdisplay.com/posts/a.html -> /posts/a.html"""
    u = u.strip().split('#')[0].split('?')[0]
    if not u:
        return None
    if '://' in u:
        u = re.sub(r'^[a-z]+://[^/]+', '', u, flags=re.I)
    if not u.startswith('/'):
        u = '/' + u
    return u.rstrip('/') or '/'


def html_files():
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.html') and not any(s in f for s in SKIP_PATTERNS):
                p = os.path.relpath(os.path.join(root, f), '.')
                yield p.replace('\\', '/')


def check_file(rel):
    raw = open(rel, 'rb').read()
    problems = []

    # 1. UTF-8 字节合法性
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError as e:
        problems.append(f'非法UTF-8字节@{e.start}')
        return problems, False
    text = raw.decode('utf-8', errors='replace')

    # 2. 替换字符 / mojibake
    if '�' in text:
        problems.append('含U+FFFD替换字符(乱码)')
    if MOJIBAKE_RE.search(text):
        problems.append('含mojibake模式(编码错读)')

    # 3. 必备 head 元素（hard=缺即拦 / warn=提示）
    for name, rx in HARD:
        if not rx.search(text):
            problems.append(f'[HARD] 缺 {name}')

    # 壳页(meta-refresh 跳转桩)的 viewport/desc/hreflang 无意义, 跳过 warn
    is_shell = 'http-equiv="refresh"' in text
    if not is_shell:
        for name, rx in WARN:
            if not rx.search(text):
                problems.append(f'[WARN] 缺 {name}')

    # 4. canonical 目录形式（不链 /index.html）— hard
    m = re.search(r'rel=["\']canonical["\'] href=["\']([^"\']+)', text)
    if m and m.group(1).endswith('index.html'):
        problems.append(f'[HARD] canonical 用 index.html 形式: {m.group(1)}')

    # 5. lang 与路径匹配 — warn（EN路径含中文内容页属合法，不硬拦；壳页跳过）
    # 精确匹配 zh / zh-XX（区域变体）。用 startswith('zh') 会放走 lang="zh-" 半截值。
    lang_m = re.search(r'<html[^>]*lang=["\']([a-zA-Z-]+)["\']', text)
    is_zh = rel.startswith('zh/')
    ZH_OK = re.compile(r'zh(-[A-Za-z]{2})?$')
    if lang_m and not is_shell:
        lang = lang_m.group(1)
        if is_zh and not ZH_OK.match(lang):
            problems.append(f'[WARN] zh路径但lang={lang}')
        elif not is_zh and ZH_OK.match(lang):
            problems.append(f'[WARN] 非zh路径但lang={lang}')

    # 6. 壳页自循环检测（meta-refresh → 自身 = 死循环，HARD）— 2026-08-09 第7个漏网教训
    # url 值通常无引号包裹（content="0;url=/path"），捕获到引号/边界即止
    refresh_m = re.search(r'http-equiv=["\']refresh["\'][^>]*url=([^"\'>]+)', text, re.I)
    if refresh_m:
        target = norm_url(refresh_m.group(1))
        cur = norm_url('/' + rel)
        if target and cur and target == cur:
            problems.append(f'[HARD] 壳页自循环: refresh→自身 {target}')

    return problems, True


def main():
    fix = '--fix' in sys.argv
    quiet = '--quiet' in sys.argv
    total = hard_bad = warn_bad = 0
    for rel in sorted(html_files()):
        total += 1
        problems, _ = check_file(rel)
        if not problems:
            continue
        hard = [p for p in problems if p.startswith('[HARD]')]
        warn = [p for p in problems if p.startswith('[WARN]')]
        if hard:
            hard_bad += 1
            if not quiet:
                print(f'[HARD] {rel}')
                for p in hard[:6]:
                    print(f'   - {p}')
        if warn:
            warn_bad += 1
    print(f'checked {total} pages, {hard_bad} hard-error, {warn_bad} warn')
    if hard_bad:
        print(f'FAIL: {hard_bad} 页有硬错误（乱码/编码/title/canonical），必须修')
        sys.exit(1)
    if warn_bad:
        print(f'PASS(带债): {warn_bad} 页有增强债（viewport/description/hreflang），列入 backlog')
        sys.exit(0)
    print('PASS: 所有页面符合标准')


if __name__ == '__main__':
    main()
