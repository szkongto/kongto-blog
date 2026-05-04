# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path
from urllib.parse import quote
import glob

def fix_sitemap():
    """Fix sitemap.xml - URL encode Chinese characters"""
    sitemap_path = 'sitemap.xml'
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all URLs in sitemap
    def encode_url(match):
        url = match.group(1)
        # URL encode the path part
        parts = url.split('/')
        encoded_parts = []
        for part in parts:
            if part and any(ord(c) > 127 for c in part):
                # Contains non-ASCII, needs encoding
                encoded_parts.append(quote(part, safe=''))
            else:
                encoded_parts.append(part)
        return '<loc>' + '/'.join(encoded_parts) + '</loc>'
    
    content = re.sub(r'<loc>(https://szkongto\.github\.io/kongto-blog/[^<]+)</loc>', encode_url, content)
    
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed sitemap.xml')

def add_viewport_and_description(file_path):
    """Add viewport meta and meta description if missing"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Check if viewport is missing
    if '<meta name="viewport"' not in content:
        # Add viewport after charset
        content = re.sub(
            r'(<meta charset="UTF-8">)',
            r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            content
        )
        changed = True
    
    # Check if meta description is missing (for important pages)
    if 'about.html' in file_path or 'posts/index.html' in file_path:
        if '<meta name="description"' not in content:
            # Add description after viewport/title
            if 'about.html' in file_path and '/en/' not in file_path.replace('\\', '/'):
                desc = '<meta name="description" content="深圳市江图科技有限公司专注于工业视频显示解决方案，为CNC数控系统提供显示器升级改造服务。">'
            elif 'about.html' in file_path:
                desc = '<meta name="description" content="Kongto Technology specializes in industrial video display integration solutions for CNC systems.">'
            elif 'posts/index.html' in file_path and '/en/' not in file_path.replace('\\', '/'):
                desc = '<meta name="description" content="工业视频显示技术文章，涵盖FANUC显示器升级、工业视频信号转换、CNC数控备件等专业内容。">'
            else:
                desc = '<meta name="description" content="Technical articles about industrial video display, FANUC display retrofit, and CNC solutions.">'
            
            # Add after title
            content = re.sub(
                r'(</title>)',
                r'\1\n    ' + desc,
                content
            )
            changed = True
    
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_article_meta_description(file_path):
    """Fix meta descriptions that contain Markdown syntax"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Find and fix meta descriptions with Markdown image syntax
    # Pattern: content="![...](...)"
    def clean_description(full_match, desc_value):
        # If it contains Markdown image syntax, clean it
        if '![' in desc_value and '](' in desc_value:
            # Extract alt text or generate a proper description
            alt_match = re.search(r'!\[([^\]]*)\]', desc_value)
            if alt_match:
                alt_text = alt_match.group(1)
                # Create proper description based on article title
                return f'content="{alt_text} - 专业工业显示器升级解决方案"'
            return 'content="工业视频显示解决方案"'
        return f'content="{desc_value}"'
    
    # Fix description meta tags
    content = re.sub(
        r'<meta name="description" content="([^"]*)"',
        lambda m: '<meta name="description" ' + clean_description(m.group(0), m.group(1)),
        content
    )
    
    # Also fix og:description
    content = re.sub(
        r'<meta property="og:description" content="([^"]*)"',
        lambda m: '<meta property="og:description" ' + clean_description(m.group(0), m.group(1)),
        content
    )
    
    # Fix twitter:description
    content = re.sub(
        r'<meta name="twitter:description" content="([^"]*)"',
        lambda m: '<meta name="twitter:description" ' + clean_description(m.group(0), m.group(1)),
        content
    )
    
    # Fix JSON-LD description
    content = re.sub(
        r'"description":\s*"!\[[^\]]*\]\([^)]*\)"',
        '"description": "工业显示器升级解决方案"',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_h1_duplication(file_path):
    """Fix H1 duplication in article pages - change content h1 to h2"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the article title in the header h1
    header_h1_match = re.search(r'<article[^>]*>\s*<h1>([^<]+)</h1>', content)
    
    if header_h1_match:
        article_title = header_h1_match.group(1)
        
        # Find duplicate h1 in content div and change it to a different element
        # Pattern: <div class="content">...<h1>Title</h1>
        def replace_duplicate_h1(match):
            h1_content = match.group(1)
            # If it's the same as the header h1, remove it (it's a duplicate)
            if h1_content.strip() == article_title.strip():
                return ''  # Remove the duplicate h1
            else:
                return '<h2>' + h1_content + '</h2>'
        
        # Find h1 tags inside the content div
        content = re.sub(
            r'<div class="content">.*?(<h1>([^<]+)</h1>)',
            lambda m: m.group(0).replace('<h1>' + m.group(2) + '</h1>', ''),
            content,
            flags=re.DOTALL
        )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def clean_posts_list_markdown(file_path):
    """Clean Markdown syntax from posts list page"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove Markdown image syntax from post excerpts
    content = re.sub(r'<p>!\[[^\]]*\]\([^)]*\)\.\.\.</p>', '<p>...</p>', content)
    content = re.sub(r'!\[[^\]]*\]\([^)]*\)\.\.\.', '...', content)
    
    # Remove blockquote syntax
    content = re.sub(r'<p>&gt;\s*\*\*[^*]+\*\*[^<]*</p>', '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python seo_fix.py <command>")
        print("Commands: sitemap, viewport, articles, all")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'sitemap':
        fix_sitemap()
    elif command == 'viewport':
        # Fix viewport for key pages
        pages = [
            'posts/index.html',
            'about.html',
            'en/posts/index.html',
            'en/about.html'
        ]
        for page in pages:
            if os.path.exists(page):
                if add_viewport_and_description(page):
                    print(f'Fixed viewport/description: {page}')
    elif command == 'articles':
        # Fix all article pages
        for pattern in ['posts/article_*.html', 'posts/comparison_*.html', 'posts/faq_*.html', 
                        'en/posts/article_*.html', 'en/posts/comparison_*.html', 'en/posts/faq_*.html']:
            for file in glob.glob(pattern):
                fix_article_meta_description(file)
                fix_h1_duplication(file)
                print(f'Fixed article: {file}')
        # Fix posts list
        clean_posts_list_markdown('posts/index.html')
        print('Fixed posts/index.html')
    elif command == 'all':
        fix_sitemap()
        for page in ['posts/index.html', 'about.html', 'en/posts/index.html', 'en/about.html']:
            if os.path.exists(page):
                add_viewport_and_description(page)
                print(f'Fixed: {page}')
        for pattern in ['posts/article_*.html', 'posts/comparison_*.html', 'posts/faq_*.html',
                        'en/posts/article_*.html', 'en/posts/comparison_*.html', 'en/posts/faq_*.html']:
            for file in glob.glob(pattern):
                fix_article_meta_description(file)
                fix_h1_duplication(file)
        clean_posts_list_markdown('posts/index.html')
        print('All fixes completed!')
