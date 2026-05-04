# -*- coding: utf-8 -*-
import os
import re
import glob

def add_author_info(file_path, author_name="kongto01"):
    """Add/update author information in article pages"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # 1. Update meta author tag
    if '<meta name="author"' in content:
        content = re.sub(
            r'<meta name="author" content="[^"]*"',
            f'<meta name="author" content="{author_name}"',
            content
        )
        changed = True
    else:
        # Add author meta after keywords meta
        content = re.sub(
            r'(<meta name="keywords"[^>]*>)',
            rf'\1\n    <meta name="author" content="{author_name}">',
            content
        )
        changed = True
    
    # 2. Add article:author meta tag (for Open Graph)
    if '<meta property="article:author"' not in content:
        content = re.sub(
            r'(<meta property="article:published_time"[^>]*>)',
            rf'\1\n    <meta property="article:author" content="{author_name}">',
            content
        )
        changed = True
    
    # 3. Update JSON-LD author to Person type
    content = re.sub(
        r'"author":\s*\{"@type":\s*"[^"]*",\s*"name":\s*"[^"]*"\}',
        f'"author": {{"@type": "Person", "name": "{author_name}"}}',
        content
    )
    
    # 4. Add author info in visible content (after date)
    # Find the meta div and add author link if not present
    if 'class="author"' in content:
        # Update existing author span
        content = re.sub(
            r'<span class="author">[^<]*</span>',
            f'<span class="author">作者: {author_name}</span>',
            content
        )
        changed = True
    
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def create_author_page(author_name="kongto01", output_dir="."):
    """Create an author page"""
    author_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>作者: {author_name} | 深圳市江图科技有限公司</title>
    <meta name="description" content="{author_name} - 工业视频显示技术专家，专注于FANUC数控显示器升级、工业视频信号转换等领域。">
    <link rel="stylesheet" href="/kongto-blog/css/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="/kongto-blog/" class="logo">深圳市江图科技有限公司</a>
            <div class="nav-links">
                <a href="/kongto-blog/">首页</a>
                <a href="/kongto-blog/posts/">文章</a>
                <a href="/kongto-blog/about.html">关于</a>
            </div>
        </nav>
    </header>
    <main>
        <article class="author-profile">
            <h1>关于作者: {author_name}</h1>
            <div class="author-info">
                <p><strong>{author_name}</strong> 是深圳市江图科技有限公司的技术专家，专注于工业视频显示解决方案。</p>
                <h2>专业领域</h2>
                <ul>
                    <li>FANUC数控显示器CRT升级LCD解决方案</li>
                    <li>工业视频信号转换器应用</li>
                    <li>CNC数控系统显示器维修与改造</li>
                    <li>工业自动化设备显示系统集成</li>
                </ul>
                <h2>联系方式</h2>
                <ul>
                    <li>电子邮件: szkongto01@foxmail.com</li>
                    <li>电话: 13686889647</li>
                </ul>
            </div>
        </article>
    </main>
    <footer>
        <p>&copy; 深圳市江图科技有限公司. 专注工业视频显示解决方案.</p>
    </footer>
</body>
</html>'''
    
    author_path = os.path.join(output_dir, 'author.html')
    with open(author_path, 'w', encoding='utf-8') as f:
        f.write(author_html)
    return author_path

if __name__ == '__main__':
    import sys
    
    author_name = "kongto01"
    if len(sys.argv) > 1:
        author_name = sys.argv[1]
    
    print(f"Adding author '{author_name}' to all articles...")
    
    # Fix all article pages
    patterns = [
        'posts/article_*.html',
        'posts/comparison_*.html', 
        'posts/faq_*.html',
        'posts/press_release_*.html',
        'posts/social_*.html',
        'en/posts/article_*.html',
        'en/posts/comparison_*.html',
        'en/posts/faq_*.html',
        'en/posts/press_release_*.html',
        'en/posts/social_*.html'
    ]
    
    count = 0
    for pattern in patterns:
        for file in glob.glob(pattern):
            if add_author_info(file, author_name):
                count += 1
                print(f"  Updated: {file}")
    
    # Create author page
    author_page = create_author_page(author_name)
    print(f"  Created: {author_page}")
    
    print(f"\nDone! Updated {count} files.")
