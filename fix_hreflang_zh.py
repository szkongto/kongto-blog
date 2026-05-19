#!/usr/bin/env python3
"""
修复中文文件的 hreflang="en" 标签
"""
import os
import re
from urllib.parse import quote, unquote

BASE_DIR = r"D:\workspace\kongto-blog"

def fix_chinese_hreflang_en():
    """修复中文文件的 hreflang="en" 标签"""
    fixed = 0
    no_match = 0

    for zh_file in os.listdir(os.path.join(BASE_DIR, 'posts')):
        if not zh_file.endswith('.html'):
            continue

        zh_path = os.path.join(BASE_DIR, 'posts', zh_file)
        with open(zh_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找 hreflang="en" 标签
        en_match = re.search(r'(<link[^>]*hreflang="en"[^>]*href=")([^"]+)(")', content)
        if not en_match:
            continue

        en_href = en_match.group(2)
        en_filename = en_href.split('/en/posts/')[-1] if '/en/posts/' in en_href else ''

        # 检查是否指向中文文件名（错误）
        if any(ord(c) > 127 or c == '%' for c in en_filename):
            # 需要修复：找到对应的英文文件
            matched_en = None
            for en_file in os.listdir(os.path.join(BASE_DIR, 'en/posts')):
                if not en_file.endswith('.html'):
                    continue
                # 检查英文文件的hreflang="zh"是否指向此中文文件
                en_path = os.path.join(BASE_DIR, 'en/posts', en_file)
                with open(en_path, 'r', encoding='utf-8') as f:
                    en_content = f.read()
                zh_url_pattern = f'https://cncdisplay.com/posts/{quote(zh_file, safe="")}'
                if zh_url_pattern in en_content:
                    matched_en = en_file
                    break

            if matched_en:
                new_en_href = f'https://cncdisplay.com/en/posts/{matched_en}'
                old_tag = en_match.group(1) + en_href + en_match.group(3)
                new_tag = en_match.group(1) + new_en_href + en_match.group(3)
                content = content.replace(old_tag, new_tag)
                with open(zh_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed += 1
                print(f"✓ 修复中文: {zh_file[:50]}...")
                print(f"  -> {matched_en}")
            else:
                no_match += 1
                print(f"✗ 无英文对应: {zh_file}")

    return fixed, no_match

def main():
    print("=" * 60)
    print("修复中文文件的 hreflang=\"en\" 标签...")
    print("=" * 60)

    fixed, no_match = fix_chinese_hreflang_en()

    print("\n" + "=" * 60)
    print(f"修复完成: 修复 {fixed} 个, 无匹配 {no_match} 个")
    print("=" * 60)

if __name__ == "__main__":
    main()
