#!/usr/bin/env python3
"""Regression test: owner-system child scripts must be able to import repo-root packages.

Grok Owner Systems / `operate` failed with ``ModuleNotFoundError: No module named 'foundry'``
because ``tools/grok_run_owner_systems.py`` launched ``tools/*.py`` children with
``cwd=ROOT`` but no ``PYTHONPATH``. A script run as ``python tools/x.py`` gets ``tools/``
as ``sys.path[0]``, not the repo root, so ``foundry/`` was not importable.
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import grok_run_owner_systems as runner  # noqa: E402

PROBE_SOURCE = (
    "import foundry.weight_balancer\n"
    "print('foundry-import-ok')\n"
)


@pytest.fixture
def probe_script():
    """A throwaway child script under tools/, launched exactly like the real owner jobs."""
    path = ROOT / "tools" / f"_pythonpath_probe_{uuid.uuid4().hex}.py"
    path.write_text(PROBE_SOURCE, encoding="utf-8")
    try:
        yield path.relative_to(ROOT).as_posix()
    finally:
        path.unlink(missing_ok=True)


def test_runner_child_can_import_foundry_without_pythonpath(monkeypatch, probe_script):
    # Reproduce the CI environment: no PYTHONPATH set by the workflow.
    monkeypatch.delenv("PYTHONPATH", raising=False)
    result = runner.run_job(probe_script)
    assert "ModuleNotFoundError" not in result["stderr_tail"], result["stderr_tail"]
    assert result["state"] == "passed", result
    assert "foundry-import-ok" in result["stdout_tail"]


def test_runner_child_keeps_existing_pythonpath(monkeypatch, tmp_path, probe_script):
    # An existing PYTHONPATH entry must be preserved, not replaced.
    extra = tmp_path / "extra_site"
    extra.mkdir()
    (extra / "owner_systems_extra_marker.py").write_text("VALUE = 'kept'\n", encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", str(extra))
    probe = ROOT / probe_script
    probe.write_text(
        PROBE_SOURCE + "import owner_systems_extra_marker\nprint(owner_systems_extra_marker.VALUE)\n",
        encoding="utf-8",
    )
    result = runner.run_job(probe_script)
    assert result["state"] == "passed", result
    assert "foundry-import-ok" in result["stdout_tail"]
    assert "kept" in result["stdout_tail"]


def test_child_env_prepends_repo_root_and_preserves_existing():
    build = getattr(runner, "child_env", None)
    assert build is not None, "tools/grok_run_owner_systems.py must expose child_env()"
    env = build({"PYTHONPATH": "/already/here", "KEEP": "1"})
    assert env["PYTHONPATH"] == f"{runner.ROOT}{os.pathsep}/already/here"
    assert env["KEEP"] == "1"
    assert build({})["PYTHONPATH"] == str(runner.ROOT)
