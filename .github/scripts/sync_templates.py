#!/usr/bin/env python3
"""
Template sync: aligns nav menu and footer across all HTML files.

SAFETY RULES:
  - Only touches <header><nav> and <footer> blocks
  - Preserves each file's own lang-switch URLs (they vary per file)
  - Validates lang-switch links but does NOT change them
  - Non-HTML content (scripts, article body, schema) is untouched

Usage:
  python sync_templates.py           # Apply fixes
  python sync_templates.py --check   # Check only, exit 1 if changes needed
  python sync_templates.py --dry-run # Show what would change
"""
import os, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES = ROOT / '_templates'

SKIP_FILES = {
    # Redirect/tool pages with no nav
    '404.html', 'en/404.html',
    # Special pages
    'search.html', 'en/search.html',
    'shipping-calculator-test.html',
    'baidu_verify_codeva-MOcuLxbSCp.html',
    'google7478b8e743977291.html',
    'sitemap.html',  # Has unique structure
    # Template files themselves
    '_templates/nav_zh.html', '_templates/nav_en.html',
    '_templates/footer_zh.html', '_templates/footer_en.html',
}

SKIP_DIRS = {'.git', '.github', '_archive_audit', 'node_modules',
             'backlinks_output', 'backlinks_daily', '.claude'}


def load_template(name):
    path = TEMPLATES / name
    if path.exists():
        return path.read_text(encoding='utf-8').strip()
    return None


def find_html_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(str(ROOT)):
        rel = Path(dirpath).relative_to(ROOT)
        if set(rel.parts) & SKIP_DIRS:
            continue
        for f in filenames:
            if not f.endswith('.html'):
                continue
            rp = str(Path(dirpath).relative_to(ROOT) / f).replace('\\', '/')
            if rp in SKIP_FILES:
                continue
            files.append(Path(dirpath) / f)
    return files


def is_cn(filepath, content):
    """Determine if file is Chinese version based on <html lang="...">"""
    m = re.search(r'<html\s+lang="([^"]*)"', content)
    if m:
        return 'zh' in m.group(1).lower()
    rel = str(filepath.relative_to(ROOT)).replace('\\', '/')
    return not rel.startswith('en/')


def extract_lang_switch(content):
    """Extract the per-file lang-switch div from an existing nav."""
    m = re.search(r'<div class="lang-switch">.*?</div>', content, re.DOTALL)
    return m.group(0) if m else None


def extract_nav_block(content):
    """Extract the entire <header>...</header> block."""
    m = re.search(r'<header>.*?</header>', content, re.DOTALL)
    return m.group(0) if m else None


def extract_footer_block(content):
    """Extract the entire <footer>...</footer> block."""
    m = re.search(r'<footer>.*?</footer>', content, re.DOTALL)
    return m.group(0) if m else None


def build_nav(filepath, content):
    """Build standard nav for this file, preserving its lang-switch."""
    cn = is_cn(filepath, content)
    template_name = 'nav_zh.html' if cn else 'nav_en.html'
    template = load_template(template_name)
    if not template:
        return None

    old_lang_switch = extract_lang_switch(content)
    if not old_lang_switch:
        return None

    # Replace the placeholder lang-switch with the file's actual one
    nav = re.sub(
        r'<div class="lang-switch">.*?</div>',
        old_lang_switch,
        template,
        flags=re.DOTALL
    )
    return nav


def build_footer(filepath, content):
    """Return the standard footer for this file's language."""
    cn = is_cn(filepath, content)
    template_name = 'footer_zh.html' if cn else 'footer_en.html'
    return load_template(template_name)


def main():
    dry_run = '--dry-run' in sys.argv
    check_only = '--check' in sys.argv

    html_files = find_html_files()

    # Verify templates exist
    for t in ['nav_zh.html', 'nav_en.html', 'footer_zh.html', 'footer_en.html']:
        if not (TEMPLATES / t).exists():
            print(f"ERROR: Missing template: _templates/{t}")
            sys.exit(1)

    changes = []
    print(f"Scanning {len(html_files)} files...\n")

    for html_file in sorted(html_files):
        rel = str(html_file.relative_to(ROOT)).replace('\\', '/')

        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        old_nav = extract_nav_block(content)
        old_footer = extract_footer_block(content)
        new_nav = build_nav(html_file, content)
        new_footer = build_footer(html_file, content)

        file_changes = []

        if old_nav and new_nav and old_nav.strip() != new_nav.strip():
            # Verify lang-switch is preserved
            old_ls = extract_lang_switch(content)
            new_ls = extract_lang_switch(new_nav)
            if old_ls and new_ls and old_ls.strip() == new_ls.strip():
                file_changes.append(('nav', old_nav, new_nav))

        if old_footer and new_footer and old_footer.strip() != new_footer.strip():
            file_changes.append(('footer', old_footer, new_footer))

        if file_changes:
            changes.append((html_file, rel, file_changes))
            if dry_run or check_only:
                print(f"  [{rel}] {len(file_changes)} fix(es): {' '.join(c[0] for c in file_changes)}")
            else:
                for ftype, old, new in file_changes:
                    content = content.replace(old, new)
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  FIXED: {rel}")

    total_files = len(changes)
    total_changes = sum(len(c[2]) for c in changes)

    print(f"\n{'='*50}")
    print(f"Files scanned:   {len(html_files)}")
    print(f"Files modified:  {total_files}")
    print(f"Changes applied: {total_changes}")
    print(f"Mode:            {'DRY-RUN' if dry_run else 'CHECK' if check_only else 'APPLIED'}")

    if check_only and total_changes > 0:
        print("\nERROR: Template inconsistencies found. Run without --check to fix.")
        sys.exit(1)


if __name__ == '__main__':
    main()
