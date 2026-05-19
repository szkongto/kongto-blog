#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规范化文章中的URL（将绝对URL转换为相对URL）
"""

import re
import os

# 文章目录
POSTS_DIR = r'./posts'  # 改成相对路径，或者保留你原来的路径
# 要替换的URL模式
# 要替换的URL模式
URL_PATTERNS = [
    ('https://szkongto.github.io/kongto-blog/', '/'),
    ('http://szkongto.github.io/kongto-blog/', '/'),
]

def normalize_urls_in_file(filepath, filename):
    """规范化文件中的URL"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 不替换的内容：
    # - canonical link (应该是绝对URL)
    # - og:url (应该是绝对URL)
    # - schema.org url (应该是绝对URL)
    # - share buttons 中的URL (应该是绝对URL)

    # 只替换文章内容中的内部链接（不包括meta标签和JSON-LD）
    # 找到 </head> 位置，之后的内容中的链接可以替换
    head_end = content.find('</head>')
    if head_end == -1:
        print(f'  ⚠ 未找到</head>: {filename}')
        return False

    # 分离head和body
    head = content[:head_end]
    body = content[head_end:]

    # 在body中替换绝对URL为相对URL
    for abs_url, rel_url in URL_PATTERNS:
        # 替换 posts 链接
        body = body.replace(abs_url + 'posts/', '/kongto-blog/posts/')
        body = body.replace(abs_url, rel_url)

    # 重新组合
    new_content = head + body

    if new_content == original_content:
        print(f'  ✓ 无需修改: {filename}')
        return False

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  ✓ 已规范化URL: {filename}')
    return True

def main():
    print('开始规范化文章中的URL...\n')

    # 获取所有HTML文件
    html_files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.html')]
    html_files.sort()

    success_count = 0
    skip_count = 0

    for filename in html_files:
        filepath = os.path.join(POSTS_DIR, filename)
        print(f'处理: {filename}')

        if normalize_urls_in_file(filepath, filename):
            success_count += 1
        else:
            skip_count += 1

    print(f'\n完成！')
    print(f'  成功修改: {success_count} 篇')
    print(f'  无需修改: {skip_count} 篇')

if __name__ == '__main__':
    main()
