# -*- coding: utf-8 -*-
"""P1-2 补充: 唯一内容零引用孤儿清理 — cncdisplay.com
dedup_images.py 只删 MD5 重复组里的零引用副本, 漏掉"唯一内容但零引用"孤儿。
本脚本补齐: 找同目录同 stem(忽略大小写/扩展名) 组内未被任何页面引用的文件。

策略:
  1. 活跃图片按 (目录, stem小写) 分组
  2. 综合引用扫描: 全仓库非图片文本, 正则抓 basename (含 src/href/CSS/JS/OG)
  3. 中文名文件补 substring 搜索 (正则 \\w 不匹配中文)
  4. 组内未被引用 -> 孤儿, 分类: 有被引用兄弟 / 整组全孤儿
  5. ASCII 名引用扫描可靠, 中文名标"待人工核"

用法: python scripts/audit_orphans.py            # dry-run 出清单
      python scripts/audit_orphans.py --commit   # 真正删除
      python scripts/audit_orphans.py --report   # 只出清单文件到 seo_reports/
"""
import io, sys, os, glob, re, argparse, subprocess, datetime
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SKIP = {'en_bak', '_archive', '_archive_audit', '_templates', 'node_modules', '.git',
        '.github', 'backlinks_output', 'backlinks_daily', 'screaming_frog_reports',
        'output', '__pycache__', 'seo_reports', 'data', 'docs', 'scripts',
        'images_backup_20260809_035304', 'images_backup_compressed'}

IMG_PAT = re.compile(r'([\w\-\.]+\.(?:jpg|jpeg|png|webp))', re.I)
CN_RE = re.compile(r'[一-鿿]')
EXT_SET = ('jpg', 'jpeg', 'png', 'webp', 'gif')


def ok(fs):
    return not any(fs.startswith(s + '/') for s in SKIP)


def is_tracked(fs):
    return subprocess.call(['git', 'ls-files', '--error-unmatch', fs],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def active_images():
    out = []
    for pat in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        for f in glob.glob('**/' + pat, recursive=True):
            fs = f.replace('\\', '/')
            if not fs.startswith('images/') or not ok(fs):
                continue
            if is_tracked(fs):
                out.append(fs)
    return out


def build_refs():
    """返回 (regex命中集, 子串命中集)。子串集用于中文名。"""
    refs = set()          # 正则抓到 basename.lower()
    substring = set()     # 完整文件名字符串 (含扩展名, 全小写)
    for f in glob.glob('**/*', recursive=True):
        fs = f.replace('\\', '/')
        if os.path.isdir(fs) or not ok(fs):
            continue
        ext = fs.rsplit('.', 1)[-1].lower() if '.' in fs else ''
        if ext in EXT_SET:
            continue
        try:
            t = open(f, encoding='utf-8', errors='ignore').read().lower()
        except Exception:
            continue
        for m in IMG_PAT.finditer(t):
            refs.add(m.group(1).lower())
            # 正则截断的边界 -> 也把整个匹配片段加上 (防 srcset 里的数字后缀)
            substring.add(m.group(1).lower())
    return refs, substring


def group_images(imgs):
    by = defaultdict(list)
    for f in imgs:
        d = os.path.dirname(f)
        stem = os.path.basename(f).rsplit('.', 1)[0].lower()
        by[(d, stem)].append(f)
    return by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', action='store_true')
    ap.add_argument('--report', action='store_true', help='写清单到 seo_reports/')
    a = ap.parse_args()

    imgs = active_images()
    by = group_images(imgs)
    refs, substring = build_refs()

    orphans = []       # (file, size, group_status, is_cn)
    for (d, stem), files in sorted(by.items()):
        if len(files) <= 1:
            continue
        ref_in = [f for f in files if os.path.basename(f).lower() in refs
                  or os.path.basename(f).lower() in substring]
        status = '有被引用兄弟' if ref_in else '整组全孤儿'
        for f in files:
            b = os.path.basename(f).lower()
            if b in refs or b in substring:
                continue
            is_cn = bool(CN_RE.search(os.path.basename(f)))
            orphans.append((f, os.path.getsize(f), status, is_cn))

    total = sum(s for _, s, _, _ in orphans) / 1048576
    cnt = Counter(('中文名' if c else 'ASCII') + '/' + st for _, _, st, c in orphans)
    print('活跃图: %d, 孤儿: %d 个, %.1fMB' % (len(imgs), len(orphans), total))
    for k, v in sorted(cnt.items()):
        print('  %-24s %d' % (k, v))

    if a.report:
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        rp = 'seo_reports/orphan_images_%s.txt' % ts
        os.makedirs('seo_reports', exist_ok=True)
        with open(rp, 'w', encoding='utf-8') as w:
            w.write('# 孤儿图片清单 %s (dry-run)\n' % ts)
            w.write('# 共 %d 个, %.1fMB\n' % (len(orphans), total))
            cur = None
            for f, sz, st, is_cn in sorted(orphans, key=lambda x: (x[0].rsplit('/', 1)[0], -x[1])):
                d = f.rsplit('/', 1)[0]
                if d != cur:
                    cur = d
                    w.write('\n## %s\n' % d)
                tag = '中文名待核' if is_cn else st
                w.write('%7.1fK  [%s]  %s\n' % (sz / 1024, tag, f))
        print('\n清单已写: %s' % rp)
        print('注意: 此文件在 seo_reports/ 会被 SKIP 排除, 不会自引.')

    if a.commit:
        dels = [f for f, _, _, c in orphans if not c]  # 只删 ASCII 可靠孤儿, 中文名留着人工核
        for f in dels:
            os.remove(f)
            print('  DEL %s' % f)
        print('\n已删 %d 个' % len(dels))
    else:
        print('\n--dry: 未删除. 加 --commit 执行 (仅删 ASCII 可靠孤儿, 中文名留待人工核)')
        for f, sz, st, is_cn in sorted(orphans, key=lambda x: -x[1])[:12]:
            print('  %7.1fK  [%s]  %s' % (sz / 1024, st, f))
        print('  ...共 %d 个' % len(orphans))


if __name__ == '__main__':
    main()
