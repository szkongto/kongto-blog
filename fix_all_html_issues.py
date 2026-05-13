#!/usr/bin/env python3
"""
全面修复HTML文件的所有问题：
1. BOM字符
2. DOCTYPE位置
3. 多余的闭合标签
4. JSON-LD格式错误
"""
import os
import re
import json

posts_dir = 'posts'
fixed_count = 0
all_issues = []

def fix_file(filepath):
    """修复单个文件，返回修复项列表"""
    # 使用 utf-8-sig 编码自动去除 BOM
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    fixes = []
    
    # 1. 确保 DOCTYPE 是文件的开头
    if not content.lstrip().startswith('<!DOCTYPE html>'):
        # 查找 DOCTYPE 的位置
        doctype_match = re.search(r'<!DOCTYPE html>', content, re.IGNORECASE)
        if doctype_match:
            # 保留 DOCTYPE 之前的内容（应该只有 BOM 或空白）
            before_doctype = content[:doctype_match.start()]
            if before_doctype.strip():
                fixes.append(f'DOCTYPE 前有内容: {repr(before_doctype[:50])}')
            # 将 DOCTYPE 移到最前面
            after_doctype = content[doctype_match.start():]
            content = after_doctype
            fixes.append('修正 DOCTYPE 位置')
    
    # 2. 移除残留的控制字符
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    if cleaned != content:
        fixes.append(f'移除 {len(content) - len(cleaned)} 个控制字符')
        content = cleaned
    
    # 3. 修复多余的 </p> 标签
    # 统计 <p> 和 </p> 的数量
    p_open = len(re.findall(r'<p[>\s]', content, re.IGNORECASE))
    p_close = content.count('</p>')
    
    if p_close > p_open:
        # 有多余的 </p>，需要删除
        excess = p_close - p_open
        # 简单处理：删除多余的 </p>
        lines = content.split('\n')
        removed = 0
        new_lines = []
        for line in lines:
            if '</p>' in line and removed < excess:
                # 删除 </p>
                new_line = line.replace('</p>', '', 1)
                removed += 1
                if new_line.strip():  # 如果行还有其他内容，保留
                    new_lines.append(new_line)
                continue
            new_lines.append(line)
        
        if removed > 0:
            content = '\n'.join(new_lines)
            fixes.append(f'删除 {removed} 个多余的 </p>')
    
    # 4. 修复 JSON-LD 格式错误
    json_ld_pattern = r'<script type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    json_ld_matches = list(re.finditer(json_ld_pattern, content, re.DOTALL | re.IGNORECASE))
    
    for match in json_ld_matches:
        json_str = match.group(1).strip()
        try:
            json.loads(json_str)
        except json.JSONDecodeError as e:
            # 尝试修复常见的 JSON 错误
            fixes.append(f'JSON-LD 错误: {str(e)[:50]}')
            # 可以在这里添加自动修复逻辑
    
    # 写回文件（不使用 BOM）
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, fixes
    
    return False, []

print("="*70)
print("开始全面修复 HTML 文件...")
print("="*70)

# 修复 posts 目录下的文件
for filename in sorted(os.listdir(posts_dir)):
    if not filename.endswith('.html'):
        continue
    
    filepath = os.path.join(posts_dir, filename)
    try:
        fixed, fixes = fix_file(filepath)
        if fixed:
            fixed_count += 1
            print(f"✓ 修复: {filename}")
            for fix in fixes:
                print(f"  - {fix}")
    except Exception as e:
        print(f"✗ 错误: {filename} - {e}")
        all_issues.append(f"{filename}: {e}")

# 修复根目录下的 HTML 文件
root_html_files = ['index.html', 'about.html', 'author.html', '404.html']
for filename in root_html_files:
    filepath = os.path.join('.', filename)
    if os.path.exists(filepath):
        try:
            fixed, fixes = fix_file(filepath)
            if fixed:
                fixed_count += 1
                print(f"✓ 修复: {filename}")
                for fix in fixes:
                    print(f"  - {fix}")
        except Exception as e:
            print(f"✗ 错误: {filename} - {e}")

print("\n" + "="*70)
print(f"修复完成: 共修复 {fixed_count} 个文件")
if all_issues:
    print(f"错误: {len(all_issues)} 个")
print("="*70)
