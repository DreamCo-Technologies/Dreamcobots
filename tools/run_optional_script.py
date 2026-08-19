#!/usr/bin/env python3
"""Run an optional repository script when present, otherwise skip explicitly.

Used by orchestration workflows whose capabilities are progressively installed.
The workflow remains deterministic: required entry points should still fail
normally; this helper is only for intentionally optional lanes.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parser.add_argument("--fallback", dest="fallback", default=None)
    ns = parser.parse_args()

    script = ROOT / ns.script
    args = list(ns.args)
    if script.exists():
        return subprocess.run([sys.executable, str(script), *args], cwd=ROOT).returncode

    if ns.fallback:
        fallback = ROOT / ns.fallback
        if fallback.exists():
            print(f"Optional script {ns.script} is absent; running fallback {ns.fallback}.")
            return subprocess.run([sys.executable, str(fallback), *args], cwd=ROOT).returncode

    print(f"Optional script {ns.script} is absent; lane skipped by policy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
