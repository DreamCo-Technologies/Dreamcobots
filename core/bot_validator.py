"""
DreamCo Bot Validator — Static code analysis for uploaded bot files.

Screens Python source files for dangerous patterns before they are
executed in the sandbox.  This is a best-effort first line of defence;
true isolation is provided by the subprocess sandbox.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Blocked patterns
# ---------------------------------------------------------------------------

# String-level keyword blocks (fast pre-check before AST parsing)
_BLOCKED_STRINGS: Tuple[str, ...] = (
    "os.system(",
    "subprocess.call(",
    "subprocess.Popen(",
    "subprocess.check_output(",
    "__import__(",
    "eval(",
    "exec(",
    "compile(",
    "open(",
    "socket.socket(",
    "urllib.request",
    "http.client",
    "ftplib",
    "shutil.rmtree(",
    "shutil.move(",
)

# AST-level checks: function / attribute names that are never allowed
_BLOCKED_FUNC_NAMES: frozenset[str] = frozenset(
    {
        "eval",
        "exec",
        "compile",
        "execfile",
        "__import__",
    }
)

# Whitelisted top-level import names (everything else is allowed unless it
# appears in _BLOCKED_STRINGS above)
_ALLOWED_IMPORTS: frozenset[str] = frozenset(
    {
        "random", "math", "time", "datetime", "json", "re", "uuid",
        "dataclasses", "enum", "typing", "collections", "itertools",
        "functools", "operator", "string", "textwrap", "hashlib",
        "hmac", "secrets", "copy", "pathlib", "io", "base64",
        "abc", "contextlib", "logging",
    }
)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


class BotValidator:
    """
    Static analyser for uploaded bot Python files.

    Usage
    -----
        validator = BotValidator()
        ok, issues = validator.validate_file("/uploads/my_bot.py")
        if ok:
            run_in_sandbox("/uploads/my_bot.py")
        else:
            print(issues)
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a Python file at *file_path*.

        Returns
        -------
        (ok, issues)
            *ok* is True when no issues were found.
            *issues* is a list of human-readable problem descriptions.
        """
        # Resolve to an absolute, canonical path to prevent traversal
        try:
            resolved = Path(file_path).resolve(strict=False)
        except (OSError, ValueError) as exc:
            return False, [f"invalid file path: {exc}"]

        if not resolved.exists():
            return False, [f"file not found: {resolved.name}"]
        if resolved.suffix != ".py":
            return False, ["only .py files are accepted"]
        if resolved.stat().st_size > 512_000:  # 512 KB hard cap
            return False, ["file exceeds 512 KB size limit"]

        try:
            source = resolved.read_text(encoding="utf-8")
        except OSError:
            return False, ["could not read file"]

        return self.validate_source(source)

    def validate_source(self, source: str) -> Tuple[bool, List[str]]:
        """
        Validate raw *source* code.

        Returns
        -------
        (ok, issues)
        """
        issues: List[str] = []

        # 1. Syntax check
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return False, [f"syntax error: {exc}"]

        # 2. String-level pattern blocks
        for pattern in _BLOCKED_STRINGS:
            if pattern in source:
                issues.append(f"blocked pattern detected: {pattern!r}")

        # 3. AST-level checks
        for node in ast.walk(tree):
            # Block dangerous built-in calls
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name in _BLOCKED_FUNC_NAMES:
                    issues.append(f"call to blocked function: {name!r}")

            # Block imports of non-whitelisted standard-library OS/network modules
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top in ("os", "subprocess", "socket", "ftplib", "shutil"):
                        issues.append(f"import of blocked module: {alias.name!r}")

            if isinstance(node, ast.ImportFrom):
                module = (node.module or "").split(".")[0]
                if module in ("os", "subprocess", "socket", "ftplib", "shutil"):
                    issues.append(f"import from blocked module: {node.module!r}")

        ok = len(issues) == 0
        return ok, issues


# ---------------------------------------------------------------------------
# Standalone validate_bot function
# ---------------------------------------------------------------------------

# Patterns blocked by validate_bot (open() is intentionally omitted)
_VALIDATE_BOT_BLOCKED: Tuple[str, ...] = (
    "os.system(",
    "subprocess.call(",
    "subprocess.Popen(",
    "subprocess.check_output(",
    "__import__(",
    "eval(",
    "exec(",
    "compile(",
    "socket.socket(",
    "urllib.request",
    "http.client",
    "ftplib",
    "shutil.rmtree(",
    "shutil.move(",
)


def validate_bot(file_path: str) -> Tuple[bool, str]:
    """
    Validate a Python bot file.

    Parameters
    ----------
    file_path : str
        Path to the Python file to validate.

    Returns
    -------
    (ok, message)
        ok is True when no blocked patterns are found.
        message is "Safe" or a description of the first violation found.

    Raises
    ------
    FileNotFoundError
        If *file_path* does not exist.
    """
    resolved = Path(file_path).resolve(strict=False)
    if not resolved.exists():
        raise FileNotFoundError(f"Bot file not found: {file_path}")

    try:
        source = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"could not read file: {exc}"

    # String-level checks
    for pattern in _VALIDATE_BOT_BLOCKED:
        if pattern in source:
            return False, f"blocked pattern detected: {pattern!r}"

    # AST-level checks
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return False, f"syntax error: {exc}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in ("os", "subprocess", "socket", "ftplib", "shutil"):
                    return False, f"import of blocked module: {alias.name!r}"
        if isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".")[0]
            if module in ("os", "subprocess", "socket", "ftplib", "shutil"):
                return False, f"import from blocked module: {node.module!r}"

    return True, "Safe"
