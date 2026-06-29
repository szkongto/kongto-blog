# cncdisplay.com 项目指令 — 严格SOP

## 核心原则

> **pre-commit hook 会自动执行所有检查。不要用 --no-verify 绕过。**
> 如果 hook 挡住了，修好问题再提交，不要跳过。

## 修改流程

### Step 1: 修改代码
按需求精确修改，只改需要的文件。

### Step 2: 自查
```bash
git diff --stat          # 确认只改了目标文件
git diff                 # 逐行检查每个改动
```

### Step 3: 提交（hook 会自动检查）
```bash
git add -A
git commit -m "fix: 具体描述改了什么"
```

pre-commit hook 自动执行：
1. **Auto-fix** — `python scripts/site_checker.py --fix` 自动修复常见问题
2. **Error check** — 剩余 ERROR > 50 则阻止提交
3. **Link check** — 断链 > 5 个则阻止提交

### Step 4: 推送
```bash
git push
```

### 如果 hook 阻止了提交
1. 看错误信息确定问题类型
2. 修复后重新 `git add` + `git commit`
3. **不要**用 `--no-verify`

## 已知的 CI 警告（可忽略）
- weixin:// 协议链接（微信 deep link，非HTTP）
- zh/ 目录中文 URL 编码的历史遗留断链
- ${r.url} 模板变量（search.html 的 JS 模板）

## 可用技能
- `/site-check` — 手动全站HTML质量扫描
