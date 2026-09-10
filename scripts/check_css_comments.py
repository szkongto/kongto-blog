# -*- coding: utf-8 -*-
"""CSS 注释完整性门禁 — cncdisplay.com

背景（2026-09-10 事故）：
  破损注释标记 `/* ===== */` 退化成 `/ ===== /`（开头 `*` 丢失）后，
  样式表层出现游离 `/`，浏览器的错误恢复会丢弃它到第一个 `}` 之间的所有规则。
  紧跟其后的规则（如 `.article-hero{background:navy;color:#fff}`）整条失效，
  而下游独立的 `.article-hero h1{color:#fff}` 还在，于是白字叠白底，肉眼才看得出来。
  curl 只看得到文本，看不到被丢弃的渲染规则 —— 所以必须静态拦。
  当时波及 7 篇文章 64 处（commit 9c9820ec + 1b987a88）。

本脚本扫两类目标里的 CSS：
  - css/*.css（整文件）
  - HTML 里的 <style>...</style> 块

判定（按行，带注释状态跟踪，不会把注释体内部的 `/ ` 误报）：
  E1  游离斜杠：不在注释里，且一行以 `/` 开头但不是 `/*`  → 破损注释标记
  E2  注释未闭合：文件或 style 块结束时仍在注释状态
  E3  多余闭合：不在注释里却出现 `*/`

字符串字面量内的 `/*` `*/` 会被跳过，避免误判 `content: "/*"`。

用法：
    python scripts/check_css_comments.py          # 扫全站（git ls-files，尊重 gitignore）
    python scripts/check_css_comments.py -v       # 打印扫描统计
"""

import re
import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

STYLE_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.I | re.S)

# 行首游离斜杠：`/` 后面不是 `*`（`/*` 才是合法注释开头）
BROKEN_LINE_RE = re.compile(r'^\s*/(?!\*)')


def track_lines(text):
    """逐行跑字符状态机。

    返回 (行号, 行内容, 行首状态, 行尾状态, 本行是否出现多余 `*/`) 的列表。
    状态：code / comment / single / double
    """
    out = []
    state = 'code'

    for lineno, line in enumerate(text.split('\n'), start=1):
        start_state = state
        stray_close = False
        i = 0
        n = len(line)
        while i < n:
            ch = line[i]
            nxt = line[i + 1] if i + 1 < n else ''

            if state == 'code':
                if ch == '/' and nxt == '*':
                    state = 'comment'
                    i += 2
                    continue
                if ch == '*' and nxt == '/':
                    # 不在注释里却出现 `*/` —— CSS 解析错误
                    stray_close = True
                    i += 2
                    continue
                if ch == '"':
                    state = 'double'
                elif ch == "'":
                    state = 'single'
            elif state == 'comment':
                if ch == '*' and nxt == '/':
                    state = 'code'
                    i += 2
                    continue
            elif state == 'single':
                if ch == '\\':
                    i += 2
                    continue
                if ch == "'":
                    state = 'code'
            elif state == 'double':
                if ch == '\\':
                    i += 2
                    continue
                if ch == '"':
                    state = 'code'
            i += 1

        out.append((lineno, line, start_state, state, stray_close))

    return out


def check_text(text, label, errors):
    """检查一段 CSS 文本。label 用于报错定位。"""
    if '/*' not in text and '*/' not in text and not BROKEN_LINE_RE.search(text):
        return

    end_state = 'code'
    for lineno, line, start_state, end_state, stray_close in track_lines(text):
        # E1：行首游离斜杠（不在注释里）
        if start_state == 'code' and BROKEN_LINE_RE.match(line):
            errors.append((label, lineno, 'E1 游离斜杠（破损注释标记，缺 `*`）', line.strip()))
        # E3：不在注释里却出现 `*/`
        if stray_close:
            errors.append((label, lineno, 'E3 多余闭合 `*/`（无对应 `/*`）', line.strip()))

    # E2：注释未闭合
    if end_state == 'comment':
        errors.append((label, 0, 'E2 注释未闭合（缺 `*/`）', text.strip().split('\n')[-1][:60]))


def git_files():
    r = subprocess.run(['git', 'ls-files', '-z'], capture_output=True)
    if r.returncode != 0:
        print('!! git ls-files 失败，需在仓库根目录运行', file=sys.stderr)
        sys.exit(1)
    names = r.stdout.decode('utf-8', 'replace').split('\0')
    return [n for n in names if n]


def main():
    verbose = '-v' in sys.argv
    errors = []
    n_html = n_css = 0

    for name in git_files():
        low = name.lower()
        if low.endswith('.css'):
            n_css += 1
            try:
                text = open(name, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            check_text(text, name, errors)
        elif low.endswith('.html'):
            n_html += 1
            try:
                text = open(name, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            for m in STYLE_RE.finditer(text):
                block = m.group(1)
                # 换算成文件内真实行号
                base = text[:m.start(1)].count('\n')
                sub = []
                check_text(block, name, sub)
                for f, ln, kind, snippet in sub:
                    errors.append((f, ln + base if ln else 0, kind, snippet))

    if verbose:
        print(f'扫描: {n_html} 个 HTML, {n_css} 个 CSS')

    if errors:
        print(f'[CSS-COMMENTS] FAIL — {len(errors)} 处', file=sys.stderr)
        for f, ln, kind, snippet in errors[:40]:
            loc = f'{f}:{ln}' if ln else f
            print(f'  {loc}  {kind}', file=sys.stderr)
            if snippet:
                print(f'      {snippet[:90]}', file=sys.stderr)
        if len(errors) > 40:
            print(f'  ... 另有 {len(errors) - 40} 处', file=sys.stderr)
        print('\n危害：游离 `/` 会让浏览器丢弃它到第一个 `}` 之间的规则，'
              '样式静默失效，curl 查不出来。', file=sys.stderr)
        print('修法：把 `/ ===== /` 补回 `/* ===== */`。', file=sys.stderr)
        sys.exit(1)

    print(f'[CSS-COMMENTS] OK — {n_html} 个 HTML + {n_css} 个 CSS，注释标记完整')


if __name__ == '__main__':
    main()
