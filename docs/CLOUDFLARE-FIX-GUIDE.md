# Cloudflare Dashboard 修复指南 — cncdisplay.com

## #1 修复 HTTP→HTTPS 重定向死循环 ⚠️ CRITICAL

### 症状
访问 `http://cncdisplay.com/` 返回 301 后陷入无限重定向循环

### 修复步骤
1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择 cncdisplay.com 域名
3. **SSL/TLS → 概述**
   - 确认加密模式设为 **"完全（严格）"**（Full strict），不是"灵活"（Flexible）
   - 如果源站是 GitHub Pages（只支持 HTTPS），选"完全"即可
4. **SSL/TLS → 边缘证书**
   - 确认"始终使用 HTTPS"已开启
   - 检查是否有多个 Page Rules 或 Bulk Redirects 产生冲突
5. **规则 → Page Rules**
   - 检查是否有 `http://*cncdisplay.com/*` → `https://cncdisplay.com/$1` 规则
   - 确保只有**一条** http→https 重定向规则
6. **规则 → Bulk Redirects**
   - 确认没有额外的重定向规则与 Page Rule 冲突

### 验证
```bash
curl -I http://cncdisplay.com/
# 应返回: 301 → https://cncdisplay.com/ → 200
```

---

## #4 安全响应头（Cloudflare Workers 方式）

已创建 `_headers` 文件，但 Cloudflare 代理 GitHub Pages 时可能需要 Workers 来注入安全头。

### 方案 A：通过 Transform Rules（推荐，免费）
1. Cloudflare → 规则 → 转换规则 → 修改响应头
2. 创建新规则：
   - **当传入请求匹配**: `*cncdisplay.com/*`
   - **设置响应头**:
     ```
     Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
     X-Content-Type-Options: nosniff
     X-Frame-Options: SAMEORIGIN
     Referrer-Policy: strict-origin-when-cross-origin
     Permissions-Policy: camera=(), microphone=(), geolocation=()
     ```

### 方案 B：通过 Workers（更灵活）
如果 Transform Rules 不够用，创建 Cloudflare Worker 注入安全头。

---

## #12 从 Sitemap 移除 Google 验证文件

线上 sitemap 中包含 `google7478b8e743977291.html`，本地源文件中已不存在此 URL。

### 可能原因
Cloudflare 可能有 Worker 或 Transform Rule 自动向 sitemap 注入 URL，或有缓存。

### 修复
1. Cloudflare → 缓存 → 清除缓存 → 输入 `https://cncdisplay.com/sitemap.xml`
2. 如果使用 Cloudflare Worker 处理 sitemap，检查 Worker 代码中是否有自动添加逻辑
3. 清除后等待 5 分钟重新验证

---

## 域名配置确认清单

- [ ] SSL/TLS 模式: 完全（严格）
- [ ] 始终使用 HTTPS: 开启
- [ ] HTTP 重定向: 301（仅一条规则）
- [ ] 安全头已配置
- [ ] 缓存已清除
- [ ] 检查 sitemap 中无 Google 验证文件
