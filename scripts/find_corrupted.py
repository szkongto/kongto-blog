"""Scan all files for encoding corruption"""
import subprocess, re, sys
from pathlib import Path

ROOT = Path("d:/code/seo_deploy")
PRE_COMMIT = "64f6e321"
sys.stdout.reconfigure(encoding='utf-8')

CORRUPTION_MARKERS = set('鍙戦偅绉鏄剧ず鍣崌绾柟妗娣卞湷甯傛睙浘绉戞妧鏈夐檺鍏稿凡涓嬭浇彇鎶ヤ环棰樼殑鎴戜滑')

def has_corruption(text):
    cn = [c for c in text if '一' <= c <= '鿿']
    if len(cn) < 5:
        return False
    bad = sum(1 for c in cn if c in CORRUPTION_MARKERS)
    return bad / len(cn) > 0.3

def get_prev(rel):
    try:
        r = subprocess.run(["git", "show", f"{PRE_COMMIT}:{rel}"],
            capture_output=True, encoding='utf-8', cwd=ROOT, timeout=10)
        return r.stdout if r.returncode == 0 else None
    except: return None

print("Scanning for encoding corruption...")
corrupted = []
for f in sorted(ROOT.rglob("*.html")):
    rel = str(f.relative_to(ROOT)).replace("\\", "/")
    if ".git" in rel or "screaming_frog" in rel:
        continue
    current = f.read_text('utf-8', errors='ignore')
    if not has_corruption(current):
        continue

    # Check key areas
    matches = re.findall(r'<title>(.+?)<|"name":\s*"([^"]{3,})"|>([^<]{2,10})</a>', current)
    bad_areas = [m[0] or m[1] or m[2] for m in matches[:5] if has_corruption(m[0] or m[1] or m[2])]
    if not bad_areas:
        continue

    prev = get_prev(rel)
    if prev:
        cur_cn = set(re.findall(r'[一-鿿]+', current)[:30])
        prev_cn = set(re.findall(r'[一-鿿]+', prev)[:30])
        if cur_cn and prev_cn:
            sim = len(cur_cn & prev_cn) / max(len(cur_cn), len(prev_cn))
            if sim > 0.5:
                continue  # Not actually corrupted, false positive
    corrupted.append((rel, bad_areas[:3]))

print(f"\nCorrupted files: {len(corrupted)}")
for rel, areas in sorted(corrupted):
    print(f"  BROKEN: {rel}")
    for a in areas:
        print(f"    -> {a[:50]}")
