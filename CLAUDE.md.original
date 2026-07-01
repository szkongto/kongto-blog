# cncdisplay.com 项目指令 — 严格SOP

## 核心原则

> **pre-commit hook 会自动执行所有检查。不要用 --no-verify 绕过。**
> 如果 hook 挡住了，修好问题再提交，不要跳过。

## 修改流程

### Step 0: 规划（跨文件修改必做）

```bash
/plan
```

Plan 会分析需求→出架构方案→列出受影响文件→你确认后才开始写代码。
**杜绝"边猜边写"导致的连带bug。**

### Step 1: 修改代码

按需求精确修改，只改需要的文件。

- 小修小改（1-2文件）直接改
- 跨文件/新增功能 → 先 /plan

### Step 2: 自查

```bash
git diff --stat          # 确认只改了目标文件
git diff                 # 逐行检查每个改动
```

### Step 3: 审查（修改量大时推荐）

对 Claude 发：
```
帮我审查这次修改，看看有没有漏改、改错、引入回归的地方
```

会自动调用 reviewer skill 做对抗性审查，抓出逻辑漏洞。

### Step 4: 提交（hook 会自动检查）

```bash
git add -A
git commit -m "fix: 具体描述改了什么"
```

pre-commit hook 自动执行：

1. **Auto-fix** — `python scripts/site_checker.py --fix` 自动修复常见问题
2. **Error check** — 剩余 ERROR > 50 则阻止提交
3. **Link check** — 断链 > 5 个则阻止提交

### Step 5: 推送

```bash
git push
```

### 如果 hook 阻止了提交

1. 看错误信息确定问题类型
2. 修复后重新 `git add` + `git commit`
3. **不要**用 `--no-verify`

## 可用技能

- `/site-check` — 手动全站HTML质量扫描
- `/plan` — 修改前先出方案（跨文件必用）
- `帮我审查这次修改` — 自动调用 reviewer 做对抗性审查

## Forum Outreach Plan

Forum outreach guide saved at `docs/forum-outreach-plan.md`:

- Targets: Practical Machinist, CNCzone, Reddit (r/Machinists, r/CNC)
- 2-3 replies/week per platform, 4-part reply structure (empathy -> troubleshoot -> solution -> offer)
- Content templates for CRT flickering, blank display, LCD upgrade, comparison threads
- 4:1 non-commercial to commercial post ratio; anti-detection measures (IP diversity, phrasing variation, rate limiting)
- No affiliate links, no copy-paste, no multi-account

## 已知的 CI 警告（可忽略）

- weixin:// 协议链接（微信 deep link，非HTTP）
- zh/ 目录中文 URL 编码的历史遗留断链
- ${r.url} 模板变量（search.html 的 JS 模板）
