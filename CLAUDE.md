# cncdisplay.com 项目指令

每次修改网站代码后，必须按以下流程操作：

## Step 1: 修改代码
按需求精确修改。

## Step 2: 对比审查
```bash
git diff --stat
```

## Step 3: 跑全站质量扫描
```bash
python d:/code/site_checker.py --fix
```
确保 ERROR 为 0，WARNING 可控。

## Step 4: 提交推送
```bash
git add -A
git commit -m "fix: 具体描述改了什么"
git push
```

## 可用技能
- `/site-check` — 全站HTML质量扫描
