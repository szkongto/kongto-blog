"""Analyze Screaming Frog exported reports for cncdisplay.com"""
import pandas as pd
from pathlib import Path

DIR = Path(__file__).parent

# 1. Internal URLs
internal = pd.read_excel(DIR / "internal_all.xlsx")
# Find status code column - might be named differently
status_col = [c for c in internal.columns if "status" in str(c).lower() or "code" in str(c).lower()]
status_col = status_col[0] if status_col else internal.columns[2]

internal["status_str"] = internal[status_col].astype(str)
print("=== 全站概览 ===")
print(f"总URL数: {len(internal)}")
print(f"2xx正常: {len(internal[internal['status_str'].str.startswith('2')])}")
print(f"3xx跳转: {len(internal[internal['status_str'].str.startswith('3')])}")
print(f"4xx断链: {len(internal[internal['status_str'].str.startswith('4')])}")
print(f"5xx错误: {len(internal[internal['status_str'].str.startswith('5')])}")

# Top-level path breakdown
if "Address" in internal.columns:
    internal["path"] = internal["Address"].str.replace("https://cncdisplay.com", "").str.split("/").str[1]
    print(f"\n=== 目录分布 ===")
    print(internal[internal["status_str"].str.startswith("2")]["path"].value_counts().head(15).to_string())

# 2. Response Codes
codes = pd.read_excel(DIR / "response_codes_all.xlsx")
sc = [c for c in codes.columns if "status" in str(c).lower() or "code" in str(c).lower()]
sc = sc[0] if sc else codes.columns[1]
addr = "Address" if "Address" in codes.columns else codes.columns[0]

print(f"\n=== 断链分析 ===")
broken = codes[codes[sc].astype(str).str.startswith("4")]
print(f"4xx总数: {len(broken)}")
for code in sorted(broken[sc].unique()):
    cnt = len(broken[broken[sc] == code])
    print(f"  {code}: {cnt} 个")

# Top broken URLs
print(f"\n=== Top 20 断链 ===")
for _, row in broken.head(20).iterrows():
    print(f"  {row[sc]} | {str(row.get(addr, ''))[:100]}")

# 3. Page Titles
titles = pd.read_excel(DIR / "page_titles_all.xlsx")
print(f"\n=== 页面标题分析 ===")
print(f"总页面数: {len(titles)}")

# Check for duplicates
title_col = [c for c in titles.columns if "title" in str(c).lower() and "meta" in str(c).lower()]
title_col = title_col[0] if title_col else [c for c in titles.columns if "title" in str(c).lower()][0]

dupes = titles[titles.duplicated(subset=[title_col], keep=False)]
print(f"重复标题: {len(dupes.drop_duplicates(subset=[title_col]))} 组")
for t, group in dupes.groupby(title_col):
    print(f"  「{str(t)[:60]}」x{len(group)}")
    for _, r in group.head(3).iterrows():
        addr_c = "Address" if "Address" in r.index else r.index[0]
        print(f"    → {r[addr_c][:80]}")
    print()

# 4. Hreflang
try:
    hrf = pd.read_excel(DIR / "hreflang_all.xlsx")
    print(f"\n=== Hreflang 分析 ===")
    print(f"总hreflang条目: {len(hrf)}")
    if "Issue" in hrf.columns:
        issues = hrf["Issue"].value_counts()
        print(f"问题分布:")
        for issue, cnt in issues.items():
            print(f"  {issue}: {cnt}")
except:
    print("\n=== Hreflang: 无导出 ===")

# 5. Structured Data
sd = pd.read_excel(DIR / "structured_data_all.xlsx")
print(f"\n=== Schema 结构化数据 ===")
print(f"总条目: {len(sd)}")
# Types
type_col = [c for c in sd.columns if "type" in str(c).lower()][0]
print(f"Schema类型分布:")
for t, cnt in sd[type_col].value_counts().head(15).items():
    print(f"  {t}: {cnt}")
