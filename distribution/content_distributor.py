#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KONGTO 内容分发助手 - 实用版
功能：生成各平台格式的内容 + 发布清单 + 操作指南
"""

import os
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import html2text

class ContentDistributor:
    """内容分发助手 - 生成可直接使用的内容"""
    
    def __init__(self, blog_path="D:/workspace/kongto-blog"):
        self.blog_path = blog_path
        self.output_base = os.path.join(blog_path, "distribution_output")
        
    def read_article(self, html_file):
        """读取博客文章"""
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        content_div = soup.find('div', class_='content')
        content_md = ""
        if content_div:
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.body_width = 0
            content_md = h.handle(str(content_div))
        
        return {
            'title': soup.find('h1').get_text().strip() if soup.find('h1') else "",
            'content': content_md,
            'url': soup.find('meta', property='og:url')['content'] if soup.find('meta', property='og:url') else "",
            'description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else ""
        }
    
    def generate_zhihu_content(self, article):
        """生成知乎格式内容"""
        # 智能生成问题
        title = article['title']
        if '指南' in title:
            question = f"{title.replace('指南', '')}该怎么做？有哪些实战经验？"
        elif '应用' in title:
            question = f"{title}的实际效果如何？有什么成功案例？"
        else:
            question = f"关于{title}，有哪些需要了解的知识点？"
        
        answer = f"""# {article['title']}

> 本文首发于 [KONGTO技术博客]({article['url']})，转载请注明出处。

## 问题背景

{article['description']}

## 详细解答

{article['content'][:3000]}...

[阅读全文]({article['url']})

## 总结

以上是关于**{title}**的详细解答。如果你在实施过程中遇到问题，欢迎交流讨论。

---
*本文由工业自动化领域从业者分享，仅供参考。*
"""
        
        return {
            'platform': '知乎',
            'question': question,
            'answer': answer,
            'publish_tips': [
                '在知乎搜索相关问题，选择高流量问题回答',
                '或自己提问后自问自答（需注意社区规范）',
                '回答时不要过度营销，提供有价值的内容',
                '在个人简介中留下博客链接'
            ]
        }
    
    def generate_tieba_content(self, article):
        """生成贴吧格式内容"""
        content = f"""【标题】{article['title']} - 技术分享

【正文】
各位吧友好，分享一个关于{article['title']}的实战经验。

{article['description']}

详细内容（含图表）：{article['url']}

---
💡 适用场景：
- CNC数控机床改造
- 工业显示器升级
- 设备兼容性改造

📞 有类似问题的可以交流讨论
"""
        
        return {
            'platform': '百度贴吧',
            'target_bars': ['机床吧', '数控吧', '工业显示器吧'],
            'content': content,
            'publish_tips': [
                '每个贴吧单独发帖，不要跨吧刷屏',
                '以技术分享的口吻，不要硬广',
                '可以回复相关帖子，自然地提及你的解决方案',
                '注意贴吧规则，避免被删帖'
            ]
        }
    
    def generate_csdn_content(self, article):
        """生成CSDN格式内容"""
        content = f"""---
title: {article['title']}
date: {datetime.now().strftime('%Y-%m-%d')}
tags: 工业显示器,信号转换器,CNC数控,江图科技
categories: 工业自动化
---

# {article['title']}

> 本文首发于 [KONGTO技术博客]({article['url']})，转载请注明出处。

{article['content']}

---
**版权声明**：本文为原创文章，遵循 CC 4.0 BY-SA 版权协议。

**原文链接**：{article['url']}
"""
        
        return {
            'platform': 'CSDN',
            'title': article['title'],
            'content': content,
            'publish_tips': [
                '登录CSDN后台，新建文章',
                '复制上述内容粘贴即可',
                '选择合适的分类和标签',
                '发布前预览检查格式'
            ]
        }
    
    def generate_jianshu_content(self, article):
        """生成简书格式内容"""
        content = f"""# {article['title']}

> 本文首发于 [KONGTO技术博客]({article['url']})

{article['content'][:5000]}

---

*本文为原创内容，转载请注明出处。*

**查看完整版**：{article['url']}
"""
        
        return {
            'platform': '简书',
            'title': article['title'],
            'content': content,
            'publish_tips': [
                '简书对新人有一定限制，先养号几天',
                '内容要原创，不要直接复制粘贴',
                '可以添加个人简介和公众号信息'
            ]
        }
    
    def save_content(self, data, platform, article_title):
        """保存生成的内容"""
        safe_title = re.sub(r'[\\/*?:"<>|]', '', article_title)[:30]
        platform_dir = os.path.join(self.output_base, platform)
        os.makedirs(platform_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if platform == '知乎':
            # 保存问题和回答
            q_file = os.path.join(platform_dir, f'问题_{safe_title}_{timestamp}.txt')
            a_file = os.path.join(platform_dir, f'回答_{safe_title}_{timestamp}.txt')
            
            with open(q_file, 'w', encoding='utf-8') as f:
                f.write(f"问题：{data['question']}\n\n")
                f.write("发布建议：\n")
                for tip in data['publish_tips']:
                    f.write(f"- {tip}\n")
            
            with open(a_file, 'w', encoding='utf-8') as f:
                f.write(data['answer'])
            
            return [q_file, a_file]
        
        else:
            filename = f'{safe_title}_{timestamp}.md'
            filepath = os.path.join(platform_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {platform} - 发布内容\n\n")
                f.write(f"## 标题\n{data['title']}\n\n" if data.get('title') else "")
                f.write(f"## 内容\n{data['content']}\n\n")
                f.write("## 发布建议\n")
                for tip in data.get('publish_tips', []):
                    f.write(f"- {tip}\n")
            
            return [filepath]
    
    def process_articles(self, max_articles=None):
        """处理文章并生成各平台内容
        Args:
            max_articles: 最大处理数量，None表示处理所有文章
        """
        posts_dir = os.path.join(self.blog_path, "posts")
        html_files = [f for f in os.listdir(posts_dir) if f.endswith('.html')]
        
        if max_articles:
            html_files = html_files[:max_articles]
        
        total = len(html_files)
        print(f"\n📝 开始处理 {total} 篇文章...\n")
        
        all_results = []
        
        for idx, html_file in enumerate(html_files, 1):
            print(f"[{idx}/{len(html_files)}] 处理: {html_file}")
            
            try:
                article = self.read_article(os.path.join(posts_dir, html_file))
                print(f"  ✓ 已读取: {article['title'][:40]}...")
                
                # 为每个平台生成内容
                platforms_data = [
                    ('知乎', self.generate_zhihu_content(article)),
                    ('贴吧', self.generate_tieba_content(article)),
                    ('CSDN', self.generate_csdn_content(article)),
                    ('简书', self.generate_jianshu_content(article))
                ]
                
                for platform_name, data in platforms_data:
                    saved_files = self.save_content(data, platform_name, article['title'])
                    print(f"    ✓ {platform_name}: 已生成 {len(saved_files)} 个文件")
                    
                    all_results.append({
                        'article': article['title'],
                        'platform': platform_name,
                        'files': saved_files
                    })
                
                print()
                
            except Exception as e:
                print(f"  ✗ 错误: {e}\n")
        
        return all_results
    
    def create_publish_checklist(self):
        """创建发布清单"""
        checklist = f"""# KONGTO 内容发布清单

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 发布前检查

- [ ] 内容已修改为适合平台风格
- [ ] 标题已优化（包含关键词）
- [ ] 图片已下载或替换为图床链接
- [ ] 联系方式/链接已按要求放置
- [ ] 已阅读平台社区规范

## 🎯 推荐发布顺序

1. **CSDN** - 专业技术社区，最适合首发
2. **知乎** - 搜索相关问题回答，或自问自答
3. **简书** - 内容创作平台
4. **百度贴吧** - 谨慎发布，避免被删

## ⚠️ 注意事项

### 知乎
- 不要过度营销，提供有价值内容
- 在个人简介留链接
- 回答老问题也可能有流量

### 百度贴吧
- 每个贴吧单独发，不要刷屏
- 以技术交流口吻
- 可以回复相关帖子

### CSDN/简书
- 直接复制生成的内容
- 选择合适的分类标签
- 发布前预览

## 📊 效果追踪

建议记录：
- 发布日期
- 平台
- 浏览量/点赞数
- 带来的询盘数

---

**下一步**：打开各平台文件夹，按照内容逐条发布。
"""
        
        checklist_file = os.path.join(self.output_base, '发布清单.md')
        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        return checklist_file


def main():
    print("=" * 70)
    print("  KONGTO 内容分发助手 - 实用版")
    print("=" * 70)
    
    distributor = ContentDistributor()
    
    # 1. 生成各平台内容
    print("\n【第一步】生成各平台格式的内容")
    print("-" * 70)
    results = distributor.process_articles(max_articles=3)
    
    # 2. 创建发布清单
    print("\n【第二步】创建发布清单和操作指南")
    print("-" * 70)
    checklist = distributor.create_publish_checklist()
    print(f"✓ 已生成: {checklist}")
    
    # 3. 统计
    print("\n" + "=" * 70)
    print("  完成！")
    print("=" * 70)
    print(f"\n📊 统计：")
    print(f"  - 处理文章数：{len(set([r['article'] for r in results]))}")
    print(f"  - 生成内容包：{len(results)} 个")
    print(f"\n📁 输出目录：")
    print(f"  {distributor.output_base}")
    print(f"\n📝 下一步：")
    print(f"  1. 打开输出目录查看生成的内容")
    print(f"  2. 按照「发布清单.md」逐平台发布")
    print(f"  3. 测试几篇后，可以批量处理剩余文章")
    print()


if __name__ == '__main__':
    main()
