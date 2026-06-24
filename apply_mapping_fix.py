#!/usr/bin/env python3
"""基于内容比对映射表，修复中英文文章的 hreflang 和 lang-switch 链接。"""
import os, re, json

BASE = r"D:\code\seo_deploy"
MIN_SCORE = 5   # 映射表已是型号优先匹配，低分也接受

def fix_article(filepath, hreflang_zh, hreflang_en, lang_btn_zh, lang_btn_en):
    """修复单篇文章的 hreflang 和 lang-switch 按钮"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except:
        return False, "read-error"

    changes = []

    # 修复 hreflang zh-CN
    m = re.search(r'<link\s+rel="alternate"\s+hreflang="zh-CN"\s+href="([^"]+)"', content)
    if m and m.group(1) != hreflang_zh:
        content = content.replace(m.group(0), f'<link rel="alternate" hreflang="zh-CN" href="{hreflang_zh}"')
        changes.append(f"hreflang zh-CN: {m.group(1)[:50]} -> {hreflang_zh[:50]}")

    # 修复 hreflang en
    m = re.search(r'<link\s+rel="alternate"\s+hreflang="en"\s+href="([^"]+)"', content)
    if m and m.group(1) != hreflang_en:
        content = content.replace(m.group(0), f'<link rel="alternate" hreflang="en" href="{hreflang_en}"')
        changes.append(f"hreflang en: {m.group(1)[:50]} -> {hreflang_en[:50]}")

    # 修复中文按钮
    m = re.search(r'<a\s+href="([^"]*)"\s+lang="zh"\s+class="lang-zh">', content)
    if m:
        old_href = m.group(1)
        # 只有当当前值不对时才改
        if old_href != lang_btn_zh:
            content = content.replace(m.group(0), f'<a href="{lang_btn_zh}" lang="zh" class="lang-zh">')
            changes.append(f"lang-zh btn: {old_href} -> {lang_btn_zh}")

    # 修复英文按钮
    m = re.search(r'<a\s+href="([^"]*)"\s+lang="en"\s+class="lang-en">', content)
    if m:
        old_href = m.group(1)
        if old_href != lang_btn_en:
            content = content.replace(m.group(0), f'<a href="{lang_btn_en}" lang="en" class="lang-en">')
            changes.append(f"lang-en btn: {old_href} -> {lang_btn_en}")

    # 修复 og:url 中的乱码
    m = re.search(r'<meta\s+property="og:url"\s+content="([^"]+)"', content)
    if m and ('%' in m.group(1) or 'CRT' in m.group(1)):
        # og:url 中包含非英文字符（乱码），修复为 canonical URL
        canon = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', content)
        if canon:
            content = content.replace(m.group(0), f'<meta property="og:url" content="{canon.group(1)}" />')
            changes.append("og:url: fixed garbled URL")

    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes

    return False, []

def main():
    # 读取映射表
    with open(os.path.join(BASE, 'article_mapping.json'), 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    print(f"映射表共 {len(mapping)} 对\n")
    print(f"使用最低匹配分: {MIN_SCORE}")
    print()

    fixed = 0
    errors = 0

    for pair in mapping:
        if pair['score'] < MIN_SCORE:
            continue

        zh_path = os.path.join(BASE, pair['zh'].replace('/', os.sep))
        en_path = os.path.join(BASE, pair['en'].replace('/', os.sep))

        zh_url = f"https://cncdisplay.com/{pair['zh']}"
        en_url = f"https://cncdisplay.com/{pair['en']}"
        zh_rel = f"/{pair['zh']}"
        en_rel = f"/{pair['en']}"

        # 修复中文文章
        if os.path.isfile(zh_path):
            ok, changes = fix_article(zh_path, zh_url, en_url, zh_rel, en_rel)
            if ok:
                print(f"  [ZH] {pair['zh']}")
                for c in changes:
                    print(f"       {c}")
                fixed += 1

        # 修复英文文章
        if os.path.isfile(en_path):
            ok, changes = fix_article(en_path, zh_url, en_url, zh_rel, en_rel)
            if ok:
                print(f"  [EN] {pair['en']}")
                for c in changes:
                    print(f"       {c}")
                fixed += 1

    print(f"\n{'='*50}")
    print(f"修复完成: {fixed} 个文件")
    print(f"错误: {errors} 个")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
