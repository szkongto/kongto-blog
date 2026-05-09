#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KONGTO Blog Content Distribution System v2.0
自动化内容分发系统 - 改进版
支持：知乎、CSDN、简书、工业论坛
"""

import os
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
import html2text

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
        title_tag = soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else ""
        
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
        
        # 提取正文内容 - 改进：保留HTML结构
        content_div = soup.find('div', class_='content')
        
        if content_div:
            # 改进表格格式化
            self._fix_tables(content_div)
            content_html = str(content_div)
            
            # 转换为Markdown - 改进配置
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0
            h.ignore_emphasis = False
            h.inline_links = True
            content_md = h.handle(content_html)
        else:
            content_html = ""
            content_md = ""
        
        # 提取描述
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else ""
        
        return {
            'title': title,
            'author': author,
            'date': date,
            'description': description,
            'content_html': content_html,
            'content_md': content_md,
            'url': soup.find('meta', property='og:url')['content'] if soup.find('meta', property='og:url') else "",
            'keywords': soup.find('meta', attrs={'name': 'keywords'})['content'] if soup.find('meta', attrs={'name': 'keywords'}) else ""
        }
    
    def _fix_tables(self, soup_obj):
        """修复HTML表格格式，使其更好转换为Markdown"""
        for table in soup_obj.find_all('table'):
            # 确保表格有正确的结构
            if not table.find('thead') and table.find('tr'):
                first_row = table.find('tr')
                thead = soup_obj.new_tag('thead')
                thead.append(first_row.extract())
                table.insert(0, thead)
            
            # 添加tbody如果不存在
            if not table.find('tbody'):
                tbody = soup_obj.new_tag('tbody')
                for tr in table.find_all('tr'):
                    tbody.append(tr.extract())
                table.append(tbody)
    
    def convert_to_zhihu_qa(self, article):
        """转换为知乎问答格式 - 改进版"""
        title = article['title'].strip()
        
        # 智能生成问题标题
        question = self._generate_zhihu_question(title)
        
        # 生成回答内容 - 改进结构
        answer = f"""# {title}

> 本文首发于 [KONGTO技术博客]({article['url']})，转载请注明出处。

## 问题背景

{self._extract_intro(article)}

## 详细解答

{self._clean_content_for_zhihu(article['content_md'])}

## 实战案例

{self._extract_case_studies(article['content_md'])}

## 总结

以上就是关于**{title}**的详细解答。如果你在实施过程中遇到问题，欢迎在评论区交流讨论。

---
**作者**：{article['author']}  
**发布时间**：{article['date']}  
**原文链接**：{article['url']}
"""
        
        return {
            'platform': 'zhihu',
            'question': question,
            'answer': answer,
            'tags': self._extract_tags(article)
        }
    
    def _generate_zhihu_question(self, title):
        """智能生成知乎问题标题"""
        # 移除末尾的空格和标点
        title = title.strip().rstrip(' 　、，。')
        
        # 根据标题类型生成问题
        if '指南' in title or '攻略' in title:
            return f"{title}该怎么做？有什么注意事项？"
        elif '应用' in title:
            return f"{title}的实际效果如何？有哪些成功案例？"
        elif '区别' in title or '对比' in title:
            return f"{title}？该如何选择？"
        elif '如何解决' in title or '方案' in title:
            return f"{title}？最佳实践是什么？"
        else:
            return f"关于{title}，有哪些需要了解的知识点？"
    
    def _extract_intro(self, article):
        """提取文章简介 - 改进版"""
        content = article['content_md'] if isinstance(article, dict) else article
        
        # 查找第一个段落
        lines = content.split('\n')
        intro = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('>') and not line.startswith('|'):
                intro.append(line)
                if len(intro) >= 2:
                    break
        
        if intro:
            return '\n'.join(intro)
        
        # 如果没有找到，使用描述
        if isinstance(article, dict) and article.get('description'):
            return article['description']
        
        return "本文将详细介绍相关技术实施方案和最佳实践。"
    
    def _clean_content_for_zhihu(self, md_content):
        """为知乎清理和优化的Markdown内容"""
        # 移除营销性过强的内容
        content = re.sub(r'【.*?】', '', md_content)
        content = re.sub(r'（.*?联系方式.*?）', '', content)
        content = re.sub(r'电话：\d+', '', content)
        
        # 优化表格格式
        content = self._fix_markdown_tables(content)
        
        # 移除空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def _fix_markdown_tables(self, content):
        """修复Markdown表格格式"""
        lines = content.split('\n')
        fixed_lines = []
        in_table = False
        
        for i, line in enumerate(lines):
            # 检测表格行
            if '|' in line and line.strip().startswith('|'):
                if not in_table:
                    in_table = True
                    fixed_lines.append('')  # 表格前加空行
                fixed_lines.append(line)
            else:
                if in_table:
                    fixed_lines.append('')  # 表格后加空行
                    in_table = False
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _extract_case_studies(self, md_content):
        """提取案例研究部分"""
        lines = md_content.split('\n')
        case_lines = []
        in_case = False
        
        for line in lines:
            if '案例' in line or 'case' in line.lower():
                in_case = True
            if in_case:
                case_lines.append(line)
                if len(case_lines) >= 10:  # 最多取10行
                    break
        
        return '\n'.join(case_lines) if case_lines else "本文包含多个实际工业应用案例，效果显著。"
    
    def convert_to_csdn(self, article):
        """转换为CSDN博客格式"""
        content = f"""---
title: {article['title']}
date: {article['date']}
tags: {article['keywords'] if article['keywords'] else '工业显示器,信号转换器,CNC数控'}
categories: 工业自动化
---

# {article['title']}

> 本文首发于 [KONGTO技术博客]({article['url']})，转载请注明出处。

{self._clean_content_for_csdn(article['content_md'])}

---
**版权声明**：本文为博主原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。

**原文链接**：{article['url']}
"""
        
        return {
            'platform': 'csdn',
            'title': article['title'],
            'content': content,
            'tags': article['keywords'].split(',') if article['keywords'] else ['工业自动化', '数控机床']
        }
    
    def _clean_content_for_csdn(self, md_content):
        """为CSDN优化内容"""
        # CSDN支持HTML，可以保留更多格式
        content = md_content
        
        # 确保代码块格式正确
        content = re.sub(r'```\s*\n', '\n```\n', content)
        
        return content
    
    def convert_to_jianshu(self, article):
        """转换为简书格式"""
        content = f"""# {article['title']}

> 本文首发于 [KONGTO技术博客]({article['url']})

{self._clean_content_for_jianshu(article['content_md'])}

---
*本文为原创内容，如需转载请联系作者。*

**查看原文**：{article['url']}
"""
        
        return {
            'platform': 'jianshu',
            'title': article['title'],
            'content': content,
            'tags': ['工业自动化', '数控机床', '技术分享']
        }
    
    def _clean_content_for_jianshu(self, md_content):
        """为简书优化内容"""
        # 简书喜欢简洁风格
        content = re.sub(r'\n{3,}', '\n\n', md_content)
        return content.strip()
    
    def convert_to_industrial_forum(self, article):
        """转换为工业论坛格式"""
        content = f"""【问题描述】
{self._extract_intro(article)}

【技术背景】
{article['description'] if article.get('description') else '工业现场实际应用需求'}

【解决方案】
{self._clean_content_for_forum(article['content_md'])}

【应用效果】
根据多个实际案例，该方案已成功应用于：
- CNC数控机床改造
- 工业控制系统升级  
- 老旧设备兼容性改造

【联系方式】
如需了解更多技术细节或获取报价，请联系：
电话：13686889647
邮箱：1251701967@qq.com

---
*本文来源于 KONGTO 技术团队实战经验总结*
"""
        
        return {
            'platform': 'industrial_forum',
            'title': f"【实战分享】{article['title']}",
            'content': content,
            'tags': ['技术分享', '实战案例', '设备改造']
        }
    
    def _clean_content_for_forum(self, md_content):
        """为论坛优化内容"""
        # 论坛需要更口语化
        content = md_content
        return content
    
    def _extract_tags(self, article):
        """提取标签"""
        tags = ['工业显示器', '信号转换器', 'CNC', '数控机床']
        
        keywords = article.get('keywords', '')
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',')[:3]])
        
        content = article.get('content_md', '')
        if 'CGA' in content or 'EGA' in content:
            tags.append('CGA/EGA改造')
        if 'RGB' in content:
            tags.append('RGBHV')
        
        return list(set(tags))[:5]  # 最多5个标签
    
    def save_transformed_content(self, transformed, output_dir, article_title):
        """保存转换后的内容 - 改进版"""
        os.makedirs(output_dir, exist_ok=True)
        
        platform = transformed['platform']
        
        # 生成安全的文件名
        safe_title = re.sub(r'[\\/*?:"<>|]', '', article_title)[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if platform == 'zhihu':
            # 保存问题
            question_file = os.path.join(output_dir, f'zhihu_question_{timestamp}.md')
            with open(question_file, 'w', encoding='utf-8') as f:
                f.write(f"# {transformed['question']}\n\n")
                f.write(f"**标签**：{', '.join(transformed['tags'])}\n\n")
                f.write(f"**来源文章**：{article_title}\n")
            
            # 保存回答
            answer_file = os.path.join(output_dir, f'zhihu_answer_{timestamp}.md')
            with open(answer_file, 'w', encoding='utf-8') as f:
                f.write(transformed['answer'])
            
            return [question_file, answer_file]
        
        else:
            # 其他平台保存为单个文件
            filename = f"{platform}_{safe_title}_{timestamp}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if platform == 'csdn':
                    f.write(transformed['content'])
                elif platform == 'jianshu':
                    f.write(transformed['content'])
                elif platform == 'industrial_forum':
                    f.write(f"# {transformed['title']}\n\n")
                    f.write(transformed['content'])
            
            return [filepath]
    
    def batch_process(self, posts_dir, platforms=['zhihu', 'csdn', 'jianshu', 'industrial_forum'], max_articles=3):
        """批量处理文章 - 改进版"""
        results = []
        
        # 获取所有HTML文章
        html_files = [f for f in os.listdir(posts_dir) if f.endswith('.html')]
        
        print(f"\n找到 {len(html_files)} 篇文章，开始处理前 {max_articles} 篇...\n")
        
        for idx, html_file in enumerate(html_files[:max_articles], 1):
            print(f"[{idx}/{max_articles}] 处理文章: {html_file}")
            
            try:
                # 读取文章
                article_path = os.path.join(posts_dir, html_file)
                article = self.read_html_article(article_path)
                
                print(f"  ✓ 已读取：{article['title']}")
                
                # 为每个平台转换
                for platform in platforms:
                    output_dir = os.path.join(self.distribution_path, platform)
                    
                    print(f"  → 转换为 {platform} 格式...", end=' ')
                    
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
                    saved_files = self.save_transformed_content(transformed, output_dir, article['title'])
                    results.append({
                        'article': html_file,
                        'article_title': article['title'],
                        'platform': platform,
                        'files': saved_files,
                        'status': 'success'
                    })
                    
                    print(f"✓ 已保存 {len(saved_files)} 个文件")
                    
                print(f"  ✓ 文章处理完成\n")
                
            except Exception as e:
                print(f"  ✗ 处理失败: {e}\n")
                results.append({
                    'article': html_file,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results


def create_automation_workflow():
    """创建自动化工作流配置文件"""
    workflow = {
        'name': 'KONGTO Content Distribution Automation',
        'version': '2.0',
        'schedule': {
            'type': 'periodic',
            'cron': '0 10 * * *',  # 每天早上10点
            'description': '每天早上10点自动分发新文章'
        },
        'platforms': [
            {
                'name': 'zhihu',
                'enabled': True,
                'auto_post': False,  # 需要手动审核
                'content_format': 'qa'
            },
            {
                'name': 'csdn',
                'enabled': True,
                'auto_post': False,
                'content_format': 'blog'
            },
            {
                'name': 'jianshu',
                'enabled': True,
                'auto_post': False,
                'content_format': 'blog'
            },
            {
                'name': 'industrial_forum',
                'enabled': True,
                'auto_post': False,
                'content_format': 'forum'
            }
        ],
        'notification': {
            'email': '1251701967@qq.com',
            'notify_on_complete': True
        }
    }
    
    config_path = 'D:/workspace/kongto-blog/distribution/automation_config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    
    return config_path


def main():
    """主函数"""
    print("=" * 70)
    print("  KONGTO 博客内容自动分发系统 v2.0")
    print("=" * 70)
    
    transformer = ContentTransformer()
    
    # 1. 测试转换（前3篇文章）
    print("\n【第一步】测试内容转换功能")
    print("-" * 70)
    posts_dir = "D:/workspace/kongto-blog/posts"
    results = transformer.batch_process(posts_dir, max_articles=3)
    
    # 2. 创建自动化配置
    print("\n【第二步】创建自动化工作流配置")
    print("-" * 70)
    config_file = create_automation_workflow()
    print(f"✓ 配置文件已保存: {config_file}")
    
    # 3. 生成报告
    print("\n【第三步】生成转换报告")
    print("-" * 70)
    report_file = os.path.join(transformer.distribution_path, 'transformation_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_processed': len([r for r in results if r['status'] == 'success']),
            'total_failed': len([r for r in results if r['status'] == 'failed']),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 报告已保存: {report_file}")
    
    # 4. 总结
    print("\n" + "=" * 70)
    print("  处理完成！")
    print("=" * 70)
    print(f"\n📊 统计信息：")
    print(f"  - 成功处理：{len([r for r in results if r['status'] == 'success'])} 个")
    print(f"  - 处理失败：{len([r for r in results if r['status'] == 'failed'])} 个")
    print(f"\n📁 输出目录：")
    print(f"  {transformer.distribution_path}")
    print(f"\n🔧 下一步：")
    print(f"  1. 检查生成的文件内容")
    print(f"  2. 手动发布到各平台（或配置自动发布）")
    print(f"  3. 设置定时任务实现自动化")
    print()


if __name__ == '__main__':
    main()
