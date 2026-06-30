"""
Sync root domain files to /zh/ with path rewriting.

Run: python sync_root_to_zh.py [--check] [file1 file2 ...]
  --check: just show what would be synced
  with files: sync only those files (for pre-commit hook)
  without args: sync all root files that have /zh/ counterparts
"""

import re
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Files NEVER synced (different content per language)
EXCLUDE = {
    'index.html',
    'zh/index.html',
    'en/index.html',
}

# Dirs NEVER synced (internal/tool files)
EXCLUDE_DIRS = {'zh', 'en', '.git', '__pycache__', '_archive_audit', '_templates'}

# Files NEVER synced (verification/config files)
EXCLUDE_FILES = {
    'baidu_verify_codeva-MOcuLxbSCp.html',
    'google7478b8e743977291.html',
    'ddac7c800685a15fa23809dc08c3b6c9.txt',
}

# Relative paths that stay as-is (images, CSS, JS, external links)
NO_REWRITE_PREFIXES = (
    '/images/', '/css/', '/js/', '/fonts/',
    'http://', 'https://', '//', 'mailto:', 'tel:', '#', 'javascript:',
)

def needs_sync(rel_path):
    """Check if a file should be synced from root to /zh/."""
    if rel_path in EXCLUDE:
        return False
    fname = os.path.basename(rel_path)
    if fname in EXCLUDE_FILES:
        return False
    for prefix in ('zh/', 'en/', '_'):
        if rel_path.startswith(prefix):
            return False
    if not rel_path.endswith('.html'):
        return False
    return True

def zh_path(rel_path):
    """Convert root path to /zh/ equivalent."""
    return os.path.join('zh', rel_path)

def rewrite_internal_links(content):
    """Rewrite internal content links from root path to /zh/ path."""
    def replace_link(match):
        prefix = match.group(1)
        path = match.group(2)
        suffix = match.group(3)
        if not path.startswith('/') or path.startswith('//'):
            return match.group(0)
        if path == '/':
            return match.group(0)
        for exclude in NO_REWRITE_PREFIXES:
            if path.startswith(exclude):
                return match.group(0)
        if path.startswith('/zh/') or path.startswith('/en/'):
            return match.group(0)
        return f'{prefix}/zh{path}{suffix}'

    content = re.sub(
        r'(href=")(/[^"]*)(["\s>])',
        replace_link,
        content
    )
    return content

def rewrite_for_zh(content, rel_path):
    """Rewrite internal links for /zh/ version."""
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        # Rewrite hreflang zh-CN URLs: /about.html → /zh/about.html
        # Only rewrite when path doesn't already have /en/ or /zh/
        line = re.sub(
            r'(hreflang="zh-CN" href="https://cncdisplay\.com)/(?!en/|zh/)([^"]+)',
            r'\1/zh/\2',
            line
        )
        # Rewrite canonical links: /about.html → /zh/about.html
        # Skip if path already has /en/ or /zh/ (e.g., redirect pages)
        line = re.sub(
            r'(rel="canonical" href="https://cncdisplay\.com)/(?!en/|zh/)([^"]+)',
            r'\1/zh/\2',
            line
        )
        # Rewrite og:url: /about.html → /zh/about.html
        line = re.sub(
            r'(property="og:url" content="https://cncdisplay\.com)/(?!en/|zh/)([^"]+)',
            r'\1/zh/\2',
            line
        )
        # Fix language switcher: /about.html -> /zh/about.html
        line = re.sub(
            r'(href=")/([^"]*\.html)"\s+lang="zh"',
            r'\1/zh/\2" lang="zh"',
            line
        )
        new_lines.append(line)

    result = '\n'.join(new_lines)
    # After meta rewrites, rewrite internal content links
    result = rewrite_internal_links(result)
    return result

def sync_file(rel_path, check_only=False):
    """Sync one file from root to /zh/."""
    if not needs_sync(rel_path):
        return None

    root_file = os.path.join(ROOT, rel_path)
    zh_rel = zh_path(rel_path)
    zh_file = os.path.join(ROOT, zh_rel)

    if not os.path.exists(root_file):
        return None
    if not os.path.exists(zh_file):
        # File exists in root but not in /zh/ - new file, needs creation
        action = 'CREATE'
    else:
        with open(root_file, 'r', encoding='utf-8') as f:
            root_content = f.read()
        with open(zh_file, 'r', encoding='utf-8') as f:
            zh_content = f.read()
        expected_zh = rewrite_for_zh(root_content, rel_path)
        if zh_content == expected_zh:
            return None  # Already in sync
        action = 'UPDATE'

    if check_only:
        return (action, rel_path)

    # Read and rewrite
    with open(root_file, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = rewrite_for_zh(content, rel_path)

    # Write
    os.makedirs(os.path.dirname(zh_file), exist_ok=True)
    with open(zh_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return (action, rel_path)

def collect_all_html():
    """Recursively collect all .html files in root (not excluded dirs)."""
    results = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Filter out excluded dirs in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for f in filenames:
            if f in EXCLUDE_FILES:
                continue
            if f.endswith('.html'):
                rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
                # Normalize to forward slash
                rel = rel.replace('\\', '/')
                results.append(rel)
    return sorted(results)

def main():
    check_only = '--check' in sys.argv
    files_to_sync = [a for a in sys.argv[1:] if a != '--check']

    if files_to_sync:
        # Specific files from pre-commit hook (staged files)
        inputs = files_to_sync
    else:
        # All HTML files
        inputs = collect_all_html()

    synced = []
    for rel_path in inputs:
        result = sync_file(rel_path, check_only)
        if result:
            synced.append(result)

    if not synced:
        print(f"[sync] All {len(inputs)} files checked - nothing to sync")
        return

    if check_only:
        print(f"[sync] Would sync {len(synced)} files:")
        for action, path in synced:
            print(f"  [{action}] {path}")
        return

    print(f"[sync] Synced {len(synced)} files from root → /zh/:")
    for action, path in synced:
        print(f"  [{action}] {path}")

if __name__ == '__main__':
    main()
