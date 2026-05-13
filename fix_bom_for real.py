#!/usr/bin/env python3
"""
强力修复 HTML 文件的 BOM 和 DOCTYPE 问题
直接以二进制模式处理，确保万无一失
"""
import os
import re

posts_dir = 'posts'

def fix_bom_and_doctype(filepath):
    """修复 BOM 和 DOCTYPE 位置问题"""
    # 以二进制模式读取
    with open(filepath, 'rb') as f:
        raw_content = f.read()
    
    original_len = len(raw_content)
    
    # 1. 去除 BOM (EF BB BF)
    if raw_content.startswith(b'\xef\xbb\xbf'):
        raw_content = raw_content[3:]
        bom_removed = True
    else:
        bom_removed = False
    
    # 2. 解码为文本
    try:
        content = raw_content.decode('utf-8')
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            content = raw_content.decode('gbk')
        except:
            return False, ['解码失败']
    
    # 3. 确保 DOCTYPE 在最前面
    fixes = []
    if bom_removed:
        fixes.append('移除 BOM 字符')
    
    # 查找 DOCTYPE 位置
    doctype_match = re.search(r'<!DOCTYPE\s+html>', content, re.IGNORECASE)
    if doctype_match and doctype_match.start() > 0:
        # DOCTYPE 不在最前面，移到最前面
        before_doctype = content[:doctype_match.start()]
        if before_doctype.strip():
            fixes.append(f'DOCTYPE 前有内容: {repr(before_doctype[:30])}')
        
        # 保留 DOCTYPE 及之后的内容
        content = content[doctype_match.start():]
        fixes.append('修正 DOCTYPE 位置到文件开头')
    
    # 4. 移除其他控制字符
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    if len(cleaned) != len(content):
        fixes.append(f'移除 {len(content) - len(cleaned)} 个控制字符')
        content = cleaned
    
    # 5. 写回文件（UTF-8 无 BOM）
    if fixes:
        with open(filepath, 'wb') as f:
            f.write(content.encode('utf-8'))
        return True, fixes
    
    return False, []

print("="*70)
print("开始强力修复 BOM 和 DOCTYPE 问题...")
print("="*70)

fixed_count = 0
failed_files = []

# 获取所有需要检查的文件
html_files = []

# posts 目录
for f in os.listdir(posts_dir):
    if f.endswith('.html'):
        html_files.append(os.path.join(posts_dir, f))

# 根目录 HTML 文件
for f in ['index.html', 'about.html', 'author.html', '404.html']:
    if os.path.exists(f):
        html_files.append(f)

print(f"\n检查 {len(html_files)} 个 HTML 文件...\n")

for filepath in sorted(html_files):
    filename = os.path.basename(filepath)
    try:
        fixed, fixes = fix_bom_and_doctype(filepath)
        if fixed:
            fixed_count += 1
            print(f"✓ 修复: {filename}")
            for fix in fixes:
                print(f"  - {fix}")
    except Exception as e:
        error_msg = f"{filename}: {e}"
        failed_files.append(error_msg)
        print(f"✗ 失败: {error_msg}")

print("\n" + "="*70)
print(f"修复完成: 成功 {fixed_count} 个, 失败 {len(failed_files)} 个")
if failed_files:
    print("\n失败的文件:")
    for err in failed_files[:10]:
        print(f"  - {err}")
print("="*70)
