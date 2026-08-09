# -*- coding: utf-8 -*-
"""P1-5 量化: 同一型号在不同文件名里的分隔符/大小写不一致
方法: 提取文件名中含数字的 token(型号必含数字), 去除日期(>=6位纯数字),
     归一化(去分隔符+小写)分组, 同归一化但有>=2种原始拼写 => 不一致
"""
import io, sys, re, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP = {'en_bak','_archive','_archive_audit','_templates','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output','__pycache__',
        'seo_reports','data','docs','scripts'}

files = [f.replace('\\','/') for f in glob.glob('**/*.html', recursive=True)]
files = [f for f in files if not any(f.startswith(s+'/') or '/node_modules/' in f for s in SKIP)]

# 含数字的 token: 字母数字连字符下划线连续串, 内含至少一个数字
TOKEN_RE = re.compile(r'(?i)[a-z0-9_-]{2,}')

def model_tokens(base):
    """返回 {canonical: 原始token}，过滤日期和纯词"""
    out = {}
    for m in TOKEN_RE.finditer(base):
        tok = m.group(0)
        if not re.search(r'\d', tok):
            continue  # 无数字 => 不是型号
        if re.fullmatch(r'\d{6,}', tok):
            continue  # 日期/序列号
        if re.fullmatch(r'\d{2}', tok):
            continue  # 两位数年份
        canon = re.sub(r'[-_]', '', tok).lower()
        if len(canon) < 3:
            continue
        out.setdefault(canon, set()).add(tok)
    return out

by_canon = defaultdict(lambda: defaultdict(list))
for f in files:
    base = os.path.basename(f).replace('.html','').replace('-zh','').replace('_zh','')
    for canon, spellings in model_tokens(base).items():
        for s in spellings:
            by_canon[canon][s].append(f)

inconsistent = {c: sp for c, sp in by_canon.items() if len(sp) > 1}
affected = set()
for c, sp in inconsistent.items():
    for fl in sp.values():
        affected.update(fl)

print('== 型号不一致族: %d 个 ==' % len(inconsistent))
print('受影响文件总数: %d' % len(affected))
print()
for c in sorted(inconsistent, key=lambda x: -sum(len(v) for v in inconsistent[x].values())):
    sp = inconsistent[c]
    total = sum(len(v) for v in sp.values())
    print('canon=%s  共%d文件  %d种拼写' % (c, total, len(sp)))
    for spelling, fl in sorted(sp.items(), key=lambda x: -len(x[1])):
        print('   %-38s x%-3d %s%s' % (spelling, len(fl), fl[0], ' ...' if len(fl)>1 else ''))
