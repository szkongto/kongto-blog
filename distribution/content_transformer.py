#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KONGTO Blog Content Distribution System
自动化内容分发系统 - 将博客文章转换为各平台格式
"""

import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import html2text
import json

class ContentTransformer:
    """内容转换器 - 将博客HTML转换为各平台格式"""
    
    def __init__(self, blog_path="D:/workspace/kongto-blog"):
        self.blog_path = blog_path
        self.distribution_path = os.path.join(blog_path, "distribution")
        
    def read_html_article(self, html_file):
        """读取HTML文章并提取主要内容"""
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # 提取标题
        title = soup.find('h1').get_text() if soup.find('h1') else ""
        
        # 提取作者
        author = ""
        author_tag = soup.find('span', class_='author')
        if author_tag:
            author = author_tag.get_text().replace('作者:', '').strip()
        
        # 提取日期
        date = ""
        time_tag = soup.find('time')
        if time_tag:
            date = time_tag.get('datetime', '')
        
        # 提取正文内容
        content_div = soup.find('div', class_='content')
        content_html = str(content_div) if content_div else ""
        
        # 转换为Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # 不自动换行
        content_md = h.handle(content_html)
        
        return {
            'title': title,
            'author': author,
            'date': date,
            'content_html': content_html,
            'content_md': content_md,
            'url': soup.find('meta', property='og:url')['content'] if soup.find('meta', property='og:url') else ""
        }
    
    def convert_to_zhihu_qa(self, article):
        """转换为知乎问答格式"""
        # 生成问题标题（从文章标题衍生）
        title = article['title'].strip()
        
        # 创建问题 - 基于文章主题生成问句
        question_templates = [
            f"{title.replace('指南', '该怎么做？').replace('攻略', '有什么好的方法？')}",
            f"如何解决{title.split('：')[0] if '：' in title else title.split('-')[0]}的问题？",
            f"{title}的最佳实践是什么？"
        ]
        question = question_templates[0]
        
        # 生成回答内容
        answer = f"""
# {article['title']}

> 本文首发于[深圳市江图科技有限公司博客]({article['url']})，转载请注明出处。

## 问题背景

{self._extract_intro(article['content_md'])}

## 详细解答

{self._convert_md_for_zhihu(article['content_md'])}

## 总结

以上是关于{article['title']}的详细解答。如有疑问，欢迎在评论区交流。

---
**作者**：{article['author']}  
**发布时间**：{article['date']}  
**来源**：[KONGTO工业视频显示解决方案](https://szkongto.github.io/kongto-blog/)
"""
        
        return {
            'platform': 'zhihu',
            'question': question,
            'answer': answer,
            'tags': self._extract_tags(article['content_md'])
        }
    
    def convert_to_csdn(self, article):
        """转换为CSDN博客格式"""
        content = f"""
---
title: {article['title']}
date: {article['date']}
tags: 工业显示器,信号转换器,CNC数控,江图科技
categories: 工业自动化
---

# {article['title']}

> 本文首发于[深圳市江图科技有限公司博客]({article['url']})，转载请注明出处。

{self._convert_md_for_csdn(article['content_md'])}

---
**版权声明**：本文为原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。

**原文链接**：{article['url']}
"""
        
        return {
            'platform': 'csdn',
            'title': article['title'],
            'content': content,
            'tags': ['工业显示器', '信号转换器', 'CNC数控', '江图科技']
        }
    
    def convert_to_jianshu(self, article):
        """转换为简书格式"""
        content = f"""
# {article['title']}

> 本文首发于[深圳市江图科技有限公司博客]({article['url']})

{self._convert_md_for_jianshu(article['content_md'])}

---
*本文为原创内容，如需转载请联系作者。*

**查看原文**：{article['url']}
"""
        
        return {
            'platform': 'jianshu',
            'title': article['title'],
            'content': content,
            'tags': ['工业自动化', '数控机床', '显示器改造', '技术分享']
        }
    
    def convert_to_industrial_forum(self, article):
        """转换为工业论坛格式"""
        content = f"""
【问题描述】
{self._extract_intro(article['content_md'])}

【解决方案】
{self._convert_md_for_forum(article['content_md'])}

【效果展示】
根据多个实际案例，该方案已成功应用于：
- CNC数控机床改造
- 工业控制系统升级
- 老旧设备兼容性改造

【联系方式】
如需了解更多技术细节或获取报价，请联系：
电话：13686889647
邮箱：1251701967@qq.com

---
本文来源于 KONGTO 技术团队实战经验总结
"""
        
        return {
            'platform': 'industrial_forum',
            'title': f"【实战分享】{article['title']}",
            'content': content,
            'tags': ['技术分享', '实战案例', '设备改造']
        }
    
    def _extract_intro(self, md_content):
        """提取文章简介"""
        lines = md_content.split('\n')
        intro_lines = []
        for line in lines[:20]:
            if line.strip() and not line.startswith('#') and not line.startswith('>'):
                intro_lines.append(line)
                if len(intro_lines) >= 3:
                    break
        return '\n'.join(intro_lines) if intro_lines else "本文详细介绍相关技术实施方案。"
    
    def _convert_md_for_zhihu(self, md_content):
        """为知乎优化Markdown格式"""
        # 移除过于营销的内容
        md = re.sub(r'【.*?】', '', md_content)
        md = re.sub(r'（.*?报价.*?）', '', md)
        return md
    
    def _convert_md_for_csdn(self, md_content):
        """为CSDN优化格式"""
        # CSDN支持HTML，保留更多格式
        return md_content
    
    def _convert_md_for_jianshu(self, md_content):
        """为简书优化格式"""
        # 简书喜欢更简洁的风格
        md = md_content.replace('| ', '|')
        md = md.replace(' |', '|')
        return md
    
    def _convert_md_for_forum(self, md_content):
        """为论坛优化格式"""
        # 论坛需要更口语化
        md = md_content
        return md
    
    def _extract_tags(self, md_content):
        """提取关键词作为标签"""
        tags = ['工业显示器', '信号转换器', 'CNC', '数控机床']
        if 'CGA' in md_content or 'EGA' in md_content:
            tags.append('CGA/EGA改造')
        if 'RGB' in md_content:
            tags.append('RGBHV')
        return tags
    
    def save_transformed_content(self, transformed, output_dir):
        """保存转换后的内容"""
        os.makedirs(output_dir, exist_ok=True)
        
        platform = transformed['platform']
        
        if platform == 'zhihu':
            # 保存问题和回答
            question_file = os.path.join(output_dir, 'zhihu_question.md')
            answer_file = os.path.join(output_dir, 'zhihu_answer.md')
            
            with open(question_file, 'w', encoding='utf-8') as f:
                f.write(f"# {transformed['question']}\n\n")
                f.write(f"标签：{', '.join(transformed['tags'])}\n")
            
            with open(answer_file, 'w', encoding='utf-8') as f:
                f.write(transformed['answer'])
            
            return [question_file, answer_file]
        
        else:
            # 其他平台保存为单个文件
            filename = f"{platform}_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if platform == 'csdn':
                    f.write(f"# {transformed['title']}\n\n")
                    f.write(transformed['content'])
                elif platform == 'jianshu':
                    f.write(transformed['content'])
                elif platform == 'industrial_forum':
                    f.write(f"# {transformed['title']}\n\n")
                    f.write(transformed['content'])
            
            return [filepath]
    
    def batch_process(self, posts_dir, platforms=['zhihu', 'csdn', 'jianshu', 'industrial_forum']):
        """批量处理文章"""
        results = []
        
        # 获取所有HTML文章
        html_files = [f for f in os.listdir(posts_dir) if f.endswith('.html')]
        
        for html_file in html_files[:3]:  # 先处理前3篇测试
            print(f"处理文章: {html_file}")
            
            try:
                # 读取文章
                article_path = os.path.join(posts_dir, html_file)
                article = self.read_html_article(article_path)
                
                # 为每个平台转换
                for platform in platforms:
                    output_dir = os.path.join(self.distribution_path, platform)
                    
                    if platform == 'zhihu':
                        transformed = self.convert_to_zhihu_qa(article)
                    elif platform == 'csdn':
                        transformed = self.convert_to_csdn(article)
                    elif platform == 'jianshu':
                        transformed = self.convert_to_jianshu(article)
                    elif platform == 'industrial_forum':
                        transformed = self.convert_to_industrial_forum(article)
                    else:
                        continue
                    
                    # 保存
                    saved_files = self.save_transformed_content(transformed, output_dir)
                    results.append({
                        'article': html_file,
                        'platform': platform,
                        'files': saved_files
                    })
                    
                    print(f"  ✓ 已生成 {platform} 格式: {saved_files}")
            
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
        
        return results


def main():
    """主函数 - 测试内容转换系统"""
    print("=" * 60)
    print("KONGTO 博客内容自动分发系统")
    print("=" * 60)
    
    transformer = ContentTransformer()
    
    # 测试：转换中文文章
    posts_dir = "D:/workspace/kongto-blog/posts"
    
    print("\n开始批量转换文章...")
    results = transformer.batch_process(posts_dir)
    
    print("\n" + "=" * 60)
    print(f"转换完成！共处理 {len(results)} 个文章-平台组合")
    print("=" * 60)
    
    # 保存转换报告
    report_file = os.path.join(transformer.distribution_path, 'transformation_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n转换报告已保存至: {report_file}")


if __name__ == '__main__':
    main()
