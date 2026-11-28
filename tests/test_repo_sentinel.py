"""Offline tests for safe AST reconciliation and catalog freshness."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ast_tool = load("sentinel_ast", "stages/08_repo_sentinel/ast_consolidator.py")
sentinel = load("sentinel", "stages/08_repo_sentinel/sentinel.py")


class RepoSentinelTests(unittest.TestCase):
    def test_duplicate_scan_finds_top_level_symbols(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stages/a").mkdir(parents=True)
            (root / "tools").mkdir()
            code = "def canonical(x):\n    return x + 1\n"
            (root / "stages/a/one.py").write_text(code)
            (root / "tools/two.py").write_text(code)
            result = ast_tool.scan_duplicate_symbols(root, ["stages", "tools"])
            self.assertEqual(result["symbols_scanned"], 2)
            self.assertEqual(result["duplicates"][0]["symbol"], "canonical")

    def test_only_ast_identical_duplicates_can_be_shimmed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stages/a").mkdir(parents=True)
            (root / "tools").mkdir()
            canonical = root / "stages/a/core.py"
            duplicate = root / "tools/legacy.py"
            code = "def calculate(x):\n    return x + 1\n"
            canonical.write_text(code)
            duplicate.write_text(code)
            scan = ast_tool.scan_duplicate_symbols(root, ["stages", "tools"])
            with self.assertRaises(ValueError):
                ast_tool.consolidate_exact_duplicates(root, scan["duplicates"], {"calculate": "stages/a/core.py"}, apply=True)
            report = ast_tool.consolidate_exact_duplicates(
                root, scan["duplicates"], {"calculate": "stages/a/core.py"},
                apply=True, backup_dir=root / "backup",
            )
            self.assertEqual(report[0]["status"], "applied")
            self.assertIn("importlib.import_module", duplicate.read_text())
            self.assertTrue((root / "backup/tools/legacy.py").exists())

    def test_semantic_conflicts_are_never_rewritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stages/a").mkdir(parents=True)
            (root / "tools").mkdir()
            (root / "stages/a/core.py").write_text("def calculate(x):\n    return x + 1\n")
            duplicate = root / "tools/legacy.py"
            original = "def calculate(x):\n    return x * 2\n"
            duplicate.write_text(original)
            scan = ast_tool.scan_duplicate_symbols(root, ["stages", "tools"])
            report = ast_tool.consolidate_exact_duplicates(
                root, scan["duplicates"], {"calculate": "stages/a/core.py"},
                apply=True, backup_dir=root / "backup",
            )
            self.assertEqual(report[0]["status"], "conflict")
            self.assertEqual(duplicate.read_text(), original)

    def test_unregistered_duplicate_owner_is_reported_not_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stages").mkdir()
            (root / "tools").mkdir()
            (root / "stages/a.py").write_text("def same():\n    return 1\n")
            (root / "tools/b.py").write_text("def same():\n    return 1\n")
            scan = ast_tool.scan_duplicate_symbols(root, ["stages", "tools"])
            result = ast_tool.consolidate_exact_duplicates(root, scan["duplicates"], {})
            self.assertEqual(result[0]["status"], "unregistered_owner")

    def test_catalog_freshness_marks_missing_and_old_ledgers_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "catalog.jsonl"
            self.assertTrue(sentinel.catalog_freshness(ledger, 24)["stale"])
            old = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            ledger.write_text(json.dumps({"observed_at": old}) + "\n")
            result = sentinel.catalog_freshness(ledger, 24)
            self.assertTrue(result["stale"])
            self.assertEqual(result["record_count"], 1)

    def test_catalog_freshness_accepts_recent_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "catalog.jsonl"
            ledger.write_text(json.dumps({"observed_at": datetime.now(timezone.utc).isoformat()}) + "\n")
            self.assertFalse(sentinel.catalog_freshness(ledger, 24)["stale"])


    def test_multiple_same_file_definitions_are_left_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stages/a").mkdir(parents=True)
            (root / "tools").mkdir()
            canonical = "def calculate(x):\n    return x + 1\n"
            (root / "stages/a/core.py").write_text(canonical)
            duplicate = root / "tools/legacy.py"
            original = canonical + "\ndef calculate(y):\n    return y + 1\n"
            duplicate.write_text(original)
            scan = ast_tool.scan_duplicate_symbols(root, ["stages", "tools"])
            result = ast_tool.consolidate_exact_duplicates(
                root, scan["duplicates"], {"calculate": "stages/a/core.py"},
                apply=True, backup_dir=root / "backup",
            )
            self.assertEqual(result[0]["status"], "conflict")
            self.assertEqual(duplicate.read_text(), original)
            self.assertFalse((root / "backup/tools/legacy.py").exists())

    def test_symlinked_duplicate_is_never_rewritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = Path(tmp).parent / (Path(tmp).name + "-outside.py")
            try:
                (root / "stages/a").mkdir(parents=True)
                (root / "tools").mkdir()
                code = "def calculate(x):\n    return x + 1\n"
                (root / "stages/a/core.py").write_text(code)
                outside.write_text(code)
                (root / "tools/legacy.py").symlink_to(outside)
                scan = ast_tool.scan_duplicate_symbols(root, ["stages", "tools"])
                result = ast_tool.consolidate_exact_duplicates(
                    root, scan["duplicates"], {"calculate": "stages/a/core.py"},
                    apply=True, backup_dir=root / "backup",
                )
                self.assertEqual(result[0]["status"], "conflict")
                self.assertEqual(outside.read_text(), code)
            finally:
                outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
