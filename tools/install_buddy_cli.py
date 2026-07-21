#!/usr/bin/env python3
"""Install the repo-managed Buddy CLI wrapper on this laptop."""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "buddy_cli.py"
DEFAULT_BIN_DIR = Path("/usr/local/bin")
DEFAULT_COMMAND = DEFAULT_BIN_DIR / "buddy"


def wrapper_text() -> str:
    return f"""#!/bin/sh
cd {str(ROOT)!r} || exit 1
exec /usr/bin/env python3 {str(CLI)!r} "$@"
"""


def install(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(wrapper_text(), encoding="utf-8")
    mode = target.stat().st_mode
    target.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Buddy CLI wrapper.")
    parser.add_argument("--target", default=str(DEFAULT_COMMAND), help="Command path to install. Default: /usr/local/bin/buddy")
    args = parser.parse_args()
    target = Path(args.target).expanduser()
    install(target)
    print(f"Installed Buddy CLI: {target}")
    print("Try: buddy status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
