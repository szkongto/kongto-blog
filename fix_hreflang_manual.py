#!/usr/bin/env python3
"""
手动映射修复 - 处理无法自动匹配的情况
根据人工确认的映射关系修复hreflang
"""
import os
import re
from urllib.parse import quote, unquote

BASE_DIR = r"D:\workspace\kongto-blog"

# 手动确认的映射关系：(英文文件, 正确的中文文件)
MANUAL_MAPPING = {
    # CGA_EGA系列
    'CGA_EGA_to_RGBHV_Industrial_Display_Retrofit_Guide.html': 'article_20260501_CGA_EGA显示器改造为RGBHV工业显示器实战指南.html',
    'Industrial_RGBHV_Retrofit_Guide_CGA_EGA_to_HD.html': 'article_20260501_工业显示器RGBHV改造全攻略_从CGA_EGA到高清显示.html',
    'Industrial_RGBHV_Signal_Analysis_CGA_EGA_to_HD_Display.html': 'article_20260501_工业显示器RGBHV改造全攻略_从CGA_EGA到高清显示.html',

    # FANUC系列
    'FANUC_A61L_0001_0093_Display_Abnormality_Troubleshooting.html': 'faq_20260501_FANUC_A61L_0001_0093显示器常见故障及解决方案.html',
    'FANUC_A61L_0001_0093_Display_FAQ_Solutions.html': 'faq_20260501_FANUC_A61L_0001_0093显示器常见故障及解决方案.html',
    'FANUC_A61L_0001_0093_LCD_CNC_Upgrade_Replacement.html': 'article_20260501_FANUC_A61L_0001_0093_LCD液晶显示器_让老旧CNC数控系统焕发新活力.html',
    'FANUC_A61L_0001_0093_LCD_Display_Breathe_New_Life_CNC.html': 'article_20260501_FANUC_A61L_0001_0093_LCD液晶显示器_让老旧CNC数控系统焕发新活力.html',

    # FANUC CRT系列
    'FANUC_CRT_Maintenance_vs_LCD_Upgrade_Module_Comparison.html': 'comparison_20260501_FANUC_CRT显示器维修_vs_LCD升级模块成本对比.html',
    'FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html': 'article_20260501_FANUC数控显示器CRT升级LCD完整指南.html',
    'FANUC_CRT_to_LCD_Upgrade_Guide.html': 'article_20260501_FANUC数控显示器CRT升级LCD完整指南.html',
    'How_to_Retrofit_FANUC_CRT_to_LCD_Kongto_Case_Study.html': 'article_20260501_如何将FANUC_CRT显示器改装为LCD_深圳市江图科技有限公司实战案例.html',

    # 工业设备系列
    'Industrial_CNCDisplay_Troubleshooting_Repair_Guide.html': 'article_20260501_工业数控设备显示器故障诊断与维修全攻略.html',
    'Industrial_Controller_Display_Troubleshooting_Maintenance_Guide.html': 'article_20260501_工业数控设备显示器故障诊断与维修全攻略.html',
    'Industrial_Display_Market_Trends_Brand_Comparison.html': 'social_20260501_数控显示器升级市场动态与产品速递.html',
    'Industrial_Display_Procurement_Selection_Guide.html': 'article_20260501_工业触摸屏与工控显示器的区别及选型建议.html',
    'Industrial_Touchscreen_vs_Display_Difference_Selection.html': 'article_20260501_工业触摸屏与工控显示器的区别及选型建议.html',

    # 视频信号转换系列
    'Video_Signal_Converter_Series_CGA_EGA_to_VGA_Solution.html': 'article_20260501_工业视频信号转换器系列_CGA_EGA转VGA_RGB转VGA解决方案.html',
    'Video_Signal_Converter_Buying_Guide.html': 'comparison_20260501_工业视频信号转换器选购指南_VGA转VIDEO_vs_HDMI转VGA.html',
    'Video_Signal_Converter_Selection_Guide.html': 'comparison_20260501_工业视频信号转换器选购指南_VGA转VIDEO_vs_HDMI转VGA.html',
    'Video_Signal_Converters_in_CNC_Numerical_Control_Systems.html': 'article_20260501_工业视频信号转换器在CNC数控系统中的应用.html',
    'Video_Signal_Converters_in_CN_Control_Systems.html': 'article_20260501_工业视频信号转换器在CNC数控系统中的应用.html',
    'Video_Signal_Conversion_System_CGA_EGA_to_VGA_Manual.html': 'article_20260501_工业视频信号转换器系列_CGA_EGA转VGA_RGB转VGA解决方案.html',
    'Video_Signal_Conversion_System_CGA_EGA_to_VGA_Solution.html': 'article_20260501_工业视频信号转换器系列_CGA_EGA转VGA_RGB转VGA解决方案.html',

    # 产品目录
    'Kongto_Technology_Industrial_Video_Display_Product_Catalog.html': 'article_20260501_江图科技工业视频显示产品目录_LCD显示器_转换器_触摸屏.html',
    'Shenzhen_Zhongtu_Industrial_Video_Display_Catalog.html': 'article_20260501_江图科技工业视频显示产品目录_LCD显示器_转换器_触摸屏.html',

    # 新闻稿
    'Nanjing_Zhongjing_FANUC_LCD_Upgrade_Press_Release.html': 'press_release_20260501_江图科技推出FANUC数控显示器LCD升级解决方案.html',
    'Shenzhen_Zhongtu_FANUC_LCD_Retrofit_Press_Release.html': 'press_release_20260501_江图科技推出FANUC数控显示器LCD升级解决方案.html',

    # FAQ
    'FANUC_0i_System_Display_Abnormality_Troubleshooting.html': 'faq_20260501_FANUC_0i系统显示器常见问题与解决方案.html',
    'FANUC_0i_System_Display_FAQ_Solutions.html': 'faq_20260501_FANUC_0i系统显示器常见问题与解决方案.html',

    # 回收
    'Used_Display_Recycling_FAQ_TOP10.html': 'faq_20260501_数控机床显示器更换常见问题TOP10.html',
    'Used_Industrial_Display_Recycling_FAQ_TOP10.html': 'faq_20260501_数控机床显示器更换常见问题TOP10.html',

    # 智能工厂
    'Industrial_Video_Display_Color_Scanning_Technology.html': 'article_20260501_工业视频显示在智能工厂中的关键角色与江图科技方案.html',
    'Industrial_Video_Display_Smart_Factory_Kongto_Solution.html': 'article_20260501_工业视频显示在智能工厂中的关键角色与江图科技方案.html',
}

def fix_with_manual_mapping():
    """使用手动映射修复英文文件的hreflang"""
    fixed = 0
    not_found = 0

    for en_file, correct_zh in MANUAL_MAPPING.items():
        en_path = os.path.join(BASE_DIR, 'en', 'posts', en_file)
        zh_path = os.path.join(BASE_DIR, 'posts', correct_zh)

        # 检查文件是否存在
        if not os.path.exists(en_path):
            print(f"✗ 英文文件不存在: {en_file}")
            not_found += 1
            continue

        if not os.path.exists(zh_path):
            print(f"✗ 中文文件不存在: {correct_zh}")
            not_found += 1
            continue

        # 读取英文文件
        with open(en_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 构建新的hreflang标签
        new_zh_href = f'https://cncdisplay.com/posts/{quote(correct_zh, safe="")}'

        # 查找当前的hreflang="zh"标签
        zh_match = re.search(r'(<link[^>]*hreflang="zh"[^>]*href=")([^"]+)(")', content)
        if zh_match:
            old_href = zh_match.group(2)
            if old_href != new_zh_href:
                # 需要修复
                old_tag = zh_match.group(0)
                new_tag = zh_match.group(1) + new_zh_href + zh_match.group(3)
                content = content.replace(old_tag, new_tag)
                with open(en_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed += 1
                print(f"✓ 修复: {en_file[:50]}...")
                print(f"  -> {correct_zh[:50]}...")
            else:
                print(f"○ 已是正确: {en_file[:50]}...")
        else:
            # 没有hreflang="zh"标签，添加一个
            # 在</head>前添加
            zh_tag = f'<link rel="alternate" hreflang="zh" href="{new_zh_href}" />\n'
            content = content.replace('</head>', zh_tag + '</head>')
            with open(en_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed += 1
            print(f"+ 添加: {en_file[:50]}...")
            print(f"  -> {correct_zh[:50]}...")

    return fixed, not_found

def main():
    print("=" * 60)
    print("使用手动映射修复 hreflang...")
    print("=" * 60)

    fixed, not_found = fix_with_manual_mapping()

    print("\n" + "=" * 60)
    print(f"修复完成: 修复 {fixed} 个, 未找到 {not_found} 个")
    print("=" * 60)

if __name__ == "__main__":
    main()
