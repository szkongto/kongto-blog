#!/usr/bin/env python3
"""
图片压缩脚本 - 优化博客图片
功能：
1. 压缩超过500KB的图片到指定大小
2. 限制最大尺寸（如1920px）
3. 转换为WebP格式（可选）
4. 输出压缩报告
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

# 配置
MAX_SIZE_KB = 500  # 最大文件大小 KB
MAX_WIDTH = 1920   # 最大宽度
MAX_HEIGHT = 1080  # 最大高度
QUALITY = 85       # JPEG质量
IMAGES_DIR = "images"
BACKUP_DIR = "images_backup_compressed"

class ImageOptimizer:
    def __init__(self):
        self.check_tools()
        self.stats = {"total": 0, "compressed": 0, "skipped": 0, "errors": 0}
        self.backup_dir = None

    def check_tools(self):
        """检查图片处理工具 - 优先使用Pillow"""
        print("使用Pillow (Python) 进行图片压缩")
        self.converter = "python"

    def create_backup(self):
        """创建备份目录"""
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            print(f"创建备份目录: {BACKUP_DIR}")
        self.backup_dir = BACKUP_DIR

    def backup_file(self, filepath):
        """备份原文件"""
        rel_path = os.path.relpath(filepath, ".")
        backup_path = os.path.join(BACKUP_DIR, rel_path)
        backup_dir = os.path.dirname(backup_path)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        if not os.path.exists(backup_path):
            shutil.copy2(filepath, backup_path)

    def compress_with_imagemagick(self, filepath, output_path):
        """使用ImageMagick压缩"""
        cmd = [
            "magick" if shutil.which("magick") else "convert",
            filepath,
            "-resize", f"{MAX_WIDTH}x{MAX_HEIGHT}>",
            "-quality", str(QUALITY),
            "-strip",
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def compress_with_python(self, filepath, output_path):
        """使用Python PIL/Pillow压缩"""
        try:
            from PIL import Image
        except ImportError:
            print("需要安装 Pillow: pip install Pillow")
            sys.exit(1)

        img = Image.open(filepath)

        # 调整尺寸
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)

        # 转换RGB（如果是RGBA）
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # 保存
        img.save(output_path, "JPEG", quality=QUALITY, optimize=True)

    def optimize_image(self, filepath):
        """优化单张图片"""
        self.stats["total"] += 1
        size_kb = os.path.getsize(filepath) / 1024

        if size_kb <= MAX_SIZE_KB:
            self.stats["skipped"] += 1
            print(f"  跳过 (大小合适): {filepath} ({size_kb:.1f}KB)")
            return False

        # 备份
        self.backup_file(filepath)

        # 生成输出路径
        dir_name = os.path.dirname(filepath)
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        ext = os.path.splitext(filepath)[1].lower()

        # 如果是JPEG，用jpg后缀
        if ext in ['.jpg', '.jpeg']:
            output_path = filepath  # 直接覆盖
        else:
            output_path = os.path.join(dir_name, f"{base_name}_opt.jpg")

        try:
            if self.converter == "imagemagick":
                self.compress_with_imagemagick(filepath, output_path)
            else:
                self.compress_with_python(filepath, output_path)

            new_size_kb = os.path.getsize(output_path) / 1024
            saved = size_kb - new_size_kb
            print(f"  ✓ 压缩: {filepath}")
            print(f"    {size_kb:.1f}KB → {new_size_kb:.1f}KB (节省 {saved:.1f}KB, {saved/size_kb*100:.0f}%)")
            self.stats["compressed"] += 1
            return True
        except Exception as e:
            print(f"  ✗ 错误: {filepath} - {e}")
            self.stats["errors"] += 1
            return False

    def optimize_directory(self, directory):
        """优化整个目录"""
        print(f"\n扫描目录: {directory}")

        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    filepath = os.path.join(root, filename)
                    self.optimize_image(filepath)

    def print_report(self):
        """打印压缩报告"""
        print("\n" + "=" * 50)
        print("图片压缩报告")
        print("=" * 50)
        print(f"总图片数: {self.stats['total']}")
        print(f"已压缩: {self.stats['compressed']}")
        print(f"已跳过: {self.stats['skipped']} (大小合适)")
        print(f"错误数: {self.stats['errors']}")
        if self.backup_dir:
            print(f"\n备份目录: {self.backup_dir}/")
            print("如需恢复，运行: cp -r images_backup_compressed/* images/")
        print("=" * 50)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="优化博客图片")
    parser.add_argument("--max-size", type=int, default=500, help="最大文件大小 KB (默认: 500)")
    parser.add_argument("--max-width", type=int, default=1920, help="最大宽度 px (默认: 1920)")
    parser.add_argument("--quality", type=int, default=85, help="JPEG质量 (默认: 85)")
    parser.add_argument("--no-backup", action="store_true", help="跳过备份")
    parser.add_argument("directory", nargs="?", default="images", help="图片目录")
    args = parser.parse_args()

    global MAX_SIZE_KB, MAX_WIDTH, MAX_HEIGHT, QUALITY
    MAX_SIZE_KB = args.max_size
    MAX_WIDTH = args.max_width
    MAX_HEIGHT = 1080
    QUALITY = args.quality

    optimizer = ImageOptimizer()

    if not args.no_backup:
        optimizer.create_backup()

    optimizer.optimize_directory(args.directory)
    optimizer.print_report()

if __name__ == "__main__":
    main()
