import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("dreamco_pr_reconcile",ROOT/"tools/dreamco_pr_reconcile.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def test_branch_ref_is_deterministic_and_namespaced():
    assert MODULE.ref_for_branch("main") == "refs/remotes/dreamco/base/main"
    assert MODULE.ref_for_branch("release/2026") == "refs/remotes/dreamco/base/release-2026"

def test_pr_inventory_path_is_repository_scoped():
    assert MODULE.INVENTORY == ROOT/"artifacts"/"dreamco-reconciliation"/"pull-request-inventory.json"
