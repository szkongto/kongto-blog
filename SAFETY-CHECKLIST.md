# 修改前必读 — 5步安全验证

> 任何改动前必须执行，防止重复覆盖。

## Step 1: 同步基准
```
git fetch origin && git status && git diff origin/main --stat
```
- 状态必须 clean，没有未推送的修改

## Step 2: 精确修改
- 只改目标文件，不批量操作
- 改前 Read，改后 Read 验证

## Step 3: 对比审查
```
git diff --stat && git diff
```
- [ ] 只改了目标文件？
- [ ] 导航栏链接未变动？
- [ ] SEO meta 未丢失？
- [ ] sameAs / schema 未改动？
- [ ] CSP 安全头未改动？

## Step 4: 提交推送
```
git add <files> && git commit -m "fix: 描述 — 原因" && git push origin main
```

## Step 5: 验证上线（2-5分钟后）
检查 https://cncdisplay.com/ ：
- [ ] 导航：兼容查询 + 文章 + 案例 + 下载 + 关于 + 获取报价 + 🔍搜索
- [ ] Google/Baidu/Bing 验证 meta 存在
- [ ] 关键链接可点击

## 红线
- ❌ 不要在 `seo_backup_*` 目录执行 git 命令
- ❌ 不要 `git push --force`
- ❌ 不要全局批量替换 HTML
- ❌ 合并远程 main 前必须检查冲突
