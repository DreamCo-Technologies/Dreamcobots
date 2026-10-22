"""Fail-closed regression tests for study-scan evidence integrity."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "tools/daily_bot_study_scan.py"
spec = importlib.util.spec_from_file_location("study_scan_candidate", MODULE)
scan_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan_mod)

class StudyIntegrityTests(unittest.TestCase):
    def test_complete_rejects_unverified_todo_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bots = Path(tmp) / "bots"
            bots.mkdir()
            file = bots / "sample.md"
            content = "## Learning plan\n- [todo] Pass sandbox capability checks (High)\n"
            file.write_text(content)
            with patch.object(scan_mod, "BOTS", bots):
                with self.assertRaisesRegex(RuntimeError, "verified sandbox receipts"):
                    scan_mod.complete_bot_studies()
            self.assertEqual(file.read_text(), content)

    def test_complete_cli_returns_nonzero_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.json"
            with patch.object(scan_mod, "LEDGER", ledger):
                self.assertEqual(scan_mod.main(["--complete"]), 2)
            self.assertFalse(ledger.exists())

    def test_compiled_file_and_cleared_todos_do_not_prove_sandbox_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = root / "bots"
            compiled = root / "runtime" / "compiled_bots"
            original = root / "original-bots"
            for directory in (bots, compiled, original):
                directory.mkdir(parents=True)
            (bots / "sample.md").write_text("## Learning plan\n- [done] Task complete\n")
            (compiled / "sample.py").write_text("print('hello')\n")
            with patch.multiple(scan_mod, ROOT=root, BOTS=bots, COMPILED=compiled,
                                ORIGINAL=original, REQUIRED=()):
                result = scan_mod.scan()
            self.assertTrue(result["bots"][0]["structural_ready"])
            self.assertFalse(result["bots"][0]["sandbox_studied"])
            self.assertEqual(result["bots"][0]["evidence_status"], "unverified")
            self.assertEqual(result["sandbox_studied"], 0)
            self.assertEqual(result["ready_basis"], "inventory_and_todos_only")

    def test_original_markdown_record_is_not_sandbox_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "original-bots").mkdir()
            (root / "bots").mkdir()
            (root / "original-bots" / "one.md").write_text("| 1 | **Example Bot** | Example mission |\n")
            with patch.multiple(scan_mod, ROOT=root, ORIGINAL=root/"original-bots", BOTS=root/"bots", REQUIRED=()):
                result = scan_mod.scan()
            self.assertEqual(result["original_bot_studies"], 1)
            self.assertFalse(result["original_bots"][0]["sandbox_studied"])
            self.assertEqual(result["original_bots"][0]["evidence_status"], "unverified")

if __name__ == "__main__":
    unittest.main()
