#!/usr/bin/env python3
"""
DreamCo Bot Registry Compiler
==============================

Scans all bot namespace directories, extracts metadata from each bot file,
and (re)generates the ``_DREAMCO_BOTS`` catalogue section inside
``bots/global_bot_network/bot_library.py``.

Usage
-----
    python3 tools/compile_bot_registry.py [--dry-run] [--check]

Options
-------
--dry-run   Print the generated catalogue to stdout; do not write to disk.
--check     Exit with code 1 if the catalogue is out of date (CI mode).

Design principles
-----------------
* Bot identity = ``{namespace}_{filename_stem}`` for non-core namespaces,
  or just ``{filename_stem}`` for the ``core`` namespace.
* No two bots may share the same ``bot_id`` — the compiler raises an error
  on collision so drift is caught at build time, not at runtime.
* ``display_name`` is derived from the filename stem (title-cased words,
  "_bot" suffix replaced with " Bot").
* ``description`` is auto-generated from namespace and stem; enrich in the
  source file later via a per-bot MANIFEST dict (see below).
* ``source_path`` records the canonical file path relative to repo root.
* ``namespace`` records the short namespace prefix.

Per-Bot Manifest (optional enrichment)
---------------------------------------
Any bot file may define a top-level ``BOT_MANIFEST`` dict to override
auto-generated metadata:

    BOT_MANIFEST = {
        "description": "Custom description.",
        "capabilities": ["cap_a", "cap_b"],
        "version": "2.0.0",
    }

The compiler merges these overrides on top of the auto-generated values.

Namespace Map
-------------
Directories are mapped to short namespace prefixes.  Core bots (``bots/``)
are trusted and keep their filename stem as the canonical ID with no prefix.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directory → (namespace_prefix, BotCategory enum value, default description suffix)
NAMESPACE_MAP: dict[str, tuple[str, str, str]] = {
    "bots":             ("core", "SYSTEM",      "core DreamCo automation system"),
    "App_bots":         ("app",  "APP",         "mobile app automation bot"),
    "Business_bots":    ("biz",  "BUSINESS",    "business operations automation bot"),
    "Fiverr_bots":      ("fvr",  "FREELANCE",   "Fiverr platform automation bot"),
    "Marketing_bots":   ("mkt",  "MARKETING",   "marketing automation bot"),
    "Occupational_bots":("occ",  "OCCUPATIONAL","occupational intelligence bot"),
    "Real_Estate_bots": ("re",   "REAL_ESTATE", "real estate analysis bot"),
}

# Files to skip in every directory
SKIP_STEMS = frozenset({
    "__init__", "feature_1", "feature_2", "feature_3",
    "bot_base", "base_bot", "debug",
})

# Pattern for valid bot files — must end with _bot or be a recognised core file
BOT_FILE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.py$")

# Marker that surrounds the generated catalogue inside bot_library.py
CATALOGUE_START = "# <<< BEGIN GENERATED CATALOGUE >>>"
CATALOGUE_END   = "# <<< END GENERATED CATALOGUE >>>"

BOT_LIBRARY_PATH = REPO_ROOT / "bots" / "global_bot_network" / "bot_library.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_display_name(stem: str) -> str:
    """Convert a snake_case stem to a Title Case display name."""
    return stem.replace("_", " ").title()


def to_canonical_id(namespace: str, stem: str) -> str:
    """Return the canonical bot_id for a given namespace + stem."""
    if namespace == "core":
        return stem
    return f"{namespace}_{stem}"


def _extract_manifest(source: str) -> dict[str, Any]:
    """
    Parse a bot source file and return the contents of BOT_MANIFEST if present.
    Returns an empty dict if there is no manifest or parsing fails.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "BOT_MANIFEST":
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        return {}
    return {}


def _extract_main_class(source: str) -> str | None:
    """
    Return the first non-error, non-enum class name in a bot source file.
    Returns None if none is found.
    """
    skip_suffixes = ("TierError", "Error", "Exception")
    skip_exact = {"Tier", "BotStatus", "BotCategory"}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            name = node.name
            if name in skip_exact:
                continue
            if any(name.endswith(s) for s in skip_suffixes):
                continue
            if name.endswith("Enum"):
                continue
            return name
    return None


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def scan_namespaces() -> list[dict[str, Any]]:
    """
    Walk every namespace directory, extract bot metadata, and return a list
    of entry dicts sorted by namespace then stem.

    Raises
    ------
    ValueError
        If a duplicate bot_id is detected (fatal — must be fixed).
    """
    seen_ids: dict[str, str] = {}  # bot_id → source_path
    entries: list[dict[str, Any]] = []

    for dir_name, (ns_prefix, category_enum, desc_suffix) in NAMESPACE_MAP.items():
        dir_path = REPO_ROOT / dir_name
        if not dir_path.is_dir():
            continue

        for py_file in sorted(dir_path.glob("*.py")):
            stem = py_file.stem
            if stem in SKIP_STEMS:
                continue
            if not BOT_FILE_PATTERN.match(py_file.name):
                continue
            # Skip files that aren't bots (no class definition)
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            class_name = _extract_main_class(source)
            if class_name is None:
                continue

            bot_id = to_canonical_id(ns_prefix, stem)

            # Collision check
            if bot_id in seen_ids:
                raise ValueError(
                    f"Duplicate bot_id '{bot_id}':\n"
                    f"  existing → {seen_ids[bot_id]}\n"
                    f"  conflict → {py_file.relative_to(REPO_ROOT)}"
                )
            seen_ids[bot_id] = str(py_file.relative_to(REPO_ROOT))

            manifest = _extract_manifest(source)
            display = manifest.get("display_name") or to_display_name(stem)
            description = manifest.get("description") or (
                f"{to_display_name(stem)} — {desc_suffix}."
            )
            capabilities = manifest.get("capabilities") or []
            version = manifest.get("version") or "1.0.0"

            entries.append({
                "bot_id":       bot_id,
                "display_name": display,
                "description":  description,
                "category":     f"BotCategory.{category_enum}",
                "module_path":  f"{dir_name}.{stem}",
                "class_name":   class_name,
                "version":      version,
                "capabilities": capabilities,
                "namespace":    ns_prefix,
                "source_path":  str(py_file.relative_to(REPO_ROOT)),
            })

    return entries


# ---------------------------------------------------------------------------
# Code generator
# ---------------------------------------------------------------------------

def _fmt_list(items: list[str], indent: int = 12) -> str:
    """Format a Python list of strings for inclusion in generated source."""
    if not items:
        return "[]"
    pad = " " * indent
    inner = (",\n" + pad).join(f'"{item}"' for item in items)
    return f"[\n{pad}{inner},\n{' ' * (indent - 4)}]"


def generate_catalogue(entries: list[dict[str, Any]]) -> str:
    """
    Render the _DREAMCO_BOTS list body as Python source.
    Returns the text between (exclusive) the BEGIN/END markers.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = [
        f"# Generated at {now} by tools/compile_bot_registry.py",
        f"# Total bots: {len(entries)}",
        "",
    ]

    for e in entries:
        caps_str = _fmt_list(e["capabilities"])
        lines += [
            "    BotEntry(",
            f'        bot_id="{e["bot_id"]}",',
            f'        display_name="{e["display_name"]}",',
            f'        description=(',
            f'            "{e["description"]}"',
             '        ),',
            f'        category={e["category"]},',
            f'        module_path="{e["module_path"]}",',
            f'        class_name="{e["class_name"]}",',
            f'        version="{e["version"]}",',
            f'        capabilities={caps_str},',
            f'        namespace="{e["namespace"]}",',
            f'        source_path="{e["source_path"]}",',
             '    ),',
        ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# bot_library.py updater
# ---------------------------------------------------------------------------

def _read_library() -> str:
    return BOT_LIBRARY_PATH.read_text(encoding="utf-8")


def _splice_catalogue(original: str, new_catalogue: str) -> str:
    """
    Replace everything between CATALOGUE_START / CATALOGUE_END markers
    (inclusive) with the new catalogue.

    If the markers don't exist yet, replace the entire ``_DREAMCO_BOTS``
    list body.
    """
    if CATALOGUE_START in original and CATALOGUE_END in original:
        before = original[: original.index(CATALOGUE_START) + len(CATALOGUE_START)]
        after  = original[original.index(CATALOGUE_END):]
        return before + "\n" + new_catalogue + after

    # First-time: inject markers around _DREAMCO_BOTS list body
    # Find the list definition and its closing ]
    list_start_match = re.search(r"^_DREAMCO_BOTS\s*:.*=\s*\[", original, re.MULTILINE)
    if not list_start_match:
        raise RuntimeError(
            "_DREAMCO_BOTS not found in bot_library.py. "
            "Cannot inject catalogue markers."
        )
    # Find the matching closing ] — it's the last ] at column 0
    list_end_match = list(re.finditer(r"^\]$", original, re.MULTILINE))
    if not list_end_match:
        raise RuntimeError("Could not find closing ] for _DREAMCO_BOTS list.")
    last_bracket = list_end_match[-1]

    before  = original[: list_start_match.end()] + "\n" + CATALOGUE_START + "\n"
    content = new_catalogue
    after   = CATALOGUE_END + "\n" + original[last_bracket.start():]
    return before + content + after


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile the DreamCo bot registry from source directories."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print generated catalogue to stdout; do not write bot_library.py."
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Exit 1 if the generated catalogue differs from the current one (CI)."
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Print a summary of registered bots by namespace."
    )
    args = parser.parse_args(argv)

    # Scan
    try:
        entries = scan_namespaces()
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.stats or args.dry_run:
        by_ns: dict[str, int] = defaultdict(int)
        for e in entries:
            by_ns[e["namespace"]] += 1
        print(f"Scanned {len(entries)} bots:")
        for ns, count in sorted(by_ns.items()):
            print(f"  {ns:8s}  {count}")

    catalogue = generate_catalogue(entries)

    if args.dry_run:
        print("\n--- GENERATED CATALOGUE ---")
        print(catalogue[:2000], "... (truncated)" if len(catalogue) > 2000 else "")
        return 0

    original = _read_library()
    updated  = _splice_catalogue(original, catalogue)

    if args.check:
        # Strip the timestamp line before comparing so CI checks are stable
        def _strip_ts(text: str) -> str:
            return re.sub(r"^# Generated at .*$", "# Generated at <TIMESTAMP>", text, flags=re.MULTILINE)
        if _strip_ts(updated) == _strip_ts(original):
            print("bot_library.py is up to date.")
            return 0
        print(
            "bot_library.py is OUT OF DATE. "
            "Run `python3 tools/compile_bot_registry.py` to regenerate.",
            file=sys.stderr,
        )
        return 1

    BOT_LIBRARY_PATH.write_text(updated, encoding="utf-8")
    print(
        f"Wrote {len(entries)} bot entries to {BOT_LIBRARY_PATH.relative_to(REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
