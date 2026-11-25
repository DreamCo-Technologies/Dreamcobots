from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.create_buddy_library_guide_draft import build_draft


class LibraryGuideDraftTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_review_required_draft_without_granting_rights(self):
        path = build_draft(
            canonical_id="python-fastapi",
            name="FastAPI",
            ecosystem="python",
            official_homepage="https://fastapi.tiangolo.com/",
            documentation_url="https://fastapi.tiangolo.com/tutorial/",
            version_reviewed="not-yet-reviewed",
            root=self.root,
        )
        guide = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(guide["status"], "review_required")
        self.assertEqual(guide["rights"]["training_permission"], "pending")
        self.assertEqual(guide["rights"]["download_permission"], "pending")
        self.assertEqual(guide["api_inventory"]["coverage"], "unknown")
        self.assertEqual(len(guide["practice"]["exercises"]), 3)

    def test_refuses_existing_guide(self):
        kwargs = dict(
            canonical_id="python-fastapi", name="FastAPI", ecosystem="python",
            official_homepage="https://fastapi.tiangolo.com/",
            documentation_url="https://fastapi.tiangolo.com/tutorial/", root=self.root,
        )
        build_draft(**kwargs)
        with self.assertRaises(FileExistsError):
            build_draft(**kwargs)

    def test_rejects_non_https_source_urls(self):
        with self.assertRaises(ValueError):
            build_draft(
                canonical_id="unsafe-lib", name="Unsafe", ecosystem="python",
                official_homepage="http://example.com",
                documentation_url="https://example.com/docs", root=self.root,
            )

    def test_rejects_path_traversal_identifiers(self):
        with self.assertRaises(ValueError):
            build_draft(
                canonical_id="../escape", name="Escape", ecosystem="python",
                official_homepage="https://example.com",
                documentation_url="https://example.com/docs", root=self.root,
            )


if __name__ == "__main__":
    unittest.main()
