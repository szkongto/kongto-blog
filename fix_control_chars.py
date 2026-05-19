#!/usr/bin/env python3
"""
修复HTML文件中的控制字符和未闭合标签问题
"""
import os
import re
import html

posts_dir = 'posts'

def fix_html_file(filepath):
    """修复单个HTML文件"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_len = len(content)
    issues = []
    
    # 1. 移除控制字符 (保留 \n, \r, \t)
    # 控制字符范围: \x00-\x08, \x0B, \x0C, \x0E-\x1F, \x7F
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    if len(cleaned) != original_len:
        issues.append(f'移除 {original_len - len(cleaned)} 个控制字符')
        content = cleaned
    
    # 2. 修复未闭合的 table 标签
    table_open = content.count('<table>')
    table_close = content.count('</table>')
    if table_open > table_close:
        # 在 </body> 前添加缺失的 </table>
        missing = table_open - table_close
        content = content.replace('</body>', '</table>' * missing + '</body>')
        issues.append(f'修复 {missing} 个未闭合的 table 标签')
    
    # 3. 检查并修复 JSON-LD script 标签
    if '<script type="application/ld+json">' in content:
        # 确保 JSON-LD 格式正确
        pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            try:
                # 尝试解析 JSON
                json_str = match.strip()
                # 简单的括号匹配检查
                if json_str.count('{') != json_str.count('}'):
                    issues.append('JSON-LD 括号不配对')
            except:
                pass
    
    if issues:
        # 写回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, issues
    
    return False, []

# 主程序
print("开始修复 HTML 文件...")
fixed_count = 0

for filename in sorted(os.listdir(posts_dir)):
    if not filename.endswith('.html'):
        continue
    
    filepath = os.path.join(posts_dir, filename)
    try:
        fixed, issues = fix_html_file(filepath)
        if fixed:
            fixed_count += 1
            print(f"✓ 修复: {filename}")
            for issue in issues:
                print(f"  - {issue}")
    except Exception as e:
        print(f"✗ 错误: {filename} - {e}")

print(f"\n总共修复 {fixed_count} 个文件")
