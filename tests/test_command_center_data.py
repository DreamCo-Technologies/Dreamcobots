import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("command_center_generator", ROOT / "tools" / "generate_command_center_data.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class CommandCenterDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads = MODULE.build_bundle()

    def test_bundle_is_deterministic(self):
        first = MODULE.canonical_json(self.payloads)
        second = MODULE.canonical_json(MODULE.build_bundle())
        self.assertEqual(first, second)

    def test_runtime_test_caches_are_not_repository_evidence(self):
        self.assertIn(".pytest_cache", MODULE.IGNORED_PARTS)

    def test_repository_inventory_uses_only_git_tracked_files(self):
        tracked = {
            value.decode("utf-8")
            for value in subprocess.run(
                ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
            ).stdout.split(b"\0")
            if value
        }
        actual = {path.relative_to(ROOT).as_posix() for path in MODULE.repository_files()}
        self.assertTrue(actual)
        self.assertTrue(actual.issubset(tracked))
        self.assertNotIn("config/generated/actions-health-report.json", actual)
        self.assertNotIn("tmp/dreamco-verification/latest.json", actual)

    def test_all_statuses_use_evidence_taxonomy(self):
        allowed = set(MODULE.EVIDENCE_TAXONOMY)
        for payload in self.payloads.values():
            if "status" in payload:
                self.assertIn(payload["status"], allowed)
            for item in payload.get("items", []) + payload.get("checks", []):
                if "status" in item:
                    self.assertIn(item["status"], allowed)
                    if item["status"] != "catalogued":
                        self.assertTrue(item.get("evidence_refs"), item.get("id"))

    def test_original_bots_are_preserved_and_indexed(self):
        bots = self.payloads["bots.json"]
        expected = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "original-bots").rglob("*") if path.is_file())
        self.assertEqual(bots["original_bot_sources"], expected)
        self.assertEqual(bots["summary"]["preserved_original_bot_files"], len(expected))
        self.assertGreater(bots["summary"]["registered_bots"], 0)

    def test_public_and_canonical_outputs_match(self):
        with tempfile.TemporaryDirectory() as temporary:
            old_command, old_website = MODULE.COMMAND_DATA, MODULE.WEBSITE_DATA
            try:
                MODULE.COMMAND_DATA = Path(temporary) / "command"
                MODULE.WEBSITE_DATA = Path(temporary) / "website"
                MODULE.write_or_check(self.payloads, check=False)
                for name in MODULE.GENERATED_NAMES:
                    canonical = json.loads((MODULE.COMMAND_DATA / name).read_text())
                    public = json.loads((MODULE.WEBSITE_DATA / name).read_text())
                    self.assertEqual(canonical, public)
            finally:
                MODULE.COMMAND_DATA, MODULE.WEBSITE_DATA = old_command, old_website


if __name__ == "__main__":
    unittest.main()
