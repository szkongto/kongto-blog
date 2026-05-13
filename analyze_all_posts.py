#!/usr/bin/env python3
"""分析所有文章的结构问题"""
import os
import re
import glob

posts_dir = "/d/workspace/kongto-blog/posts"
html_files = glob.glob(os.path.join(posts_dir, "article_*.html"))

results = []

for f in sorted(html_files):
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    filename = os.path.basename(f)
    
    # 统计图片数量
    img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    img_count = len(img_tags)
    
    # 检查结构问题
    issues = []
    
    # 1. 检查</p><p>符号堆砌
    if '</p><p>' in content or '</P><P>' in content:
        issues.append("符号堆砌</p><p>")
    
    # 2. 检查空行段落
    empty_para = content.count('<p></p>') + content.count('<p> </p>')
    if empty_para > 0:
        issues.append(f"空段落{empty_para}个")
    
    # 3. 检查Markdown表格
    if '|' in content and 'table' not in content.lower():
        issues.append("Markdown表格未转HTML")
    
    # 4. 检查标题结构
    h2_count = len(re.findall(r'<h2', content, re.I))
    if h2_count == 0:
        issues.append("无章节标题")
    
    # 5. 检查内容长度
    text_len = len(re.sub(r'<[^>]+>', '', content))
    
    # 6. 检查关键词问题
    if 'A61L-0001-0093' in content and '0093' not in filename:
        issues.append("关键词错误(0093)")
    
    # 7. 获取标题
    title_match = re.search(r'<title>([^<]+)</title>', content)
    title = title_match.group(1)[:40] if title_match else "无标题"
    
    results.append({
        'file': filename,
        'title': title,
        'imgs': img_count,
        'issues': issues,
        'h2': h2_count,
        'chars': text_len
    })

# 按问题数量排序
results.sort(key=lambda x: -len(x['issues']))

print("=" * 100)
print(f"{'序号':<4} {'标题':<35} {'图片':<4} {'章节':<4} {'字数':<6} {'问题'}")
print("=" * 100)

for i, r in enumerate(results, 1):
    issue_str = "; ".join(r['issues']) if r['issues'] else "✓"
    print(f"{i:<4} {r['title']:<35} {r['imgs']:<4} {r['h2']:<4} {r['chars']:<6} {issue_str}")

print("=" * 100)
print(f"\n总计: {len(results)} 篇文章")

# 分类统计
no_imgs = sum(1 for r in results if r['imgs'] == 0)
has_issues = sum(1 for r in results if r['issues'])
print(f"无图片: {no_imgs} 篇")
print(f"有问题: {has_issues} 篇")
