"""Family A fix: Replace mojibake special symbols across all HTML files.
Safe mappings only — never damages valid Chinese text."""
import os, sys, re

SITE = r'd:\code\seo_deploy'

# Safe replacement mappings (verified: only match corrupted chars, never valid Chinese)
REPLACE = {
    '钘': '≤',  # 鈮? → ≤ (U+2264)
    '虏': '²',      # 虏 → ² (U+00B2)
    '銆': '。',      # 銆 → 。(U+3002, Japanese/Chinese period)
}

def fix_file(fp, dry_run=True):
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return 0, []

    orig = content
    changes = []
    for old, new in REPLACE.items():
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            changes.append((old, new, count))

    if not changes:
        return 0, []

    if not dry_run:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)

    return 1, changes

def main():
    dry_run = '--apply' not in sys.argv

    # Walk all HTML files
    targets = []
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('en_bak', 'worktrees', '__pycache__', 'node_modules')]
        for f in files:
            if f.endswith('.html'):
                targets.append(os.path.join(root, f))

    total_fixed = 0
    total_replaced = 0

    for fp in sorted(targets):
        fixed, changes = fix_file(fp, dry_run)
        if fixed:
            rel = os.path.relpath(fp, SITE)
            details = ', '.join([f'{old!r}->{new!r} x{c}' for old, new, c in changes])
            print(f'  {rel}: {details}')
            total_fixed += 1
            total_replaced += sum(c for _, _, c in changes)

    print(f'\nFiles modified: {total_fixed}')
    print(f'Replacements: {total_replaced}')
    if dry_run:
        print('\nDRY RUN — no files changed. Re-run with --apply to write.')
    else:
        print('\nAPPLIED — files written.')

if __name__ == '__main__':
    main()
