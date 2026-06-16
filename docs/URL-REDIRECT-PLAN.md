# SEO URL 规范与迁移方案 — cncdisplay.com

## 现状
170 个 URL 中有 100 个（59%）使用下划线分隔单词，Google 将 `_` 视为连接符（a_b → "ab"），而 `-` 是词分隔符（a-b → "a b"）。

## 新旧 URL 规范

### 正确格式（新文章必须遵守）
```
/posts/fanuc-a61l-0001-0093-lcd-upgrade-guide.html  ✅
/en/posts/siemens-vs-fanuc-cnc-display-comparison.html  ✅
/brands/fanuc.html  ✅
```

### 错误格式（旧文章，需要逐步迁移）
```
/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html  ❌ (下划线)
/posts/article_20260503_FANUC_A61L_0001_0074_LCD.html  ❌ (下划线)
```

## 迁移策略

### 阶段一：新文章规范（立即执行）
所有新发布的文章一律使用连字符格式和语义化命名：
- ✅ `fanuc-a61l-0001-0093-lcd-display-upgrade.html`
- ❌ `article_20260616_FANUC_A61L_0001_0093_LCD.html`

### 阶段二：高流量页面迁移（第1-2周）
优先迁移访问量最大的 Top 10 文章（需查看 Google Search Console 确定）：
1. 使用新 URL 创建页面
2. 在旧页面 `<head>` 添加：
   ```html
   <link rel="canonical" href="https://cncdisplay.com/posts/{new-url}.html" />
   ```
3. 通过 Cloudflare Page Rule 或 Bulk Redirect 添加 301：
   ```
   /posts/article_20260503_FANUC_A61L_0001_0093_LCD.html → /posts/fanuc-a61l-0001-0093-lcd-upgrade.html
   ```

### 阶段三：全量迁移（第3-4周）
剩余 90 个下划线 URL 采用同样方式逐步迁移。

## Cloudflare Bulk Redirect 配置

登录 Cloudflare → 规则 → Bulk Redirects，创建重定向列表：

```
/posts/article_20260503_FANUC_A61L_0001_0074_LCD.html → /posts/fanuc-a61l-0001-0074-lcd.html
/posts/article_20260503_FANUC_A61L_0001_0086_LCD.html → /posts/fanuc-a61l-0001-0086-lcd.html
/posts/article_20260503_FANUC_A61L_0001_0090_LCD.html → /posts/fanuc-a61l-0001-0090-lcd.html
/posts/article_20260503_FANUC_A61L_0001_0092_LCD.html → /posts/fanuc-a61l-0001-0092-lcd.html
/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html → /posts/fanuc-a61l-0001-0093-lcd.html
...
```

## SEO 最佳实践 Checklist
- [x] 新 URL 全部使用小写
- [x] 词语之间用连字符 `-` 分隔
- [ ] 旧 URL 设置 301 重定向到新 URL
- [ ] 更新 sitemap.xml 中的 URL
- [ ] 更新内部链接指向新 URL
- [ ] 更新 canonical 标签指向新 URL
- [ ] 在 Google Search Console 提交 sitemap 更新
