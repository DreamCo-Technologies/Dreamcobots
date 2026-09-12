import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "generate_dreamco_repository_master_map.py"
SPEC = importlib.util.spec_from_file_location("repository_master_map", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class RepositoryMasterMapTests(unittest.TestCase):
    def test_inventory_classifies_repository_surfaces_from_relative_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = {
                ".github/workflows/health.yml": "name: health\n",
                "website/index.html": "<!doctype html>\n",
                "tests/test_health.py": "def test_health(): pass\n",
                "App_bots/helper.py": "BOT = True\n",
                "node_modules/ignored.js": "ignored\n",
                ".pytest_cache/v/cache/nodeids": "runtime cache\n",
                "website/data/repository-master-map.json": "self output\n",
                "config/generated/repository-master-map.json": "self output\n",
            }
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            payload = MODULE.build_payload(root)

        self.assertEqual(payload["summary"]["files_scanned"], 4)
        self.assertEqual(payload["summary"]["action"], 1)
        self.assertEqual(payload["summary"]["pages_asset"], 1)
        self.assertEqual(payload["summary"]["test"], 1)
        self.assertEqual(payload["summary"]["bot"], 1)

    def test_public_projection_preserves_summary_without_duplicate_file_rows(self):
        payload = {
            "schema": "dreamco.repository-master-map.v1",
            "evidence_only": True,
            "scan_digest": "abc123",
            "summary": {"files_scanned": 1},
            "connections": {"repository_to_pages": "summary"},
            "workflow_files": [".github/workflows/health.yml"],
            "page_assets": ["website/index.html"],
            "test_files": ["tests/test_health.py"],
            "files": [
                {"path": f"website/data/record-{index}.json", "bytes": 100 + index}
                for index in range(30)
            ],
        }

        public = MODULE.build_public_payload(payload)

        self.assertEqual(public["summary"], payload["summary"])
        self.assertEqual(public["scan_digest"], "abc123")
        self.assertNotIn("files", public)
        self.assertNotIn("workflow_files", public)
        self.assertLess(len(json.dumps(public)), len(json.dumps(payload)) / 2)


if __name__ == "__main__":
    unittest.main()
