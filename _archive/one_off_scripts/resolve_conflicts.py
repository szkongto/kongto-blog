#!/usr/bin/env python3
"""
Resolve merge conflicts in 3 files:
- about.html
- compatibility-matrix.html
- en/compatibility-matrix.html

Strategy:
- Nav: Keep version with 兼容查询 (my change)
- <head>: Keep version with more SEO tags (remote)
- Language switcher: Keep version linking to same page (remote)
"""
import os, re

repo = '.'

conflict_files = [
    'about.html',
    'compatibility-matrix.html',
    'en/compatibility-matrix.html'
]

def resolve_conflicts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<<<<<<<' not in content:
        print(f"  No conflicts in {filepath}")
        return False
    
    # Find all conflict blocks
    parts = re.split(r'<<<<<<< .*?\n', content)
    resolved_parts = []
    
    for i, part in enumerate(parts):
        if '=======\n' in part and '>>>>>>> ' in part:
            # This is a conflict block
            ours, theirs = part.split('=======\n', 1)
            theirs = theirs.split('>>>>>>> ', 1)[0]
            
            # Resolution logic
            resolved = None
            
            # Rule 1: Nav conflict - keep version with 兼容查询
            if '兼容查询' in ours or '兼容查询' in theirs:
                if '兼容查询' in ours:
                    resolved = ours
                else:
                    resolved = theirs
            
            # Rule 2: <head> conflict - keep version with more SEO tags
            elif '<head>' in ours or '<head>' in theirs or 'schema.org' in ours or 'schema.org' in theirs:
                # Count SEO tags in each version
                ours_tags = len(re.findall(r'<meta |<link |schema.org', ours))
                theirs_tags = len(re.findall(r'<meta |<link |schema.org', theirs))
                if ours_tags >= theirs_tags:
                    resolved = ours
                else:
                    resolved = theirs
            
            # Rule 3: Language switcher - keep version linking to same page
            elif 'lang-zh' in ours or 'lang-en' in ours:
                # Check if links point to same page (not homepage)
                if '/en/compatibility-matrix.html' in ours or '/compatibility-matrix.html' in ours:
                    resolved = ours
                elif '/en/compatibility-matrix.html' in theirs or '/compatibility-matrix.html' in theirs:
                    resolved = theirs
                else:
                    # Default: keep ours
                    resolved = ours
            
            # Default: keep ours (remote)
            if resolved is None:
                resolved = ours
            
            resolved_parts.append(resolved)
        else:
            # No conflict in this part
            resolved_parts.append(part)
    
    # Reconstruct content
    resolved_content = ''.join(resolved_parts)
    
    # Clean up any remaining conflict markers (shouldn't happen)
    resolved_content = re.sub(r'<<<<<<< .*\n', '', resolved_content)
    resolved_content = re.sub(r'=======\n', '', resolved_content)
    resolved_content = re.sub(r'>>>>>>> .*\n', '', resolved_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(resolved_content)
    
    print(f"  [OK] Resolved conflicts in {filepath}")
    return True

print("=== Resolving Merge Conflicts ===")
for f in conflict_files:
    fpath = os.path.join(repo, f)
    if os.path.exists(fpath):
        print(f"\nResolving {f}...")
        resolve_conflicts(fpath)
    else:
        print(f"  File not found: {fpath}")

print("\n=== DONE ===")
print("Run: git add about.html compatibility-matrix.html en/compatibility-matrix.html")
print("Then: git commit -m 'Merge remote changes and resolve conflicts'")
print("Then: git push origin main")
