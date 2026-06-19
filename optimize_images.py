#!/usr/bin/env python
"""
全站图片优化脚本 v2
- 尺寸优化: 最大宽度/高度 1200px (保持比例)
- 大小优化: JPEG quality 82 + progressive + optimize
- PNG: quantize 256色 + optimize
- 创建备份: images_backup_YYYYMMDD_HHMMSS/
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

BASE = Path('d:/code/seo_deploy')
EXTS = {'.jpg', '.jpeg', '.png'}
SKIP_DIRS = {'images_backup_compressed', 'images_backup'}
MAX_DIM = 1200
JPEG_QUALITY = 82
MIN_SKIP_KB = 15  # skip images < 15KB already within size limits


class Stats:
    def __init__(self):
        self.total_before = 0.0
        self.total_after = 0.0
        self.count = 0
        self.skipped = 0
        self.resized = 0
        self.compressed_only = 0
        self.errors = []


def optimize_image(filepath, rel_path, stats):
    """Optimize a single image. Returns (before_kb, after_kb)."""
    before_kb = os.path.getsize(filepath) / 1024

    try:
        img = Image.open(filepath)
    except Exception as e:
        stats.errors.append(f"OPEN: {rel_path} - {e}")
        return (before_kb, before_kb)

    w, h = img.size

    # Skip tiny already-optimized images
    if before_kb < MIN_SKIP_KB and w <= MAX_DIM and h <= MAX_DIM:
        stats.skipped += 1
        return (before_kb, before_kb)

    # Resize if oversized
    needs_resize = w > MAX_DIM or h > MAX_DIM
    if needs_resize:
        ratio = min(MAX_DIM / w, MAX_DIM / h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        try:
            img = img.resize((new_w, new_h), Image.LANCZOS)
        except (ValueError, OSError):
            img = img.convert('RGB').resize((new_w, new_h), Image.LANCZOS)
        stats.resized += 1
    else:
        stats.compressed_only += 1

    # Compress
    ext = filepath.suffix.lower()
    if ext in ('.jpg', '.jpeg'):
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        img.save(filepath, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
    elif ext == '.png':
        save_kwargs = {'optimize': True}
        if img.mode not in ('RGBA', 'PA', 'P') or (img.mode == 'P' and 'transparency' not in img.info):
            try:
                converted = img.convert('RGB')
                img = converted.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
            except Exception:
                pass
        img.save(filepath, 'PNG', **save_kwargs)

    after_kb = os.path.getsize(filepath) / 1024
    return (before_kb, after_kb)


def find_images():
    """Yield all image paths excluding backup dirs."""
    for filepath in BASE.rglob('*'):
        if filepath.suffix.lower() not in EXTS:
            continue
        parts = set(str(filepath.relative_to(BASE)).split(os.sep))
        if parts & SKIP_DIRS:
            continue
        yield filepath


def main():
    stats = Stats()

    print("=" * 62)
    print("  cncdisplay.com 全站图片优化")
    print(f"  最大尺寸: {MAX_DIM}px | JPEG质量: {JPEG_QUALITY} | Progressive: ON")
    print("=" * 62)

    all_images = list(find_images())
    if not all_images:
        print("未找到图片。")
        return

    print(f"\n  扫描到 {len(all_images)} 张图片，分析中...")

    # Analyze
    plan = []
    total_scan = 0.0
    for filepath in all_images:
        try:
            img = Image.open(filepath)
            w, h = img.size
        except Exception:
            print(f"  SKIP: {filepath.relative_to(BASE)} (无法打开)")
            continue
        size_kb = os.path.getsize(filepath) / 1024
        total_scan += size_kb
        if size_kb < MIN_SKIP_KB and w <= MAX_DIM and h <= MAX_DIM:
            continue
        plan.append((filepath, w > MAX_DIM or h > MAX_DIM, size_kb, w, h))

    if not plan:
        print("  所有图片已优化，无需处理。")
        return

    oversized = sum(1 for _, needs_r, _, _, _ in plan if needs_r)
    print(f"  当前: {total_scan/1024:.1f} MB | 优化 {len(plan)} 张 | 缩尺寸 {oversized} 张")

    # Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE / f'images_backup_{ts}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    for filepath, _, _, _, _ in plan:
        rel = filepath.relative_to(BASE)
        dest = backup_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, dest)
    print(f"  备份: {backup_dir.name}/\n")

    # Optimize
    print(f"  {'图像文件':<52} {'优化前':>7} {'优化后':>7} {'变化':>6}")
    print(f"  {'-'*52} {'-'*7} {'-'*7} {'-'*6}")

    for filepath, needs_resize, before_kb, orig_w, orig_h in plan:
        rel_path = filepath.relative_to(BASE)
        before, after = optimize_image(filepath, rel_path, stats)
        stats.total_before += before
        stats.total_after += after
        stats.count += 1

        change = before - after
        pct = (change / before * 100) if before > 0 else 0
        marker = 'S' if needs_resize else 'C'
        name = str(rel_path)
        if len(name) > 50:
            name = '...' + name[-47:]
        print(f"  [{marker}] {name:<50} {before:>6.0f}K {after:>6.0f}K {pct:>+5.0f}%")

    # Summary
    saved_mb = (stats.total_before - stats.total_after) / 1024
    saved_pct = ((stats.total_before - stats.total_after) / stats.total_before * 100) if stats.total_before > 0 else 0

    print(f"\n{'='*62}")
    print(f"  优化完成!")
    print(f"{'='*62}")
    print(f"  处理: {stats.count} 张 | 缩尺寸: {stats.resized} | 仅压缩: {stats.compressed_only}")
    print(f"  优化前: {stats.total_before/1024:.1f} MB → 优化后: {stats.total_after/1024:.1f} MB")
    print(f"  节省: {saved_mb:.1f} MB ({saved_pct:.1f}%)")
    print(f"  备份: {backup_dir.name}/")
    if stats.errors:
        print(f"  错误: {len(stats.errors)} 张")
        for e in stats.errors[:5]:
            print(f"    - {e}")
    print()


if __name__ == '__main__':
    main()
