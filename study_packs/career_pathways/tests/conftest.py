"""Ensure generated outputs exist before tests that need the full 1,044-plan tree.

Large JSON (majors_selected.json, practice_tasks.json) and generated-tier study plans are gitignored and rebuilt by
`python build.py`. The holdout 5-word-overlap check and most pack tests need those outputs, so this hook rebuilds them
when they are missing (needs raw/ from fetch_sources.py). Authored license_gate.json files are restored from git
afterward so a local rebuild does not dirty the committed gate files (they only differ by evaluated_at).
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]  # .../Dreamcobots when pack is at <repo>/study_packs/career_pathways
MANIFEST = ROOT / "evidence" / "GENERATED_MANIFEST.json"
def _needs_build():
    sel = ROOT / "data" / "majors_selected.json"
    if not sel.is_file() or not (ROOT / "data" / "practice_tasks.json").is_file():
        return True
    import json
    try:
        n = len(json.loads(sel.read_text()))
    except ValueError:
        return True
    return n < 100 or len(list((ROOT / "study_plans").glob("*.md"))) < 100


def _restore_authored_license_gates():
    """Put committed authored license_gate.json bytes back after a rebuild (evaluated_at would otherwise dirty them)."""
    import build
    stems = []
    for cip in build.MAJORS:
        matches = list((ROOT / "study_plans").glob(f"{cip}_*"))
        dirs = [p for p in matches if p.is_dir()]
        if len(dirs) == 1:
            stems.append(f"study_plans/{dirs[0].name}/license_gate.json")
    if not stems:
        return
    repo = None
    for cand in (REPO, ROOT.parents[1], ROOT.parents[2]):
        if (cand / ".git").exists() or (cand / ".git").is_file():
            repo = cand
            break
    if repo is None:
        return
    rel = [str((ROOT / s).relative_to(repo)) if s.startswith("study_plans") else s for s in stems]
    # paths relative to repo
    rel = []
    pack = ROOT.relative_to(repo) if ROOT.is_relative_to(repo) else None
    if pack is None:
        return
    for cip in build.MAJORS:
        dirs = [p for p in (ROOT / "study_plans").glob(f"{cip}_*") if p.is_dir()]
        if len(dirs) == 1:
            rel.append(str(pack / "study_plans" / dirs[0].name / "license_gate.json"))
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in ("GITHUB_TOKEN", "GH_TOKEN")}
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "HEAD", "--", *rel], env=env, check=False,
                   capture_output=True)


def pytest_configure(config):
    if os.environ.get("DREAMCO_SKIP_ENSURE_GENERATED") == "1":
        return
    if not _needs_build():
        return
    if not (ROOT / "raw" / "task_statements.csv").is_file():
        raise SystemExit("generated outputs are missing and raw/ is not populated; run: python fetch_sources.py && python build.py")
    env = os.environ.copy()
    env.setdefault("DREAMCO_REPO_ROOT", str(REPO if (REPO / "study_packs" / "career_pathways").is_dir() else ROOT.parents[1]))
    # Keep the gate so generated license_gate.json files exist for schema tests.
    print("tests/conftest.py: running python build.py to create gitignored generated outputs (about 2 minutes)...",
          flush=True)
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=str(ROOT), env=env)
    if r.returncode:
        raise SystemExit(f"build.py failed with exit {r.returncode}; cannot run the pack tests without generated outputs")
    _restore_authored_license_gates()
