# cncdisplay.com — 严格SOP

## 核心原则

> **pre-commit hook 自动检查。不要用 --no-verify 绕过。**
> hook 挡住就修，别跳过。

## 修改流程

### Step 0: 规划（跨文件必做）

/plan

分析需求→出架构→列文件→确认后写代码。
**杜绝边猜边写导致连带bug。**

### Step 1: 修改代码

只改目标文件。

- 小改（1-2文件）直接改
- 跨文件/新增功能 → 先 /plan

### Step 2: 自查

git diff --stat          # 确认只改了目标文件
git diff                 # 逐行检查每个改动

### Step 3: 审查（改量大时推荐）

对 Claude 发：
```
帮我审查这次修改，看看有没有漏改、改错、引入回归的地方
```
自动调用 reviewer skill 做对抗性审查。

### Step 4: 提交（hook 自动检查）

git add -A
git commit -m "fix: 具体描述改了什么"

pre-commit hook 自动执行：
1. **Auto-fix** — python scripts/site_checker.py --fix
2. **Error check** — ERROR > 50 阻止提交
3. **Link check** — 断链 > 5 个阻止提交

### Step 5: 推送

git push

### hook 阻止了提交

1. 看错误信息定位问题
2. 修复后重新 git add + git commit
3. **不要**用 --no-verify

## 可用技能

- /site-check — 全站HTML质量扫描
- /plan — 改前出方案（跨文件必用）
- 帮我审查这次修改 — 调用 reviewer 做对抗性审查

## Workflow 自动化指令

### /seo-patrol — 每周SEO/GEO巡检

运行技术SEO + GEO合规 + 内容缺口 + 性能检查，生成报告到 seo_reports/。

```text
/seo-patrol
```

### /competitor-radar — 竞品情报雷达

抓取15+竞品数据 → AI分析 → 对比报告 → 行动建议。

```text
/competitor-radar
```

### /content-factory "文章主题" — 内容工厂

一键完成：关键词调研 → 英文文章 → 中文版本 → Git推送。

```text
/content-factory "FANUC A61L-0001-0093 LCD upgrade complete guide"
```

### /market-research "品类/关键词" — 市场调研

多平台（eBay/Amazon/AliExpress）品类分析 → 价格分布 → 机会点。

```text
/market-research "CNC display"
```

### /price "型号" — 定价×销量速查

Amazon + eBay 实时价格 + 销量估算，适合开新店/上新定价。

```text
/price "FANUC A61L-0001-0093"
/price "Mitsubishi MDT962B"
```

## Forum Outreach Plan

指南: docs/forum-outreach-plan.md

- 目标: Practical Machinist, CNCzone, Reddit (r/Machinists, r/CNC)
- 2-3回复/周/平台，4段结构（共情→排查→方案→协助）
- 模板: CRT闪烁/黑屏/LCD升级/对比
- 4:1 非商业:商业比例；反检测（IP多样化、措辞变换、频率限制）
- 禁联盟链接、禁复制粘贴、禁多账号

## 已知的 CI 警告（可忽略）

- weixin:// 协议链接（微信 deep link，非HTTP）
- zh/ 目录中文 URL 编码的历史遗留断链
- ${r.url} 模板变量（search.html 的 JS 模板）
