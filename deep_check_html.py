#!/usr/bin/env python3
"""
深度检查HTML文件，找出所有可能导致页面空白的问题
"""
import os
import re
import json
from html.parser import HTMLParser

class HTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.void_elements = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    
    def handle_starttag(self, tag, attrs):
        if tag.lower() not in self.void_elements:
            self.stack.append(tag.lower())
    
    def handle_endtag(self, tag):
        if tag.lower() in self.void_elements:
            return
        if self.stack and self.stack[-1] == tag.lower():
            self.stack.pop()
        elif tag.lower() in self.stack:
            # 找到匹配的开启标签
            idx = len(self.stack) - 1 - self.stack[::-1].index(tag.lower())
            unclosed = self.stack[idx+1:]
            if unclosed:
                self.errors.append(f'未闭合标签: {unclosed}')
            self.stack = self.stack[:idx]
        else:
            self.errors.append(f'多余的闭合标签: </{tag}>')

def check_file(filepath):
    """检查单个文件，返回问题列表"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 1. 检查控制字符
    control_chars = re.findall(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', content)
    if control_chars:
        issues.append(f'控制字符: {len(control_chars)} 个')
    
    # 2. 检查 DOCTYPE
    if not content.strip().startswith('<!DOCTYPE html>'):
        issues.append('缺少或错误的 DOCTYPE')
    
    # 3. 检查必要的标签
    if '<html' not in content.lower():
        issues.append('缺少 <html> 标签')
    if '<head>' not in content.lower():
        issues.append('缺少 <head> 标签')
    if '<body>' not in content.lower():
        issues.append('缺少 <body> 标签')
    if '</html>' not in content.lower():
        issues.append('缺少 </html> 闭合标签')
    
    # 4. 检查 CSS 加载
    css_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*>'
    css_tags = re.findall(css_pattern, content, re.IGNORECASE)
    if not css_tags:
        issues.append('未找到 CSS 样式表')
    else:
        for css_tag in css_tags:
            href_match = re.search(r'href=["\']([^"\']+)["\']', css_tag)
            if href_match:
                href = href_match.group(1)
                if href.startswith('//') or href.startswith('http'):
                    pass  # 绝对URL，OK
                elif href.startswith('/'):
                    pass  # 根相对路径，OK
                else:
                    issues.append(f'CSS 路径可能错误: {href}')
    
    # 5. 检查 JavaScript 语法（简单检查）
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
    for i, script in enumerate(scripts):
        if 'function' in script or 'var ' in script:
            # 简单的括号匹配检查
            opens = script.count('{')
            closes = script.count('}')
            if abs(opens - closes) > 2:  # 允许一些误差
                issues.append(f'Script {i+1}: 花括号不配对 ({opens} 开 / {closes} 关)')
            
            parens_open = script.count('(')
            parens_close = script.count(')')
            if abs(parens_open - parens_close) > 2:
                issues.append(f'Script {i+1}: 圆括号不配对 ({parens_open} 开 / {parens_close} 关)')
    
    # 6. 检查 JSON-LD 格式
    json_ld_pattern = r'<script type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    json_ld_matches = re.findall(json_ld_pattern, content, re.DOTALL | re.IGNORECASE)
    for i, json_str in enumerate(json_ld_matches):
        try:
            json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            issues.append(f'JSON-LD {i+1} 格式错误: {str(e)[:50]}')
    
    # 7. 使用 HTMLParser 检查标签配对
    try:
        validator = HTMLValidator()
        validator.feed(content)
        if validator.errors:
            issues.extend(validator.errors[:3])  # 只显示前3个错误
    except Exception as e:
        issues.append(f'HTML 解析错误: {e}')
    
    return issues

def main():
    posts_dir = 'posts'
    all_issues = {}
    
    print("="*70)
    print("深度检查 HTML 文件...")
    print("="*70)
    
    for filename in sorted(os.listdir(posts_dir)):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(posts_dir, filename)
        issues = check_file(filepath)
        
        if issues:
            all_issues[filename] = issues
    
    # 输出结果
    if all_issues:
        print(f"\n发现 {len(all_issues)} 个文件有问题:\n")
        for filename, issues in all_issues.items():
            print(f"❌ {filename}:")
            for issue in issues:
                print(f"   - {issue}")
            print()
    else:
        print("\n✅ 所有文件检查通过，未发现问题")
    
    print("="*70)

if __name__ == '__main__':
    main()
