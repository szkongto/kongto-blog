# -*- coding: utf-8 -*-
"""P1-2 图片原位压缩 — cncdisplay.com
只处理活跃站点图片 (git 追踪的 images/ 及文章内嵌图), 跳过备份/归档/构建目录。
策略: 超过阈值才压缩; 保持路径/尺寸不变 (引用不断); 只在小尺寸覆盖 (绝不反向增大)。
  JPEG: quality 82 + optimize + progressive
  WEBP: quality 80 + method 6
  PNG : RGBA 全不透明 -> 转 RGB 存; optimize + compress_level 9
用法: python scripts/compress_images.py [--threshold 200] [--dry]
"""
import io, sys, os, glob, argparse, subprocess
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SKIP = {'en_bak', '_archive', '_archive_audit', '_templates', 'node_modules', '.git',
        '.github', 'backlinks_output', 'backlinks_daily', 'screaming_frog_reports',
        'output', '__pycache__', 'seo_reports', 'data', 'docs', 'scripts',
        'images_backup_20260809_035304', 'images_backup_compressed'}

PATTERNS = ['*.jpg', '*.jpeg', '*.png', '*.webp']


def list_active_images():
    out = []
    for pat in PATTERNS:
        for f in glob.glob('**/' + pat, recursive=True):
            fs = f.replace('\\', '/')
            if any(fs.startswith(s + '/') for s in SKIP):
                continue
            if is_tracked(fs):
                out.append(fs)
    return out


def is_tracked(fs):
    # 只看 git 追踪的图片 (活跃站点), 跳过 untracked 的工作区文件
    return subprocess.call(['git', 'ls-files', '--error-unmatch', fs],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           shell=False) == 0


def compress(fs, threshold, dry):
    sz0 = os.path.getsize(fs)
    if sz0 <= threshold:
        return None
    ext = fs.rsplit('.', 1)[-1].lower()
    try:
        im = Image.open(fs)
        im.load()
    except Exception as e:
        print('  SKIP(打不开) %s: %s' % (fs, e))
        return None

    if im.mode in ('RGBA', 'LA', 'PA'):
        # alpha 通道是否全不透明 -> 可安全转 RGB 减小体积
        if 'A' in im.getbands():
            alpha = im.getchannel('A').getextrema()
            if alpha == (255, 255):
                im = im.convert('RGB')
    elif im.mode not in ('RGB', 'P'):
        try:
            im = im.convert('RGB')
        except Exception:
            pass

    buf = io.BytesIO()
    if ext in ('jpg', 'jpeg'):
        im.save(buf, 'JPEG', quality=82, optimize=True, progressive=True)
    elif ext == 'webp':
        im.save(buf, 'WEBP', quality=80, method=6)
    elif ext == 'png':
        im.save(buf, 'PNG', optimize=True, compress_level=9)
    else:
        return None
    new = len(buf.getvalue())

    # 最小收益门槛: 省 >=1KB 且 >=2%, 否则跳过 (避免无谓二次压缩累积质量损失)
    if new >= sz0 or (sz0 - new) < 1024 or (sz0 - new) * 100 < sz0 * 2:
        print('  SKIP(收益不足) %s %.1fK->%.1fK' % (fs, sz0 / 1024, new / 1024))
        return None

    if not dry:
        with open(fs, 'wb') as f:
            f.write(buf.getvalue())
    print('  %-70s %.1fK -> %.1fK  (省 %.1fK)' % (fs, sz0 / 1024, new / 1024, (sz0 - new) / 1024))
    return sz0 - new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--threshold', type=int, default=200, help='超过该 KB 才压 (默认200)')
    ap.add_argument('--dry', action='store_true', help='只统计不写盘')
    a = ap.parse_args()

    th = a.threshold * 1024
    imgs = list_active_images()
    print('活跃图片数: %d, 阈值: %dKB' % (len(imgs), a.threshold))

    saved = 0
    done = 0
    for fs in imgs:
        r = compress(fs, th, a.dry)
        if r:
            saved += r
            done += 1
    print('\n完成 %d 张, 共省 %.1fMB%s' % (done, saved / 1048576, ' (dry-run)' if a.dry else ''))


if __name__ == '__main__':
    main()
