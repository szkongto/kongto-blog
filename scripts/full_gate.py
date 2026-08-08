# -*- coding: utf-8 -*-
"""统一全站质量门禁 — cncdisplay.com
一键跑全部检查，任何一项失败 exit 1。pre-commit 与 CI 共用。
用法: python scripts/full_gate.py          # 全跑
      python scripts/full_gate.py --quick  # 只跑硬门禁(提交用)
"""
import os, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# (名称, 命令, 是否硬门禁)
GATES = [
    ("site_checker",        ["python", "scripts/site_checker.py"],             True),
    ("redirect_hard",       ["python", "scripts/audit_redirects_hard.py"],     True),
    ("link_check",          ["python", ".github/scripts/check_links_ci.py"],   True),
    ("entry_check(5入口)",  ["python", "scripts/site_map.py", "--check"],      True),
    ("page_standard",       ["python", "scripts/check_page_standard.py"],      True),
    ("canonical",           ["python", "scripts/check_canonical.py"],          False),
    ("lang_switch",         ["python", "scripts/check_lang_switch.py"],        False),
    ("link_correctness",    ["python", "scripts/check_link_correctness.py"],   False),
    ("knowledge_data",      ["python", "scripts/validate_knowledge_data.py"],  False),
    ("redirect_audit",      ["python", "scripts/audit_redirects.py"],          False),
    ("jsonld",              ["python", "scripts/validate_jsonld.py"],          False),
]


def run():
    quick = '--quick' in sys.argv
    results = []
    for name, cmd, hard in GATES:
        if quick and not hard:
            continue
        r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
        tail = (r.stdout or '').strip().splitlines()
        tail = tail[-1] if tail else ''
        ok = r.returncode == 0
        results.append((name, ok, tail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {tail[:80]}")

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{'='*50}")
    if failed:
        print(f"FAIL: {len(failed)} 项未过 — {', '.join(failed)}")
        print("先修这些再提交，别用 --no-verify 绕过")
        sys.exit(1)
    print("ALL GATES PASSED")
    sys.exit(0)


if __name__ == '__main__':
    run()
