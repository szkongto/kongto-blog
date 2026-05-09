#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理所有文章 - KONGTO内容分发系统
"""

import sys
import os
sys.path.append('D:/workspace/kongto-blog/distribution')

from content_distributor import ContentDistributor
from datetime import datetime
import json

def main():
    print("=" * 70)
    print("  KONGTO 批量内容分发 - 处理所有文章")
    print("=" * 70)
    
    distributor = ContentDistributor()
    
    # 获取文章总数
    posts_dir = os.path.join(distributor.blog_path, "posts")
    total_articles = len([f for f in os.listdir(posts_dir) if f.endswith('.html')])
    
    print(f"\n📊 检测到 {total_articles} 篇文章")
    print(f"⏳ 预计处理时间：{total_articles * 2} 秒")
    print("\n" + "-" * 70)
    print("开始处理...")
    print("-" * 70)
    
    # 批量处理所有文章（max_articles=None 表示全部）
    results = distributor.process_articles(max_articles=None)
    
    # 统计结果
    success_count = len([r for r in results if 'files' in r])
    failed_articles = [r for r in results if 'error' in r]
    
    # 生成详细报告
    print("\n" + "=" * 70)
    print("  处理完成！")
    print("=" * 70)
    
    print(f"\n📊 统计信息：")
    print(f"  - 文章总数：{total_articles}")
    print(f"  - 成功处理：{len(set([r['article'] for r in results if 'files' in r]))} 篇")
    print(f"  - 生成内容包：{len(results)} 个")
    print(f"  - 处理失败：{len(failed_articles)} 篇")
    
    # 保存详细报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_articles': total_articles,
        'successful': len(set([r['article'] for r in results if 'files' in r])),
        'total_content_packages': len(results),
        'failed': len(failed_articles),
        'failed_articles': failed_articles,
        'results': results
    }
    
    report_file = os.path.join(distributor.output_base, '批量处理报告.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 输出目录：")
    print(f"  {distributor.output_base}")
    
    print(f"\n📝 详细报告已保存：")
    print(f"  {report_file}")
    
    print(f"\n📋 下一步：")
    print(f"  1. 打开输出目录查看生成的内容")
    print(f"  2. 按照「发布清单.md」逐平台发布")
    print(f"  3. 建议先测试2-3篇，确认质量后再批量发布")
    print()
    
    # 显示生成的文件列表
    print("=" * 70)
    print("  生成的文件列表：")
    print("=" * 70)
    
    for platform in ['知乎', 'CSDN', '简书', '贴吧']:
        platform_dir = os.path.join(distributor.output_base, platform)
        if os.path.exists(platform_dir):
            files = os.listdir(platform_dir)
            print(f"\n📂 {platform} ({len(files)} 个文件):")
            for f in files[:3]:  # 只显示前3个
                print(f"  - {f}")
            if len(files) > 3:
                print(f"  ... 还有 {len(files) - 3} 个文件")

if __name__ == '__main__':
    main()
