#!/usr/bin/env python3
"""Validate all repository JSON without hiding malformed generated evidence.

Only failing files receive content-free provenance diagnostics. No repair,
network access, or file writes occur. The original Keep Green scan scope is
preserved: all *.json except files under .git and node_modules.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IGNORED = frozenset({'.git', 'node_modules'})


def prefix_class(data: bytes) -> str:
    if not data:
        return 'empty'
    if data.startswith(b'Warning: truncated output'):
        return 'tool_truncation_marker'
    if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
        return 'lfs_pointer'
    if data.startswith(b'\xef\xbb\xbf'):
        return 'utf8_bom'
    start = data.lstrip()
    if not start:
        return 'whitespace_only'
    if start[:1] in (b'{', b'[', b'"'):
        return 'json_like'
    return 'other'


def git_blob_comparison(root: Path, path: Path) -> str:
    """Compare worktree and index blobs without exposing file contents."""
    rel = path.relative_to(root).as_posix()
    try:
        indexed = subprocess.run(
            ['git', 'ls-files', '--stage', '--', rel], cwd=root,
            capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
        if len(indexed) != 1:
            return 'index_match=unknown'
        fields = indexed[0].split(maxsplit=3)
        if len(fields) != 4 or fields[2] != '0' or fields[3] != rel:
            return 'index_match=unknown'
        worktree_sha = subprocess.run(
            ['git', 'hash-object', '--no-filters', '--', rel], cwd=root,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return f'index_match={str(fields[1] == worktree_sha).lower()}'
    except (OSError, subprocess.SubprocessError):
        return 'index_match=unknown'


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob('*.json')):
        rel = path.relative_to(root)
        if any(part in IGNORED for part in rel.parts):
            continue
        try:
            data = path.read_bytes()
            json.loads(data.decode('utf-8'))
        except (OSError, UnicodeError, ValueError) as exc:
            # Avoid echoing arbitrary file content in public Actions logs.
            if 'data' not in locals():
                data = b''
            details = (
                f'bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()} '
                f'prefix={prefix_class(data)} {git_blob_comparison(root, path)}'
            )
            errors.append(f'{rel.as_posix()}: {type(exc).__name__}: {exc}; {details}')
        finally:
            if 'data' in locals():
                del data
    return errors


def main() -> int:
    failures = validate(ROOT)
    if failures:
        print('\n'.join(failures))
        return 1
    print('All discovered JSON files are valid.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
