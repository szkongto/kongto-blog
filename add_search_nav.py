"""Add search link to the nav of every HTML page on the site."""
import os, re, sys

ROOT = "d:/code/seo_deploy"

def add_search_link(filepath, content):
    """Insert search link between nav-links closing div and lang-switch div."""
    original = content

    # Pattern: </div> followed by <div class="lang-switch">
    # Replace with: </div>\n<a class="nav-search" href="...">🔍 搜索</a>\n<div class="lang-switch"

    # Determine if page is CN or EN
    is_en = '/en/' in filepath or filepath.replace('\\', '/').startswith('en/')

    if is_en:
        search_link = '<a href="/en/search.html" class="nav-search">🔍 Search</a>'
    else:
        search_link = '<a href="/search.html" class="nav-search">🔍 搜索</a>'

    # Replace the closing of nav-links before lang-switch
    old = '</div>\n<div class="lang-switch">'
    new = f'</div>\n            {search_link}\n            <div class="lang-switch">'

    if old in content:
        content = content.replace(old, new, 1)
        return content if content != original else original

    # Try without newline (compressed HTML)
    old = '</div><div class="lang-switch">'
    new = f'</div>{search_link}<div class="lang-switch">'
    if old in content:
        content = content.replace(old, new, 1)
        return content if content != original else original

    # Try with only nav-links closing div
    m = re.search(r'(<div class="nav-links">.*?</div>)', content, re.DOTALL)
    if not m:
        return original

    nav_div = m.group(1)
    new_nav = nav_div + ' ' + search_link + ' '
    # Find and replace
    content = content.replace(nav_div, new_nav, 1)
    return content if content != original else original

def main():
    os.chdir(ROOT)
    count = 0
    skipped = 0

    for root, dirs, files in os.walk('.'):
        if 'seo_fix_package' in root or 'output' in root:
            continue
        for fname in files:
            if not fname.endswith('.html'):
                continue

            filepath = os.path.join(root, fname).replace('\\', '/')
            relpath = os.path.relpath(filepath, '.').replace('\\', '/')

            # Skip already-fixed pages (search pages themselves)
            if relpath in ('search.html', 'en/search.html'):
                # Ensure they have their own nav correctly
                continue

            with open(filepath, 'rb') as f:
                raw = f.read()
            content = raw.decode('utf-8', errors='replace')

            # Check if already has nav-search
            if 'class="nav-search"' in content:
                skipped += 1
                continue

            # Must have nav-links to add search to
            if 'class="nav-links"' not in content:
                skipped += 1
                continue

            new_content = add_search_link(relpath, content)
            if new_content != content:
                with open(filepath, 'wb') as f:
                    f.write(new_content.encode('utf-8'))
                count += 1
                if count % 20 == 0:
                    print(f"  {count} files...")
            else:
                skipped += 1

    print(f"\nAdded search link: {count} files")
    print(f"Skipped: {skipped} files")

if __name__ == '__main__':
    main()
