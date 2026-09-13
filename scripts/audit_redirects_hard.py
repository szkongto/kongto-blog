# -*- coding: utf-8 -*-
"""重定向硬错审计 — 提交门禁（pre-commit hook 调用）
硬错(阻止提交): 自循环 / 目标文件不存在 / 跨型号错配
警告(不阻止): 目标=首页 / 源含型号→品牌页（上下文相关，需人工判断）
退出码: 0=通过, 1=有硬错
"""
import io
import re
import os
import sys
import urllib.parse

# stdout 必须显式切 utf-8。Windows 下 stdout 被重定向到管道时 Python 走
# locale(GBK) 编码, 本脚本输出的中文在 GBK 里编不出去会抛 UnicodeEncodeError
# 并以 1 退出 —— full_gate 会把这条当成真实硬错, 而真正原因是编码不是重定向。
# 同一写法见 check_llms.py / full_gate.py。
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = '_redirects'
# re.IGNORECASE 不可省: _redirects 的路径一律小写, 而候选里 MDT1283/CD1472/
# DR5614/BM09DF 等是大写字面量——没有 IGNORECASE 时它们对小写 URL 永不命中,
# 跨型号错配与语义错配两项对整类型号静默失效。
MODEL_RE = re.compile(
    r'(A61L[- ]0001[- ]\d{4}|A02B[- ]\d{4}[- ][A-Z]\d{3}|A05B[- ]\d{4}[- ][A-Z]\d{3}|'
    r'\d{4}-\d{5}|009\d|008\d|007\d|006\d|D9MM[- ]11A|MDT[- ]?94\d|TX[- ]\d+|'
    r'C14C[- ]1472DF|DR5614|6FC3\d{3}|BM09DF|A20B[- ]\d{4})', re.IGNORECASE)

# 人工别名表 — 补 MODEL_RE 的 token 盲区。
#
# MODEL_RE 认不出的别名会让 `if sm and dm` 短路: 两侧只要一侧认不出, 这条
# 重定向就既不报错也不进警告, 等于没审。已知实例: _redirects L248
#   /products/mazak-cd1283-d1m-lcd-upgrade.html → .../mazak-mdt1283b-...
# CD1283 不在 MODEL_RE 里, 导致这条 301 从未被型号比对覆盖过。
#
# 键 = 归一化别名(大写/去连字符/去空格); 值 = 规范 key, 与 model_key() 同空间。
# 录表即等于宣布"这两个名字是同一显示器" —— 录多了会盖掉真错配, 所以每条
# 必须能指出站内依据; 依据不足不录。
ALIAS_TABLE = {
    # CD1283-D1M 与 MDT-1283B 是同一显示器的两个编号(redirect_audit_report.html
    # 记为合理), _redirects L248 已 301 归并。
    'CD1283D1M': '1283',
    # NC6225 = MDT1283B, NC6212 = MDT962B —— 候选型号收敛别名, 见
    # memory cncdisplay-candidates-resolved-20260904; 两者都无独立页。
    'NC6225': '1283',
    'NC6212': '962',
    # MDT1283B / MDT962B 不在候选表里 (只有 MDT[- ]?94\d)。补进来,
    # 否则它们作为重定向目标时永远算不出 key, 整条再次短路。
    'MDT1283B': '1283',
    'MDT962B': '962',
    # C14C-1472DF 与 A61L-0001-0094 是同一台显示器的两个编号(件号), 依据为实物标签照片:
    # D:/工作资料/KONGTO/产品图片/FANUC/0074-0094/
    #   Fanuc发那科A61L-001-0074A61L-0001-0094 new/CRT/
    #   C14C-1472D1F-A61L-0001-0094#A-LABEL.jpg
    # HITACHI 标签同一行印有 'MOD. NO. C14C-1472D1F-A' 与 'A61L-0001-0094#A'。
    # 注意: 矩阵登记写作 C14C-1472DF, 标签实为 C14C-1472D1F-A, 差一个 1 且多 -A 后缀;
    # 视为同一物, 但该差异未在本表中消除。
    'C14C1472DF': '0094',
}
_ALIAS_KEYS = sorted(ALIAS_TABLE, key=len, reverse=True)

# 待裁决清单 — 本次修正(IGNORECASE + 别名表)后新暴露、但依据不足以自行改动的错配。
#
# 与 ALIAS_TABLE 性质相反: 别名表是"已确认同一物, 放行"; 这里是"已确认有问题,
# 但不知道该改到哪"。所以不放进别名表(那等于谎称同一物), 也不静默吞掉(那等于
# 门禁说谎)。每次运行都打印, 交用户裁决。
#
# 每条必须写清: 判错的依据 + 候选落点 + 缺什么证据。缺一条就不要登记。
PENDING = {
    # 2026-09-13 清空。原唯一一条 (fanuc-c14c-1472df-lcd-upgrade.html →
    # a61l-0001-0093-lcd-upgrade.html) 已裁决: 依据实物标签照片确认 C14C-1472D1F
    # 与 A61L-0001-0094 同一显示器, 落点改指 0094 (_redirects L288 /
    # cloudflare-worker.js L410 / compatibility-matrix.html 表格行 + COMPAT_DATA 数组),
    # 并把 C14C1472DF 登记进 ALIAS_TABLE —— 否则源 key '1472' 与目标 key '0094'
    # 不等, 门禁会立刻报跨型号错配。
}


def find_model(text):
    """取文本里的型号 token。返回匹配到的字符串, 无则 None。

    先走 MODEL_RE; 正则认不出时查人工别名表兜底。src 与 dst 两侧都必须用
    本函数, 只用 MODEL_RE 会把认不出的整条重定向丢掉(静默不审)。
    """
    m = MODEL_RE.search(text)
    if m:
        return m.group(0)
    if text:
        n = text.replace('-', '').replace(' ', '').upper()
        for alias in _ALIAS_KEYS:
            if alias in n:
                return alias
    return None


def dec(s):
    return urllib.parse.unquote(s)


def target_exists(urlpath):
    p = dec(urlpath).lstrip('/').split('?')[0]
    if not p or p.endswith('/'):
        return True  # 目录路径不判错
    return os.path.isfile(p)


def model_key(m):
    """型号身份键：取尾部 4 位数字（0093 vs A61L-0001-0093 视为同型号）；
    无 4 位数字则用全归一化串（如 BM09DF）。别名表优先。"""
    n = m.replace('-', '').replace(' ', '').upper()
    if n in ALIAS_TABLE:
        return ALIAS_TABLE[n]
    import re as _re
    digits = _re.findall(r'\d{4}', n)
    return digits[-1] if digits else n


lines = [l for l in open(SRC, encoding='utf-8').read().splitlines()
         if l.strip() and not l.startswith('#')]
hard = []
pending = []
for ln in lines:
    m = re.match(r'^(\S+)\s+(\S+)\s+(30[12])\s*$', ln)
    if not m:
        continue  # 格式错由 worker 生成步骤报
    src, dst = m.group(1), m.group(2)
    # 自循环
    if src == dst or dec(src) == dec(dst):
        hard.append((ln, '自循环'))
        continue
    # 目标文件不存在（非 http / 非目录）
    if not dst.startswith('http') and not target_exists(dst):
        hard.append((ln, f'目标不存在: {dec(dst)[:50]}'))
        continue
    # 跨型号错配 (已登记为待裁决的, 转 pending, 同时跳过后面的语义错配判定)
    if (src, dst) in PENDING:
        pending.append(((src, dst), PENDING[(src, dst)]))
        continue
    sm = find_model(src)
    dm = find_model(dst)
    if sm and dm and model_key(sm) != model_key(dm):
        # 已知纠错白名单: 错误型号 → 正确型号(刻意修正, 非错配)
        if (model_key(sm), model_key(dm)) in (('3998', '3988'),):
            continue
        hard.append((ln, f'跨型号错配: {sm} → {dm}'))

    # 语义错配: 源含型号, 目标是具体产品/文章页, 但目标页内容不含该型号 → 落地页语义不对
    # 跳过聚合页(品牌/指南/索引/方案/对比) — 它们合法地不逐型号提及
    if sm:
        dkey = model_key(sm)
        dst_file = dec(dst).lstrip('/').split('?')[0]
        if (not dst.startswith('http') and dst_file and os.path.isfile(dst_file)
                and not dst_file.endswith('/')):
            base_l = dst_file.lower()
            if ('.pdf' in base_l or 'brands/' in base_l or 'index.' in base_l
                    or any(t in base_l for t in ('guide', 'solution', 'faq',
                                                 'comparison', 'catalog', 'overview',
                                                 'troubleshoot', 'maintenance',
                                                 'compatib', 'knowledge'))):
                continue  # PDF二进制/聚合/通用页, 不判
            dcontent = open(dst_file, encoding='utf-8', errors='ignore').read()
            if dkey not in dcontent:
                hard.append((ln, f'语义错配: 源含型号{sm}但目标页({dst_file})不含该型号'))

if hard:
    print(f'\n[REDIRECT-AUDIT] 发现 {len(hard)} 条硬错，阻止提交:')
    for ln, why in hard:
        print(f'  [{why}] {ln}')
    print('\n修复 _redirects 后重试。参考: python scripts/audit_redirects.py')
    sys.exit(1)
print('[REDIRECT-AUDIT] OK — 无自循环/目标404/跨型号错配')
if pending:
    print(f'\n[REDIRECT-PENDING] {len(pending)} 条待裁决(不阻止提交, 但未修复):')
    for (s, d), why in pending:
        print(f'  {s} → {d}\n    {why}')
sys.exit(0)
