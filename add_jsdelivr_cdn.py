#!/usr/bin/env python3
"""
jsDelivr CDN 加速配置脚本 v2
将博客中的静态资源链接替换为 jsDelivr CDN 链接
支持 Windows 路径
"""

import os
import re
import fnmatch

REPO = "szkongto/kongto-blog"
BRANCH = "main"
CDN_BASE = f"https://cdn.jsdelivr.net/gh/{REPO}@{BRANCH}"

# 需要替换的规则 (old_pattern, new_pattern)
REPLACEMENTS = [
    # CSS 引用
    (
        r'href="/kongto-blog/css/',
        f'href="{CDN_BASE}/css/'
    ),
    # 图片引用
    (
        r'src="/kongto-blog/images/',
        f'src="{CDN_BASE}/images/'
    ),
]

def find_html_files(base_dir):
    """手动递归查找所有 HTML 文件，兼容 Windows"""
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def process_file(filepath):
    """处理单个 HTML 文件，替换 CDN 链接"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changed = False
    
    for old_pattern, new_pattern in REPLACEMENTS:
        new_content = re.sub(old_pattern, new_pattern, content)
        if new_content != content:
            content = new_content
            changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dir = "/d/workspace/kongto-blog"
    # 将 Git Bash 路径转换为 Windows 路径
    if base_dir.startswith('/d/'):
        # /d/workspace/... -> D:\workspace\...
        base_dir = "D:" + base_dir[2:].replace('/', '\\')
    
    print(f"工作目录: {base_dir}")
    print(f"CDN Base: {CDN_BASE}")
    print("-" * 60)
    
    # 查找所有 HTML 文件
    html_files = find_html_files(base_dir)
    print(f"找到 {len(html_files)} 个 HTML 文件\n")
    
    modified = []
    for filepath in sorted(html_files):
        rel_path = os.path.relpath(filepath, base_dir)
        if process_file(filepath):
            modified.append(rel_path)
            print(f"✅ 已修改: {rel_path}")
    
    print("-" * 60)
    print(f"共修改 {len(modified)} 个文件")
    
    # 同时也检查 CSS 文件中是否有引用的图片
    css_file = os.path.join(base_dir, "css", "style.css")
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # 检查 CSS 中是否有背景图片引用
        bg_matches = re.findall(r'url\(["\']?/kongto-blog/images/([^"\']+)["\']?\)', css_content)
        if bg_matches:
            print(f"\n⚠️  注意: css/style.css 中有 {len(bg_matches)} 个图片引用需要手动处理:")
            for m in bg_matches:
                print(f"   - /kongto-blog/images/{m}")
        else:
            print(f"\n✅ css/style.css 中没有需要替换的图片引用")

if __name__ == "__main__":
    main()
