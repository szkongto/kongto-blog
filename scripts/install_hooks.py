# -*- coding: utf-8 -*-
"""把 .github/hooks/ 下的钩子装到 .git/hooks/。

.git/hooks/ 不受版本控制，新克隆的仓库没有钩子，所以需要一个可重跑的安装脚本。
钩子本体放 .github/hooks/（受版本控制），改了就重跑本脚本。

用法：
    python scripts/install_hooks.py
"""

import os
import pathlib
import shutil
import stat
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / '.github' / 'hooks'
DST = ROOT / '.git' / 'hooks'

HOOKS = ['pre-commit']


def main():
    if not DST.parent.exists():
        print(f'!! 找不到 .git 目录：{DST.parent}', file=sys.stderr)
        sys.exit(1)
    DST.mkdir(parents=True, exist_ok=True)

    for name in HOOKS:
        src = SRC / name
        if not src.exists():
            print(f'!! 缺源文件 {src.relative_to(ROOT)}', file=sys.stderr)
            sys.exit(1)
        dst = DST / name
        shutil.copyfile(src, dst)
        dst.chmod(dst.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        print(f'已安装 {dst.relative_to(ROOT)}')

    print(f'\n完成。钩子会在每次 git commit 时跑 scripts/full_gate.py --quick。')


if __name__ == '__main__':
    main()
