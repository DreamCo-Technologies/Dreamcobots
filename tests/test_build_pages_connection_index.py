from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.build_pages_connection_index import build


class ConnectionIndexTests(unittest.TestCase):
    def test_only_tracked_files_are_published_and_only_site_html_is_a_page(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "website").mkdir()
            (root / "website/data").mkdir()
            (root / "website/data/pages-connection-index.json").write_text("{}")
            for name in ("website/page.html", "website/site.js", "source.py", "notes.html", "private.txt"):
                (root / name).write_text("fixture")
            subprocess.run(["git", "add", "website", "source.py", "notes.html"], cwd=root, check=True)
            index = build(root)
            rows = {row["path"]: row for row in index["files"]}
            self.assertEqual(index["counts"], {"tracked_files": 5, "pages": 1})
            self.assertIn("website/data/pages-connection-index.json", rows)
            self.assertNotIn("private.txt", rows)
            self.assertEqual(rows["website/page.html"]["page"], "page.html")
            self.assertEqual(rows["website/site.js"]["kind"], "asset")
            self.assertIsNone(rows["notes.html"]["page"])
            self.assertNotIn("fixture", str(index))
