import os, glob

BASE = r"D:\code\seo_deploy"
test_file = BASE + r"\posts\article_20260503_FANUC_A61L_0001_0093_LCD.html"
en_file = BASE + r"\en\posts\article_20260503_FANUC_A61L_0001_0093_LCD.html"

# Test Chinese file
print(f"Chinese file exists: {os.path.isfile(test_file)}")
with open(test_file, 'r', encoding='utf-8') as f:
    c = f.read()
print(f"Chinese file length: {len(c)}")
print(f"Is redirect (refresh): {'http-equiv=\"refresh\"' in c}")
print(f"Is redirect (single quote): {'http-equiv' in c and 'refresh' in c.split('http-equiv')[1][:20]}")

# Test English file
with open(en_file, 'r', encoding='utf-8') as f:
    c2 = f.read()
print(f"\nEnglish file length: {len(c2)}")
# Find hreflang zh-CN
for line in c2.split('\n'):
    if 'hreflang="zh-CN"' in line:
        print(f"hreflang zh-CN: {line.strip()}")
    if 'lang-zh' in line and 'class="lang-zh"' in line:
        print(f"lang-zh btn: {line.strip()}")
