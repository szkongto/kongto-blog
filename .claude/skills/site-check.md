---
name: site-check
description: Scan all HTML pages for encoding issues, stray tags, broken nav, missing meta, and auto-fix common problems
---

# Site Check — 全站HTML质量扫描

扫描 `seo_deploy/` 下所有 HTML 页面，检查常见质量问题并自动修复。

## 用法

```bash
# 扫描全部页面
python d:/code/site_checker.py

# 扫描并自动修复（删除孤立标签等）
python d:/code/site_checker.py --fix

# 扫描单个文件
python d:/code/site_checker.py brands/FANUC.html
```

## 检查项

| 等级 | 检查项 | 说明 |
|------|--------|------|
| 🔴 ERROR | 孤立 `/>` 标签 | 破坏HTML解析→导航丢失+中文乱码 |
| 🔴 ERROR | 非UTF-8编码 | 中文显示为乱码 |
| 🔴 ERROR | 缺少 `<!DOCTYPE html>` | 浏览器进入怪异模式 |
| 🔴 ERROR | 缺少 `</html>` | 页面结构不完整 |
| 🔴 ERROR | 缺少 `<meta charset>` | 中文字符无法解析 |
| 🔴 ERROR | Schema JSON解析失败 | 结构化数据无效 |
| 🟡 WARNING | 缺少/空 `<title>` | SEO影响 |
| 🟡 WARNING | 缺少/过短 Meta Description | SEO影响 |
| 🟡 WARNING | 缺少 canonical | 重复内容风险 |
| 🟡 WARNING | 缺少 viewport | 移动端显示异常 |
| 🟡 WARNING | 缺少 og:image | 社交分享无预览图 |
| 🟡 WARNING | 缺少 H1 / 多个H1 | 标题结构问题 |
| 🟡 WARNING | Title过长 >60字 | 搜索结果截断 |
| 🟡 WARNING | 导航缺少链接 | 用户无法导航 |
| 🟡 WARNING | 内部链接指向不存在文件 | 断链 |
| 🟡 WARNING | 重复标题 | 页面相互竞争 |
| 💡 INFO | UTF-8 BOM | 建议移除（大部分浏览器正常） |

## 自动修复（--fix）

- 删除孤立 `/>` 标签
- 后续可扩展：补DOVTYPE、补缺失的关闭标签等

## 与CI的关系

该检查与 pre-push hook 的链接检查互补：
- link-checker 检查**外部链接是否可访问**
- site-checker 检查**HTML结构质量**
