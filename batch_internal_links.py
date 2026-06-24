#!/usr/bin/env python3
"""Add related products section at end of article pages before footer."""
import os, re

BASE = r"D:\code\seo_deploy"

ZH_RELATED_BLOCK = """
        <div class="related-products" style="background:#f8fafc;padding:1.5rem;border-radius:8px;margin:2rem 0;border:1px solid #e2e8f0;">
            <p style="font-weight:bold;color:#1e40af;margin:0 0 0.75rem 0;">📌 相关推荐</p>
            <ul style="margin:0;padding-left:1.2rem;">
                <li><a href="/compatibility-matrix.html">95+型号兼容性对照表</a> — 查询您的CRT型号对应的LCD替代方案</li>
                <li><a href="/brands/">按品牌浏览升级方案</a> — FANUC/三菱/西门子/Mazak/Okuma/Haas</li>
                <li><a href="/quote.html">获取报价</a> — 提交询盘，24小时内回复</li>
            </ul>
        </div>
"""

EN_RELATED_BLOCK = """
        <div class="related-products" style="background:#f8fafc;padding:1.5rem;border-radius:8px;margin:2rem 0;border:1px solid #e2e8f0;">
            <p style="font-weight:bold;color:#1e40af;margin:0 0 0.75rem 0;">📌 Related Resources</p>
            <ul style="margin:0;padding-left:1.2rem;">
                <li><a href="/en/compatibility-matrix.html">95+ Model Compatibility Matrix</a> — Find your CRT model</li>
                <li><a href="/en/brands/">Browse by Brand</a> — FANUC/Mitsubishi/Siemens/Mazak/Okuma/Haas</li>
                <li><a href="/en/quote.html">Get a Quote</a> — Reply within 24 hours</li>
            </ul>
        </div>
"""

def add_related_products(filepath):
    """Add related products block before footer in article pages."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has related-products section
    if 'related-products' in content or 'Related Resources' in content:
        return False

    # Skip brand pages, main pages, etc. - only article/post pages
    relpath = os.path.relpath(filepath, BASE)
    if relpath.startswith('brands') or relpath.startswith('products'):
        return False
    if relpath in ('index.html', 'about.html', 'contact.html', 'quote.html',
                    '404.html', 'author.html', 'resources.html', 'search.html',
                    'sitemap.html', 'compatibility-matrix.html',
                    'case-studies.html', 'comparison-kongto-vs-competitors.html',
                    'crt-dead-symptoms.html', 'glossary.html',
                    'pricing.html', 'shipping-calculator-test.html'):
        return False
    if relpath.startswith('en/') and relpath in ('en/index.html', 'en/about.html', 'en/contact.html',
                                                  'en/quote.html', 'en/404.html',
                                                  'en/search.html', 'en/sitemap.html',
                                                  'en/compatibility-matrix.html',
                                                  'en/pricing.html', 'en/glossary.html'):
        return False

    # Detect language and choose block
    is_english = 'lang="en"' in content or relpath.startswith('en/')
    block = EN_RELATED_BLOCK if is_english else ZH_RELATED_BLOCK

    # Insert before footer
    footer_marker = '<footer'
    if footer_marker in content:
        content = content.replace(footer_marker, block + '\n    <footer', 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False

def main():
    files = []
    for root, dirs, fnames in os.walk(BASE):
        dirs[:] = [d for d in dirs if not d.startswith('_') and d not in ('.github', '.well-known', 'backlinks_daily', 'backlinks_output')]
        for f in fnames:
            if f.endswith('.html'):
                files.append(os.path.join(root, f))

    count = 0
    for fp in files:
        if add_related_products(fp):
            rel = os.path.relpath(fp, BASE)
            print(f"  Added: {rel}")
            count += 1

    print(f"\nTotal: {count} files updated with related products section")

if __name__ == '__main__':
    main()
