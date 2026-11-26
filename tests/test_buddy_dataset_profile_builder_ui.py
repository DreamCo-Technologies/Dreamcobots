"""Browser-page checks for the Buddy Dataset Profile Builder."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "website/dataset-profile-builder.html"


class DatasetProfileBuilderUITests(unittest.TestCase):
    def test_inline_javascript_parses(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is not installed in this test environment")
        html = PAGE.read_text(encoding="utf-8")
        scripts = re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>", html, flags=re.I | re.S)
        inline_scripts = [script for script in scripts if script.strip()]
        self.assertTrue(inline_scripts, "expected inline profile-builder script")
        with tempfile.TemporaryDirectory() as directory:
            for index, script in enumerate(inline_scripts):
                path = Path(directory) / f"profile-builder-{index}.js"
                path.write_text(script, encoding="utf-8")
                result = subprocess.run(
                    [node, "--check", str(path)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_browser_added_sources_are_never_self_approved(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('status:"pending_review"', html)
        self.assertIn("training_permission_verified:false", html)
        self.assertIn("0 content items ingested", html)
        self.assertIn("No training job has run and no weights changed", html)

    def test_builder_is_linked_from_bootcamp_and_counts_are_current(self):
        bootcamp = (ROOT / "website/buddy-bootcamp.html").read_text(encoding="utf-8")
        self.assertIn("dataset-profile-builder.html", bootcamp)
        self.assertIn("1,232 bot profiles", bootcamp)
        self.assertIn("57 runtime divisions", bootcamp)


if __name__ == "__main__":
    unittest.main()
