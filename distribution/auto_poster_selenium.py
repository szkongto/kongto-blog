#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KONGTO 浏览器自动化发布助手 v3.0
使用 Selenium 实现半自动化发布
需要手动登录一次，之后可自动填写表单
"""

import json
import os
import time
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ 错误：未安装 selenium")
    print("请运行：pip install selenium")
    print("然后下载 ChromeDriver：https://chromedriver.chromium.org/")
    exit(1)


class AutoPosterSelenium:
    """基于Selenium的自动化发布助手"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.cookies_file = 'D:/workspace/kongto-blog/distribution/cookies.json'
        self.driver = None
        self.wait = None
        
    def init_driver(self):
        """初始化浏览器驱动"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 30)
            return True
        except Exception as e:
            print(f"❌ 初始化浏览器失败：{e}")
            print("请确保已安装 ChromeDriver")
            return False
    
    def save_cookies(self):
        """保存cookies（登录状态）"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✅ Cookies已保存至：{self.cookies_file}")
            return True
        except Exception as e:
            print(f"⚠️ 保存cookies失败：{e}")
            return False
    
    def load_cookies(self, domain):
        """加载cookies"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    
                # 先访问域名
                self.driver.get(f"https://{domain}")
                time.sleep(2)
                
                # 添加cookies
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                
                print(f"✅ 已加载Cookies（自动登录）")
                return True
            else:
                print(f"⚠️ 未找到Cookies文件：{self.cookies_file}")
                return False
        except Exception as e:
            print(f"❌ 加载cookies失败：{e}")
            return False
    
    def manual_login(self, platform_name, login_url):
        """手动登录（首次使用）"""
        print(f"\n{'='*70}")
        print(f"  首次使用 {platform_name} - 需要手动登录")
        print(f"{'='*70}")
        print("请手动完成以下操作：")
        print("  1. 在打开的浏览器中登录账号")
        print("  2. 完成验证码（如果有）")
        print("  3. 登录成功后，返回这里按 Enter")
        print(f"{'='*70}\n")
        
        self.driver.get(login_url)
        input("登录完成后，按 Enter 继续...")
        self.save_cookies()
    
    def post_to_csdn(self, title, content, tags=None):
        """发布到CSDN
        Args:
            title: 文章标题
            content: 文章内容（Markdown格式）
            tags: 标签列表
        """
        print(f"\n📝 准备发布到 CSDN：{title[:50]}...")
        
        if not self.init_driver():
            return False
        
        try:
            # 尝试加载cookies
            self.load_cookies('mp.csdn.net')
            time.sleep(2)
            
            # 访问CSDN后台
            print("   → 正在打开CSDN后台...")
            self.driver.get('https://mp.csdn.net/new')
            time.sleep(3)
            
            # 检查是否需要登录
            if 'login' in self.driver.current_url.lower():
                self.manual_login('CSDN', 'https://passport.csdn.net/login')
                self.driver.get('https://mp.csdn.net/new')
                time.sleep(3)
            
            # 填写标题
            print("   → 正在填写标题...")
            try:
                title_input = self.wait.until(EC.presence_of_element_located((By.ID, 'txtTitle')))
                title_input.clear()
                title_input.send_keys(title)
                time.sleep(1)
            except TimeoutException:
                print("   ⚠️ 填写标题失败，请手动填写")
            
            # 填写内容（使用CKEditor）
            print("   → 正在填写内容...")
            try:
                # 切换到iframe（如果有）
                self.driver.switch_to.frame('editor')
                time.sleep(1)
                
                # 找到编辑器
                editor = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ck-editor__editable')))
                editor.click()
                time.sleep(1)
                
                # 输入内容
                editor.send_keys(content)
                time.sleep(2)
                
                # 切回主文档
                self.driver.switch_to.default_content()
            except Exception as e:
                print(f"   ⚠️ 自动填写内容失败：{e}")
                print("   请手动复制粘贴内容")
            
            # 填写标签
            if tags:
                print("   → 正在添加标签...")
                try:
                    for tag in tags[:5]:  # CSDN最多5个标签
                        tag_input = self.driver.find_element(By.CLASS_NAME, 'add-tag-input')
                        tag_input.clear()
                        tag_input.send_keys(tag)
                        tag_input.send_keys('\n')
                        time.sleep(0.5)
                except:
                    pass
            
            print(f"\n{'='*70}")
            print("  ✅ 内容已填写完成！")
            print(f"{'='*70}")
            print("请手动完成以下操作：")
            print("  1. 检查标题、内容、标签是否正确")
            print("  2. 选择合适的分类（如：工业自动化）")
            print("  3. 点击「发布」按钮")
            print("  4. 如需修改内容，直接在编辑器里改")
            print(f"{'='*70}\n")
            
            input("完成后按 Enter 退出...")
            
            # 保存cookies
            self.save_cookies()
            
            self.driver.quit()
            print("✅ 已退出浏览器")
            return True
            
        except Exception as e:
            print(f"❌ 发布失败：{e}")
            self.driver.quit()
            return False
    
    def post_to_jianshu(self, title, content):
        """发布到简书"""
        print(f"\n📝 准备发布到 简书：{title[:50]}...")
        
        if not self.init_driver():
            return False
        
        try:
            # 尝试加载cookies
            self.load_cookies('www.jianshu.com')
            time.sleep(2)
            
            # 访问简书后台
            print("   → 正在打开简书后台...")
            self.driver.get('https://www.jianshu.com/writer#/notebooks')
            time.sleep(3)
            
            # 检查是否需要登录
            if 'sign_in' in self.driver.current_url.lower():
                self.manual_login('简书', 'https://www.jianshu.com/sign_in')
                self.driver.get('https://www.jianshu.com/writer#/notebooks')
                time.sleep(3)
            
            # 点击新建文章
            print("   → 正在创建新文章...")
            try:
                new_note_btn = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'new-note')))
                new_note_btn.click()
                time.sleep(2)
            except TimeoutException:
                print("   ⚠️ 无法自动新建文章，请手动点击")
            
            # 填写标题
            print("   → 正在填写标题...")
            try:
                title_input = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'writer-title-input')))
                title_input.clear()
                title_input.send_keys(title)
                time.sleep(1)
            except TimeoutException:
                print("   ⚠️ 自动填写标题失败，请手动填写")
            
            # 填写内容
            print("   → 正在填写内容...")
            try:
                content_area = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'writer-textarea')))
                content_area.clear()
                content_area.send_keys(content)
                time.sleep(2)
            except TimeoutException:
                print("   ⚠️ 自动填写内容失败，请手动复制粘贴")
            
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
            self.save_cookies()
            
            self.driver.quit()
            print("✅ 已退出浏览器")
            return True
            
        except Exception as e:
            print(f"❌ 发布失败：{e}")
            self.driver.quit()
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def main():
    """主函数 - 交互式菜单"""
    print(f"\n{'='*70}")
    print("  KONGTO 浏览器自动化发布助手 v3.0 (Selenium版)")
    print(f"{'='*70}\n")
    print("⚠️ 使用说明：")
    print("  1. 首次使用需要手动登录各平台（仅一次）")
    print("  2. 登录后会在本地保存cookies")
    print("  3. 之后可以自动填写表单，但发布仍需手动点击")
    print("  4. 如果检测到验证码，需要手动处理")
    print("  5. 建议使用测试账号，不要用主账号")
    print(f"\n{'='*70}\n")
    
    poster = AutoPosterSelenium(headless=False)
    
    while True:
        print("\n请选择操作：")
        print("  1. 发布到 CSDN")
        print("  2. 发布到 简书")
        print("  3. 批量发布（从文件）")
        print("  0. 退出")
        print("-" * 70)
        
        choice = input("请输入选项 (0-3): ").strip()
        
        if choice == '1':
            # 发布到CSDN
            title = input("请输入文章标题：")
            print("请输入文章内容（Markdown格式），输入END结束：")
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
            print("请输入文章内容（Markdown格式），输入END结束：")
            lines = []
            while True:
                line = input()
                if line == 'END':
                    break
                lines.append(line)
            content = '\n'.join(lines)
            
            poster.post_to_jianshu(title, content)
        
        elif choice == '3':
            # 批量发布
            print("\n⚠️ 批量发布功能开发中...")
            print("   建议先手动测试几篇，确认脚本可用后再批量")
        
        elif choice == '0':
            print("\n✅ 已退出")
            poster.close()
            break
        
        else:
            print("❌ 无效选项")
    
    print(f"\n{'='*70}")
    print("  感谢使用 KONGTO 自动化发布助手")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
