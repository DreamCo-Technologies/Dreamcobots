"""
Bot Validator — enforces structural standards for every bot in the repository.

Every folder whose name ends with ``bot`` (case-insensitive) must contain:

  - ``config.json``                          — bot metadata
  - ``main.py``  OR  ``index.js``           — entry point
  - ``metrics.py``  OR  ``metrics.js``      — metrics tracking
  - ``README.md``                            — documentation

Usage
-----
    python scripts/bot_validator.py [--fix]

When ``--fix`` is supplied, missing files are created with safe defaults.
The script exits with code 1 if any bot still fails validation after the
optional auto-fix pass.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Standards
# ---------------------------------------------------------------------------

REQUIRED_GROUPS: list[list[str]] = [
    ["config.json"],
    ["main.py", "index.js"],
    ["metrics.py", "metrics.js"],
    ["README.md"],
]

# Default content generated when --fix creates a missing file
_DEFAULTS: dict[str, str] = {
    "config.json": json.dumps({"name": "auto-generated", "version": "1.0"}, indent=2)
    + "\n",
    "main.py": "# Auto-generated entry point\nprint('Bot running')\n",
    "metrics.py": "# Auto-generated metrics module\ndef track():\n    pass\n",
    "README.md": "# Auto-generated bot\n",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_bot_folder(path: str) -> bool:
    """Return True when any segment of *path* ends with 'bot'."""
    return any(part.lower().endswith("bot") for part in path.replace("\\", "/").split("/"))


def _validate(bot_path: str) -> list[str]:
    """Return a list of validation-failure messages for *bot_path*."""
    try:
        files = os.listdir(bot_path)
    except OSError:
        return [f"Cannot list directory: {bot_path}"]

    errors: list[str] = []
    for group in REQUIRED_GROUPS:
        if not any(f in files for f in group):
            errors.append(f"Missing one of: {group}")
    return errors


def _fix(bot_path: str) -> None:
    """Create any missing required files in *bot_path* using safe defaults."""
    try:
        existing = set(os.listdir(bot_path))
    except OSError:
        return

    for group in REQUIRED_GROUPS:
        if not any(f in existing for f in group):
            # Use the first member of the group as the canonical default
            target = group[0]
            content = _DEFAULTS.get(target, "")
            target_path = os.path.join(bot_path, target)
            with open(target_path, "w") as fh:
                fh.write(content)
            print(f"🛠️  Fixed {target} in {bot_path}")


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def scan_repo(root: str = ".", auto_fix: bool = False) -> bool:
    """
    Walk *root* and validate every bot folder found.

    Parameters
    ----------
    root : str
        Repository root to scan.
    auto_fix : bool
        When ``True``, create missing files before re-checking.

    Returns
    -------
    bool
        ``True`` if any bot failed validation (suitable for ``sys.exit``).
    """
    failed = False

    for dirpath, _dirs, _files in os.walk(root):
        # Skip hidden directories and virtual environments
        parts = dirpath.replace("\\", "/").split("/")
        if any(p.startswith(".") or p in ("node_modules", "__pycache__", "venv", ".venv") for p in parts):
            continue

        if not _is_bot_folder(dirpath):
            continue

        if auto_fix:
            _fix(dirpath)

        errors = _validate(dirpath)
        if errors:
            failed = True
            print(f"\n❌ Bot failed: {dirpath}")
            for err in errors:
                print(f"   - {err}")
        else:
            print(f"✅ Bot passed: {dirpath}")

    return failed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate bot folder structure in the repository."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-create missing required files before checking.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to scan (default: current directory).",
    )
    args = parser.parse_args(argv)

    failed = scan_repo(root=args.root, auto_fix=args.fix)

    if failed:
        print("\n🚨 BOT VALIDATION FAILED")
        return 1

    print("\n🔥 ALL BOTS VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
