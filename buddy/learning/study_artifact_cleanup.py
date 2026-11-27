"""Safe cleanup for temporary study downloads and lesson working files.

Only attempt-scoped directories created by this module are eligible for deletion.
Learning evidence and user-authored notes must be stored outside this workspace.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile
from typing import Iterator

_PREFIX = "dreamco-study-"


def create_study_workspace(base_dir: Path) -> Path:
    """Create a private, attempt-scoped workspace under base_dir."""
    base = Path(base_dir).expanduser().resolve()
    base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=_PREFIX, dir=base)).resolve()


def cleanup_study_downloads(workspace: Path, base_dir: Path) -> bool:
    """Delete only a module-created workspace contained directly under base_dir.

    Returns False when the workspace is already absent. Refuses symlinks, paths
    outside the configured root, and directories without our attempt prefix.
    """
    base = Path(base_dir).expanduser().resolve()
    target_input = Path(workspace).expanduser()
    if target_input.is_symlink():
        raise ValueError("refusing to clean a symlink workspace")
    target = target_input.resolve()
    if target.parent != base or not target.name.startswith(_PREFIX):
        raise ValueError("refusing to clean a path outside the study workspace")
    if not target.exists():
        return False
    if target.is_symlink() or not target.is_dir():
        raise ValueError("study workspace must be a real directory")
    shutil.rmtree(target)
    return True


@contextmanager
def study_download_workspace(base_dir: Path) -> Iterator[Path]:
    """Yield a temporary workspace and erase it on success, error, or cancellation."""
    workspace = create_study_workspace(base_dir)
    try:
        yield workspace
    finally:
        cleanup_study_downloads(workspace, base_dir)
