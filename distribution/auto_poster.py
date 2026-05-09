#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化发布助手 - 使用浏览器自动化
注意：本脚本需要手动登录，且仅用于辅助发布
"""

from playwright.sync_api import sync_playwright
import time
import json
import os

class AutoPoster:
    """自动发布助手 - 使用Playwright"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.cookies_file = 'cookies.json'
    
    def save_cookies(self, context):
        """保存cookies（登录状态）"""
        cookies = context.cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)
        print(f"✓ Cookies已保存至 {self.cookies_file}")
    
    def load_cookies(self, context):
        """加载cookies"""
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
            print(f"✓ 已加载Cookies")
            return True
        return False
    
    def post_to_csdn(self, title, content, tags):
        """发布到CSDN"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            
            # 尝试加载cookies
            if not self.load_cookies(context):
                print("请先手动登录CSDN...")
                page = context.new_page()
                page.goto('https://passport.csdn.net/login')
                input("登录后按Enter继续...")
                self.save_cookies(context)
            
            # 打开发布页面
            page = context.new_page()
            page.goto('https://mp.csdn.net/new')
            time.sleep(2)
            
            # 填写标题
            page.fill('#article-title', title)
            time.sleep(1)
            
            # 填写内容（需要使用CKEditor API）
            page.evaluate(f"""
                CKEDITOR.instances.editor.setValue(`{content}`);
            """)
            time.sleep(2)
            
            # 填写标签
            for tag in tags:
                page.fill('.add-tag-input', tag)
                page.press('.add-tag-input', 'Enter')
                time.sleep(0.5)
            
            print("✓ 内容已填写，请检查后手动点击发布")
            input("按Enter退出...")
            
            browser.close()
    
    def post_to_jianshu(self, title, content):
        """发布到简书"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            
            # 加载或手动登录
            if not self.load_cookies(context):
                print("请先手动登录简书...")
                page = context.new_page()
                page.goto('https://www.jianshu.com/sign_in')
                input("登录后按Enter继续...")
                self.save_cookies(context)
            
            # 打开发布页面
            page = context.new_page()
            page.goto('https://www.jianshu.com/writer#/notebooks')
            time.sleep(2)
            
            # 点击新建文章
            page.click('.new-note')
            time.sleep(1)
            
            # 填写标题和内容
            page.fill('.title-input', title)
            page.fill('.editor-textarea', content)
            time.sleep(2)
            
            print("✓ 内容已填写，请检查后手动点击发布")
            input("按Enter退出...")
            
            browser.close()
    
    def post_to_zhihu(self, question_url, answer):
        """在知乎回答问题"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            
            # 加载或手动登录
            if not self.load_cookies(context):
                print("请先手动登录知乎...")
                page = context.new_page()
                page.goto('https://www.zhihu.com/signin')
                input("登录后按Enter继续...")
                self.save_cookies(context)
            
            # 打开问题页面
            page = context.new_page()
            page.goto(question_url)
            time.sleep(2)
            
            # 点击回答按钮
            page.click('.QuestionMainAction')
            time.sleep(1)
            
            # 填写回答
            page.fill('.RichTextEditor-editor', answer)
            time.sleep(2)
            
            print("✓ 回答已填写，请检查后手动点击发布")
            input("按Enter退出...")
            
            browser.close()


def main():
    """主函数"""
    print("=" * 70)
    print("  自动化发布助手 - 浏览器自动化版")
    print("=" * 70)
    print("\n⚠️  使用说明：")
    print("  1. 首次使用需要手动登录各平台")
    print("  2. 登录后会在本地保存cookies")
    print("  3. 之后可以自动填写表单，但发布仍需手动点击")
    print("  4. 如果检测到验证码，需要手动处理")
    print("\n" + "=" * 70)
    
    poster = AutoPoster(headless=False)
    
    # 示例：发布到CSDN
    # poster.post_to_csdn(
    #     title='文章标题',
    #     content='文章内容...',
    #     tags=['标签1', '标签2']
    # )
    
    print("\n✓ 脚本已准备就绪")
    print("  请修改 main() 函数中的参数来测试自动发布")


if __name__ == '__main__':
    main()
