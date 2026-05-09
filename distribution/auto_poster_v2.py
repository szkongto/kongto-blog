#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KONGTO 自动化发布助手 v2.0
使用 Playwright 实现半自动化发布
需要手动登录一次，之后可自动填写表单
"""

import json
import os
import time
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 错误：未安装 playwright")
    print("请运行：pip install playwright")
    print("然后运行：playwright install chromium")
    exit(1)


class AutoPoster:
    """自动化发布助手"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.cookies_file = 'D:/workspace/kongto-blog/distribution/cookies.json'
        self.timeout = 30000  # 30秒超时
        
    def save_cookies(self, context):
        """保存cookies（登录状态）"""
        try:
            cookies = context.cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✅ Cookies已保存至：{self.cookies_file}")
            return True
        except Exception as e:
            print(f"⚠️  保存cookies失败：{e}")
            return False
    
    def load_cookies(self, context):
        """加载cookies"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    context.add_cookies(cookies)
                print(f"✅ 已加载Cookies（自动登录）")
                return True
            else:
                print(f"⚠️  未找到Cookies文件：{self.cookies_file}")
                return False
        except Exception as e:
            print(f"❌ 加载cookies失败：{e}")
            return False
    
    def manual_login(self, page, platform_name):
        """手动登录（首次使用）"""
        print(f"\n{'='*70}")
        print(f"  首次使用 {platform_name} - 需要手动登录")
        print(f"{'='*70}")
        print("请手动完成以下操作：")
        print("  1. 在打开的浏览器中登录账号")
        print("  2. 完成验证码（如果有）")
        print("  3. 登录成功后，返回这里按 Enter")
        print(f"{'='*70}\n")
        input("登录完成后，按 Enter 继续...")
    
    def post_to_csdn(self, title, content, tags=None):
        """发布到CSDN
        Args:
            title: 文章标题
            content: 文章内容（Markdown格式）
            tags: 标签列表，如 ['工业显示器', 'CNC']
        """
        print(f"\n📝 准备发布到 CSDN：{title[:50]}...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            
            # 尝试加载cookies
            logged_in = self.load_cookies(context)
            
            page = context.new_page()
            
            # 访问CSDN后台
            print("   → 正在打开CSDN后台...")
            page.goto('https://mp.csdn.net/new', timeout=self.timeout)
            time.sleep(3)
            
            # 如果没有登录，手动登录
            if 'login' in page.url.lower() or not logged_in:
                self.manual_login(page, 'CSDN')
                self.save_cookies(context)
                # 重新访问
                page.goto('https://mp.csdn.net/new', timeout=self.timeout)
                time.sleep(3)
            
            # 填写标题
            print("   → 正在填写标题...")
            try:
                page.fill('#txtTitle', title, timeout=10000)
                time.sleep(1)
            except Exception as e:
                print(f"   ⚠️  填写标题失败：{e}")
                print("   请手动填写标题")
            
            # 填写内容（使用CKEditor）
            print("   → 正在填写内容...")
            try:
                # 等待编辑器加载
                page.wait_for_selector('.ck-editor__editable', timeout=10000)
                page.click('.ck-editor__editable')
                time.sleep(1)
                page.keyboard.type(content, delay=10)  # 模拟打字
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️  自动填写内容失败：{e}")
                print("   请手动复制粘贴内容")
            
            # 填写标签
            if tags:
                print("   → 正在添加标签...")
                for tag in tags[:5]:  # CSDN最多5个标签
                    try:
                        page.fill('.add-tag-input', tag)
                        page.press('.add-tag-input', 'Enter')
                        time.sleep(0.5)
                    except:
                        pass
            
            print(f"\n{'='*70}")
            print("  ✅ 内容已填写完成！")
            print(f"{'='*70}")
            print("请手动完成以下操作：")
            print("  1. 检查标题、内容、标签是否正确")
            print("  2. 选择合适的分类")
            print("  3. 点击「发布」按钮")
            print("  4. 如需修改内容，直接在编辑器里改")
            print(f"{'='*70}\n")
            
            input("完成后按 Enter 退出...")
            
            # 保存cookies
            self.save_cookies(context)
            
            browser.close()
            print("✅ 已退出浏览器")
    
    def post_to_jianshu(self, title, content):
        """发布到简书
        Args:
            title: 文章标题
            content: 文章内容（Markdown格式）
        """
        print(f"\n📝 准备发布到 简书：{title[:50]}...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            
            # 尝试加载cookies
            logged_in = self.load_cookies(context)
            
            page = context.new_page()
            
            # 访问简书后台
            print("   → 正在打开简书后台...")
            page.goto('https://www.jianshu.com/writer#/notebooks', timeout=self.timeout)
            time.sleep(3)
            
            # 如果没有登录，手动登录
            if 'sign_in' in page.url.lower() or not logged_in:
                self.manual_login(page, '简书')
                self.save_cookies(context)
                page.goto('https://www.jianshu.com/writer#/notebooks', timeout=self.timeout)
                time.sleep(3)
            
            # 点击新建文章
            print("   → 正在创建新文章...")
            try:
                page.click('text=新建文章', timeout=10000)
                time.sleep(2)
            except:
                print("   ⚠️  无法自动新建文章，请手动点击")
            
            # 填写标题
            print("   → 正在填写标题...")
            try:
                page.fill('.writer-title-input', title, timeout=10000)
                time.sleep(1)
            except:
                print("   ⚠️  自动填写标题失败，请手动填写")
            
            # 填写内容
            print("   → 正在填写内容...")
            try:
                page.fill('.writer-textarea', content)
                time.sleep(2)
            except:
                print("   ⚠️  自动填写内容失败，请手动复制粘贴")
            
            print(f"\n{'='*70}")
            print("  ✅ 内容已填写完成！")
            print(f"{'='*70}")
            print("请手动完成以下操作：")
            print("  1. 检查标题和内容")
            print("  2. 可以添加专题（可选）")
            print("  3. 点击「发布」按钮")
            print(f"{'='*70}\n")
            
            input("完成后按 Enter 退出...")
            
            # 保存cookies
            self.save_cookies(context)
            
            browser.close()
            print("✅ 已退出浏览器")
    
    def post_to_zhihu_answer(self, question_url, answer):
        """在知乎回答问题
        Args:
            question_url: 问题URL
            answer: 回答内容
        """
        print(f"\n📝 准备在知乎回答问题...")
        print(f"   问题URL：{question_url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            
            # 尝试加载cookies
            logged_in = self.load_cookies(context)
            
            page = context.new_page()
            
            # 访问问题页面
            print("   → 正在打开问题页面...")
            page.goto(question_url, timeout=self.timeout)
            time.sleep(3)
            
            # 如果没有登录，手动登录
            if 'signin' in page.url.lower() or not logged_in:
                self.manual_login(page, '知乎')
                self.save_cookies(context)
                page.goto(question_url, timeout=self.timeout)
                time.sleep(3)
            
            # 点击"写回答"
            print("   → 正在打开回答编辑器...")
            try:
                page.click('text=写回答', timeout=10000)
                time.sleep(2)
            except:
                print("   ⚠️  无法自动点击「写回答」，请手动点击")
            
            # 填写回答
            print("   → 正在填写回答内容...")
            try:
                page.fill('.RichTextEditor-editor', answer)
                time.sleep(2)
            except:
                print("   ⚠️  自动填写失败，请手动复制粘贴回答内容")
            
            print(f"\n{'='*70}")
            print("  ✅ 内容已填写完成！")
            print(f"{'='*70}")
            print("请手动完成以下操作：")
            print("  1. 检查回答内容")
            print("  2. 点击「发布回答」按钮")
            print("  3. 注意遵守知乎社区规范")
            print(f"{'='*70}\n")
            
            input("完成后按 Enter 退出...")
            
            # 保存cookies
            self.save_cookies(context)
            
            browser.close()
            print("✅ 已退出浏览器")
    
    def batch_post_from_files(self, platform, files_list):
        """批量从文件发布
        Args:
            platform: 平台名称 ('csdn', 'jianshu', 'zhihu')
            files_list: 文件路径列表
        """
        print(f"\n{'='*70}")
        print(f"  批量发布到 {platform.upper()}")
        print(f"  共 {len(files_list)} 个文件")
        print(f"{'='*70}\n")
        
        for idx, file_path in enumerate(files_list, 1):
            print(f"\n[{idx}/{len(files_list)}] 处理文件：{os.path.basename(file_path)}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 根据平台调用不同的发布函数
                if platform == 'csdn':
                    # 从文件名或内容中提取标题
                    title = os.path.basename(file_path).replace('.md', '').replace('_', ' ')
                    self.post_to_csdn(title=title, content=content, tags=['工业显示器', 'CNC数控'])
                
                elif platform == 'jianshu':
                    title = os.path.basename(file_path).replace('.md', '').replace('_', ' ')
                    self.post_to_jianshu(title=title, content=content)
                
                elif platform == 'zhihu':
                    # 假设文件名包含问题URL或需要手动提供
                    print("   ⚠️  知乎发布需要问题URL，请手动提供")
                    question_url = input("   请输入问题URL：")
                    # 从文件中提取回答内容（假设文件包含回答）
                    self.post_to_zhihu_answer(question_url=question_url, answer=content)
                
                # 询问是否继续
                if idx < len(files_list):
                    cont = input(f"\n是否继续发布下一个？ (y/n): ")
                    if cont.lower() != 'y':
                        break
                        
            except Exception as e:
                print(f"   ❌ 处理失败：{e}")
                cont = input("是否继续？ (y/n): ")
                if cont.lower() != 'y':
                    break
        
        print(f"\n✅ 批量发布完成！")


def main():
    """主函数 - 交互式菜单"""
    print(f"\n{'='*70}")
    print("  KONGTO 自动化发布助手 v2.0")
    print(f"{'='*70}\n")
    print("⚠️  使用说明：")
    print("  1. 首次使用需要手动登录各平台（仅一次）")
    print("  2. 登录后自动保存cookies，之后自动登录")
    print("  3. 脚本会填写表单，但发布仍需手动点击（避免被检测）")
    print("  4. 如果遇到验证码，需要手动处理")
    print(f"\n{'='*70}\n")
    
    poster = AutoPoster(headless=False)
    
    while True:
        print("\n请选择操作：")
        print("  1. 发布到 CSDN")
        print("  2. 发布到 简书")
        print("  3. 在知乎回答问题")
        print("  4. 批量发布（从文件）")
        print("  0. 退出")
        print("-" * 70)
        
        choice = input("请输入选项 (0-4): ").strip()
        
        if choice == '1':
            # 发布到CSDN
            title = input("请输入文章标题：")
            print("请输入文章内容（输入END结束）：")
            lines = []
            while True:
                line = input()
                if line == 'END':
                    break
                lines.append(line)
            content = '\n'.join(lines)
            
            tags_input = input("请输入标签（逗号分隔，可选）：")
            tags = [t.strip() for t in tags_input.split(',')] if tags_input else None
            
            poster.post_to_csdn(title, content, tags)
        
        elif choice == '2':
            # 发布到简书
            title = input("请输入文章标题：")
            print("请输入文章内容（输入END结束）：")
            lines = []
            while True:
                line = input()
                if line == 'END':
                    break
                lines.append(line)
            content = '\n'.join(lines)
            
            poster.post_to_jianshu(title, content)
        
        elif choice == '3':
            # 知乎回答问题
            question_url = input("请输入问题URL：")
            print("请输入回答内容（输入END结束）：")
            lines = []
            while True:
                line = input()
                if line == 'END':
                    break
                lines.append(line)
            answer = '\n'.join(lines)
            
            poster.post_to_zhihu_answer(question_url, answer)
        
        elif choice == '4':
            # 批量发布
            platform = input("请输入平台名称 (csdn/jianshu/zhihu)：").strip().lower()
            if platform not in ['csdn', 'jianshu', 'zhihu']:
                print("❌ 不支持的平台")
                continue
            
            file_path = input("请输入文件路径（单个文件或目录）：").strip()
            
            if os.path.isdir(file_path):
                # 目录：处理所有.md文件
                files = [os.path.join(file_path, f) for f in os.listdir(file_path) if f.endswith('.md')]
            elif os.path.isfile(file_path):
                # 单个文件
                files = [file_path]
            else:
                print("❌ 文件或目录不存在")
                continue
            
            poster.batch_post_from_files(platform, files)
        
        elif choice == '0':
            print("\n✅ 已退出")
            break
        
        else:
            print("❌ 无效选项")


if __name__ == '__main__':
    main()
