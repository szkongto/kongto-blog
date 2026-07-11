"""Rollback Phase 0b: restore /en/ + Chinese root."""
import os, shutil
ROOT = r"d:\code\seo_deploy"
EN_DIR = os.path.join(ROOT, "en")
EN_BAK = os.path.join(ROOT, "en_bak")
ZH_DIR = os.path.join(ROOT, "zh")

# 1. Restore /en/
if os.path.exists(EN_BAK):
    if os.path.exists(EN_DIR):
        shutil.rmtree(EN_DIR)
    shutil.copytree(EN_BAK, EN_DIR)
    print("Restored /en/")

# 2. Restore Chinese root from /zh/
for fname in os.listdir(ZH_DIR):
    if fname.endswith('.html'):
        shutil.copy2(os.path.join(ZH_DIR, fname), os.path.join(ROOT, fname))
print("Restored root Chinese files")

# 3. Restore Chinese subdirectories
for subdir in ['brands', 'products', 'posts']:
    src = os.path.join(ZH_DIR, subdir)
    dst = os.path.join(ROOT, subdir)
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"Restored root guides/")

print("Rollback complete. Restore _redirects from git: git checkout _redirects")
