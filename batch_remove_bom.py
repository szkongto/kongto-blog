#!/usr/bin/env python3
"""
批量去除HTML文件的BOM字符
"""
import os

posts_dir = 'posts'

# 需要修复的文件列表（根据之前的检查结果）
files_to_fix = [
    'article_20260508_KTV104_非标订制工业显示器.html',
    'article_20260508_KTV148_非标订制工业显示器.html',
    'article_20260508_KTV800M_非标订制工业显示器.html',
    'article_20260508_KTV804_非标订制工业显示器.html',
    'article_20260509_GBS-8219_RGB转VGA工业信号转换器.html',
    'article_20260509_KT809_工业转换器.html',
    'article_20260509_KT819_工业转换器.html',
    'faq_20260501_数控机床显示器更换常见问题TOP10.html',
    'social_20260501_数控显示器升级市场动态与产品速递.html',
    '非标订制显示器系列.html',
    'index.html',
    'about.html',
    'author.html',
    '404.html'
]

print("="*70)
print("批量去除BOM字符")
print("="*70)

fixed_count = 0

for filename in files_to_fix:
    # 构建文件路径
    if filename in ['index.html', 'about.html', 'author.html', '404.html']:
        filepath = filename
    else:
        filepath = os.path.join(posts_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"⚠ 文件不存在: {filepath}")
        continue
    
    try:
        # 以二进制读取
        with open(filepath, 'rb') as f:
            raw = f.read()
        
        original_size = len(raw)
        
        # 去除BOM (EF BB BF)
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
            
            # 写回（无BOM的UTF-8）
            with open(filepath, 'wb') as f:
                f.write(raw)
            
            fixed_count += 1
            print(f"✓ 修复: {filename} ({original_size} → {len(raw)} 字节)")
        else:
            print(f"  - 跳过: {filename} (无BOM)")
    
    except Exception as e:
        print(f"✗ 错误: {filename} - {e}")

print("\n" + "="*70)
print(f"修复完成: {fixed_count} 个文件")
print("="*70)
