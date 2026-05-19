#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复HTML文件中未闭合的title标签"""

import os
import re

# 有问题的文件列表
FILES = [
    "./posts/article_20260506_三菱BM09DF工业显示屏E60数控系统TFT替代.html",
    "./posts/article_20260506_三菱FCUA-CT100工业显示器M500_M520数控系统TFT替代.html",
    "./posts/article_20260506_三菱MDT962B工业液晶显示器CRT替代方案.html",
    "./posts/article_20260507_MDT1283B_LCD替换方案.html",
    "./posts/article_20260507_Mazak_CD1472D1M_LCD替换方案.html",
    "./posts/article_20260507_Sharp_AIQA8DSP40_LCD替换方案.html",
    "./posts/article_20260507_Siemens_6FC3998-7FA20_LCD.html",
    "./posts/article_20260507_Siemens_SM0901_579417_TA.html",
    "./posts/article_20260508_KTV104_非标订制工业显示器.html",
    "./posts/article_20260508_KTV148_非标订制工业显示器.html",
    "./posts/article_20260508_KTV800M_非标订制工业显示器.html",
    "./posts/article_20260508_KTV804_非标订制工业显示器.html",
    "./posts/article_20260509_GBS-8219_RGB转VGA工业信号转换器.html",
    "./posts/article_20260509_KT809_工业转换器.html",
    "./posts/article_20260509_KT819_工业转换器.html",
    "./posts/faq_20260501_数控机床显示器更换常见问题TOP10.html",
    "./posts/social_20260501_数控显示器升级市场动态与产品速递.html",
    "./posts/非标订制显示器系列.html",
]


def fix_title_tag(filepath):
    """修复单个HTML文件中的未闭合title标签"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  读取失败: {e}")
        return False

    original = content

    # 查找未闭合的title标签模式
    # 模式: <title>...内容...\n (没有</title>)
    pattern = r'(<title>[^<]+)(\s*\n)'

    def replace_title(match):
        title_content = match.group(1)
        newline = match.group(2)
        # 在title内容后面添加</title>
        return title_content + '</title>' + newline

    new_content = re.sub(pattern, replace_title, content, count=1)

    if new_content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"  写入失败: {e}")
            return False
    return False


def main():
    fixed_count = 0
    for filepath in FILES:
        if os.path.isfile(filepath):
            print(f"修复: {filepath}")
            if fix_title_tag(filepath):
                print("  ✓ 已修复title标签")
                fixed_count += 1
            else:
                print("  - 无需修复或已跳过")
        else:
            print(f"文件不存在: {filepath}")

    print(f"\n处理完成: {fixed_count} 个文件已修复")


if __name__ == "__main__":
    main()
