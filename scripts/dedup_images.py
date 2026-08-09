# -*- coding: utf-8 -*-
"""P1-2 图片去重 — 删除零引用冗余副本
策略:
  1. 全站活跃图片按 MD5 分组 (仅压缩后的活跃文件)
  2. 全仓库文本 (非图片) 搜 basename 引用计数, 含 src/href/CSS/JS/OG/JSON-LD
  3. 每组选引用最多的为 keep; 其余若自身零引用 -> 安全删 (dry 默认, --commit 才删)
  4. 被引用的重复项不删 (恢复期风险) — 只报告
用法: python scripts/dedup_images.py [--commit]
"""
import io, sys, os, glob, hashlib, re, argparse, subprocess
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SKIP = {'en_bak', '_archive', '_archive_audit', '_templates', 'node_modules', '.git',
        '.github', 'backlinks_output', 'backlinks_daily', 'screaming_frog_reports',
        'output', '__pycache__', 'seo_reports', 'data', 'docs', 'scripts',
        'images_backup_20260809_035304', 'images_backup_compressed'}


def active_images():
    out = []
    for pat in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        for f in glob.glob('**/' + pat, recursive=True):
            fs = f.replace('\\', '/')
            if any(fs.startswith(s + '/') for s in SKIP):
                continue
            if subprocess.call(['git', 'ls-files', '--error-unmatch', fs],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                out.append(fs)
    return out


def ref_counts():
    """basename.lower() -> (count, [files]) 全仓库非图片文本"""
    cnt = defaultdict(int)
    where = defaultdict(set)
    pat = re.compile(r'([\w\-\.]+\.(?:jpg|jpeg|png|webp))', re.I)
    for f in glob.glob('**/*', recursive=True):
        fs = f.replace('\\', '/')
        if os.path.isdir(f):
            continue
        if any(fs.startswith(s + '/') for s in SKIP):
            continue
        ext = fs.rsplit('.', 1)[-1].lower() if '.' in fs else ''
        if ext in ('jpg', 'jpeg', 'png', 'webp', 'gif'):
            continue
        try:
            txt = open(f, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for m in pat.finditer(txt):
            b = m.group(1).lower()
            cnt[b] += 1
            where[b].add(fs)
    return cnt, where


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', action='store_true', help='真正执行删除')
    a = ap.parse_args()

    imgs = active_images()
    by = defaultdict(list)
    for f in imgs:
        by[hashlib.md5(open(f, 'rb').read()).hexdigest()].append(f)
    dups = {k: v for k, v in by.items() if len(v) > 1}

    cnt, where = ref_counts()

    to_del = []
    risky = []
    for group in dups.values():
        best = max(group, key=lambda g: cnt.get(os.path.basename(g).lower(), 0))
        for g in group:
            if g == best:
                continue
            rc = cnt.get(os.path.basename(g).lower(), 0)
            if rc == 0:
                to_del.append(g)
            else:
                risky.append((g, best, rc))

    total = sum(os.path.getsize(f) for f in to_del) / 1048576
    print('重复组: %d, 冗余副本: %d (压缩后)' % (len(dups), sum(len(v) - 1 for v in dups.values())))
    print('安全删除(零引用): %d 个, %.1fMB' % (len(to_del), total))
    print('被引用重复项(不动): %d 个, %.1fMB' % (
        len(risky), sum(os.path.getsize(g) for g, _, _ in risky) / 1048576))

    if a.commit:
        for f in to_del:
            os.remove(f)
            print('  DEL %s' % f)
        print('\n已删除 %d 个' % len(to_del))
    else:
        print('\n--dry: 未删除. 加 --commit 执行')
        for f in sorted(to_del)[:10]:
            print('  DEL %s' % f)
        print('  ...共 %d 个' % len(to_del))


if __name__ == '__main__':
    main()
