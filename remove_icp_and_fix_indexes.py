#!/usr/bin/env python3
"""
Batch fix: remove ICP placeholder + update index page Haas titles
"""
import os, re

BASE = r'd:\code\seo_backup_cleanup_0614'

def fix_file(path):
    p = os.path.join(BASE, path)
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    changes = []

    # 1. Remove ICP block entirely
    icp_block = r"""<div style="text-align:center;padding:20px 0;font-size:12px;color:#888888;border-top:1px solid #e0e0e0;margin-top:40px;">
  <p style="margin:4px 0;">
    <a href="https://beian.miit.gov.cn/" target="_blank" rel="nofollow noopener" style="color:#888;text-decoration:none;">
      粤ICP备XXXXXXXX号-1
    </a>
    &nbsp;|&nbsp; 深圳市江图科技有限公司 &copy; 2026
    &nbsp;|&nbsp; <a href="/sitemap.xml" style="color:#888;">Sitemap</a>
    &nbsp;|&nbsp; <a href="/en/" style="color:#888;">English</a>
  </p>
</div>"""

    if icp_block in c:
        c = c.replace(icp_block, '')
        changes.append('ICP block removed')

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    return changes

def fix_index_cn():
    path = os.path.join(BASE, 'posts', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    changes = []

    # Add new Haas guide article to CN listing
    new_haas_entry = """        <article class="post-item">\n            <a href="/posts/Haas_VF_ST_SL_CRT_LCD_Upgrade_Complete_Guide.html">\n                <h3>HAAS系统 VF/ST/SL系列CRT显示器LCD升级完全指南</h3>\n                <time>2026-06-24</time>\n            </a>\n        </article>"""

    # Find Haas section and add before existing article
    haas_section_marker = 'Haas显示器替换方案'
    if haas_section_marker in c:
        # Find the first <article tag after Haas section
        idx = c.find(haas_section_marker)
        section_end = c.find('<article', idx)
        if section_end > 0:
            c = c[:section_end] + new_haas_entry + '\n' + c[section_end:]
            changes.append('Added new Haas CN article to index')

    # Update article count
    old1 = 'Haas显示器替换方案<span class="article-count">(1篇)</span>'
    new1 = 'Haas显示器替换方案<span class="article-count">(2篇)</span>'
    if old1 in c:
        c = c.replace(old1, new1)
        changes.append('Updated Haas CN count to 2')

    # 2. Remove ICP from this file too
    icp_block = r"""<div style="text-align:center;padding:20px 0;font-size:12px;color:#888888;border-top:1px solid #e0e0e0;margin-top:40px;">
  <p style="margin:4px 0;">
    <a href="https://beian.miit.gov.cn/" target="_blank" rel="nofollow noopener" style="color:#888;text-decoration:none;">
      粤ICP备XXXXXXXX号-1
    </a>
    &nbsp;|&nbsp; 深圳市江图科技有限公司 &copy; 2026
    &nbsp;|&nbsp; <a href="/sitemap.xml" style="color:#888;">Sitemap</a>
    &nbsp;|&nbsp; <a href="/en/" style="color:#888;">English</a>
  </p>
</div>"""
    if icp_block in c:
        c = c.replace(icp_block, '')
        changes.append('ICP removed from CN index')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    return changes

def fix_index_en():
    path = os.path.join(BASE, 'en', 'posts', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    changes = []

    # Update the old case study title in EN listing
    old_title = 'Haas CNC CRT to LCD Retrofit Case Study | Kongto Technology Kongto Technology Home Articles Downloads'
    new_title = 'HAAS System 9-Pin Monochrome Display Repair & LCD Upgrade'
    if old_title in c:
        c = c.replace(old_title, new_title)
        changes.append('Updated EN case study title in listing')
    else:
        # Try partial match
        c = re.sub(r'<h3>Haas CNC CRT to LCD[^<]*</h3>', '<h3>HAAS System 9-Pin Monochrome Display Repair &amp; LCD Upgrade</h3>', c)
        changes.append('Updated EN listing title via regex')

    # Also remove ICP
    icp_block = r"""<div style="text-align:center;padding:20px 0;font-size:12px;color:#888888;border-top:1px solid #e0e0e0;margin-top:40px;">
  <p style="margin:4px 0;">
    <a href="https://beian.miit.gov.cn/" target="_blank" rel="nofollow noopener" style="color:#888;text-decoration:none;">
      粤ICP备XXXXXXXX号-1
    </a>
    &nbsp;|&nbsp; 深圳市江图科技有限公司 &copy; 2026
    &nbsp;|&nbsp; <a href="/sitemap.xml" style="color:#888;">Sitemap</a>
    &nbsp;|&nbsp; <a href="/en/" style="color:#888;">English</a>
  </p>
</div>"""
    if icp_block in c:
        c = c.replace(icp_block, '')
        changes.append('ICP removed from EN index')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    return changes

print("=== Removing ICP from all HTML files ===")
icp_fixed = 0
for root, dirs, files in os.walk(BASE):
    if '.git' in root: continue
    for fname in files:
        if not fname.endswith('.html'): continue
        path = os.path.relpath(os.path.join(root, fname), BASE)
        changes = fix_file(path)
        if changes:
            icp_fixed += 1
            if icp_fixed <= 5:
                print(f"  {path}: {', '.join(changes)}")

print(f"ICP removed from {icp_fixed} files total")

print("\n=== Fixing index pages ===")
cn_changes = fix_index_cn()
for ch in cn_changes:
    print(f"  CN index: {ch}")

en_changes = fix_index_en()
for ch in en_changes:
    print(f"  EN index: {ch}")

print("\nDone!")
