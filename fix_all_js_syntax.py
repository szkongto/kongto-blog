#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量修复HTML文件中多行innerHTML导致的JS语法错误"""

import os
import re

# 定义问题文件列表
FILES = [
    "./posts/article_20260501_CGA_EGA显示器改造为RGBHV工业显示器实战指南.html",
    "./posts/article_20260501_FANUC_A61L_0001_0093_LCD液晶显示器_让老旧CNC数控系统焕发新活力.html",
    "./posts/article_20260501_FANUC数控显示器CRT升级LCD完整指南.html",
    "./posts/article_20260501_如何将FANUC_CRT显示器改装为LCD_深圳市江图科技有限公司实战案例.html",
    "./posts/article_20260501_工业数控设备显示器故障诊断与维修全攻略.html",
    "./posts/article_20260501_工业显示器RGBHV改造全攻略_从CGA_EGA到高清显示.html",
    "./posts/article_20260501_工业视频信号转换器在CNC数控系统中的应用.html",
    "./posts/article_20260501_工业视频信号转换器系列_CGA_EGA转VGA_RGB转VGA解决方案.html",
    "./posts/article_20260501_工业视频显示在智能工厂中的关键角色与江图科技方案.html",
    "./posts/article_20260501_工业触摸屏与工控显示器的区别及选型建议.html",
    "./posts/article_20260501_江图科技工业视频显示产品目录_LCD显示器_转换器_触摸屏.html",
    "./posts/article_20260503_FANUC_A61L_0001_0074_LCD.html",
    "./posts/article_20260503_FANUC_A61L_0001_0086_LCD.html",
    "./posts/article_20260503_FANUC_A61L_0001_0090_LCD.html",
    "./posts/article_20260503_FANUC_A61L_0001_0092_LCD.html",
    "./posts/article_20260503_FANUC_A61L_0001_0093_LCD.html",
    "./posts/article_20260503_FANUC_A61L_0001_0094_LCD.html",
    "./posts/article_20260503_FANUC_A61L_0001_0095_LCD.html",
    "./posts/article_20260503_FANUC_D9MM_11A_0093_LCD.html",
    "./posts/article_20260506_三菱BM09DF工业显示屏E60数控系统TFT替代.html",
    "./posts/article_20260506_三菱FCUA-CT100工业显示器M500_M520数控系统TFT替代.html",
    "./posts/article_20260506_三菱MDT962B工业液晶显示器CRT替代方案.html",
    "./posts/article_20260507_Mazak_CD1472D1M_LCD替换方案.html",
    "./posts/article_20260507_MDT1283B_LCD替换方案.html",
    "./posts/article_20260507_Sharp_AIQA8DSP40_LCD替换方案.html",
    "./posts/article_20260507_Siemens_6FC3998-7FA20_LCD.html",
    "./posts/article_20260507_Siemens_SM0901_579417_TA.html",
    "./posts/article_20260508_Haas_CRT_LCD_Case.html",
    "./posts/article_20260508_KTV104_非标订制工业显示器.html",
    "./posts/article_20260508_KTV148_非标订制工业显示器.html",
    "./posts/article_20260508_KTV800M_非标订制工业显示器.html",
    "./posts/article_20260508_KTV804_非标订制工业显示器.html",
    "./posts/article_20260508_Mazak_C5470NS_CRT_LCD_Case.html",
    "./posts/article_20260508_Okuma_5000_5020_CRT_LCD.html",
    "./posts/article_20260509_GBS-8219_RGB转VGA工业信号转换器.html",
    "./posts/article_20260509_KT809_工业转换器.html",
    "./posts/article_20260509_KT819_工业转换器.html",
    "./posts/comparison_20260501_FANUC_CRT显示器维修_vs_LCD升级模块成本对比.html",
    "./posts/comparison_20260501_工业视频信号转换器选购指南_VGA转VIDEO_vs_HDMI转VGA.html",
    "./posts/faq_20260501_FANUC_0i系统显示器常见问题与解决方案.html",
    "./posts/faq_20260501_FANUC_A61L_0001_0093显示器常见故障及解决方案.html",
    "./posts/faq_20260501_数控机床显示器更换常见问题TOP10.html",
    "./posts/press_release_20260501_江图科技推出FANUC数控显示器LCD升级解决方案.html",
    "./posts/social_20260501_数控显示器升级市场动态与产品速递.html",
    "./posts/非标订制显示器系列.html",
    "./posts/index.html",
    "./index.html",
    "./about.html",
]


def fix_html_file(filepath):
    """修复单个HTML文件中的多行innerHTML问题"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  读取失败: {e}")
        return False

    original = content

    # 修复模式: modal.innerHTML = '<div class="wechat-modal-content">
    # <h3...>...</h3><img.../><p>...</p>
    # <button...>...</button></div>';

    # 目标格式: modal.innerHTML = '<div class="wechat-modal-content"><h3...>...</h3>...';

    # 1. 合并 <div class="wechat-modal-content"> 和 <h3 之间的换行
    content = re.sub(
        r"(modal\.innerHTML\s*=\s*'<div class=\"wechat-modal-content\">)\s*\n\s*(<h3)",
        r"\1\2",
        content
    )

    # 2. 合并 </h3> 和 <img 之间的换行
    content = re.sub(
        r"(</h3>)\s*\n\s*(<img)",
        r"\1\2",
        content
    )

    # 3. 合并 /> 和 <p 之间的换行
    content = re.sub(
        r'(alt="QR Code">)\s*\n\s*(<p)',
        r"\1\2",
        content
    )

    # 4. 合并 </p> 和 <button 之间的换行
    content = re.sub(
        r"(</p>)\s*\n\s*(<button)",
        r"\1\2",
        content
    )

    # 5. 合并 </button> 和 </div>'; 之间的换行
    content = re.sub(
        r'(关闭</button>)\s*\n\s*(</div>)',
        r"\1 \2",
        content
    )

    # 6. 移除多余的id属性（英文版本没有id）
    content = re.sub(
        r'<h3 id="微信扫码分享">',
        '<h3>',
        content
    )

    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
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
            if fix_html_file(filepath):
                print("  ✓ 已修复")
                fixed_count += 1
            else:
                print("  - 无需修复或已跳过")
        else:
            print(f"文件不存在: {filepath}")

    print(f"\n处理完成: {fixed_count} 个文件已修复")


if __name__ == "__main__":
    main()
