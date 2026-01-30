from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RunOptions:
    dry_run: bool = True
    check: bool = True  # raise error if command fails


def format_cmd(cmd: list[str]) -> str:
    # Window-friendly quoting for readable printing
    return " ".join(shlex.quote(x) for x in cmd)


def run_commands(commands: Iterable[list[str]], opts: RunOptions) -> None:
    for cmd in commands:
        print(format_cmd(cmd))
        if not opts.dry_run:
            continue
            subprocess.run(cmd, check=opts.check)
