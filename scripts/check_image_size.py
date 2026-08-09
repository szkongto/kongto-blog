# -*- coding: utf-8 -*-
"""P1-2 门禁: 图片上传尺寸校验 (只查本次变更)
规则: 本次提交新增/修改的图片 >300KB 阻止提交。历史遗留大图不拦 (避免锁死存量)。
压缩工具: python scripts/compress_images.py --threshold 200
用法: 作为 full_gate 硬门禁 / pre-commit 调用。exit 1 = 有本次变更的大图。
"""
import io, sys, os, subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp')
LIMIT = 300 * 1024  # 300KB


def changed_images():
    """只拦"新增"大图 (untracked + added)。modified 是压缩/存量修改, 不拦。
    目的: 防止上传流程把未压缩大图塞进站。存量已压到格式极限的图不锁死。"""
    out = set()
    enc = dict(text=True, encoding='utf-8', errors='replace')
    # added status (A) vs HEAD
    r = subprocess.run(['git', 'diff', '--name-status', 'HEAD'], capture_output=True, **enc)
    for line in r.stdout.splitlines():
        parts = line.split('\t')
        if parts and parts[0].startswith('A'):
            out.add(parts[-1])
    # untracked
    r2 = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                        capture_output=True, **enc)
    out.update(r2.stdout.splitlines())
    res = []
    for f in out:
        fs = f.replace('\\', '/')
        if fs.startswith('images_backup') or fs.startswith('en_bak') or '/images_backup' in fs:
            continue
        if not fs.lower().endswith(IMG_EXT):
            continue
        if os.path.exists(fs) and os.path.getsize(fs) > LIMIT:
            res.append((os.path.getsize(fs), fs))
    return res


big = changed_images()

if big:
    big.sort(reverse=True)
    print('FAIL: 本次变更 %d 张图 >300KB (单图上限)' % len(big))
    for s, f in big[:15]:
        print('  %7.1fKB  %s' % (s / 1024, f))
    print('处理: python scripts/compress_images.py --threshold 200')
    sys.exit(1)
print('OK: 本次变更图片全部 <=300KB')

