import tempfile
import unittest
from pathlib import Path
from tools.buddy_preventive_site_audit import inspect

class PreventiveSiteAuditTests(unittest.TestCase):
    def test_rejects_escape_and_missing_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            web = Path(tmp) / "website"
            web.mkdir()
            (web / "index.html").write_text('<a href="../docs/guide.md">Guide</a><a href="missing.html">Missing</a>')
            kinds = {item["kind"] for item in inspect(tmp)}
            self.assertEqual(kinds, {"escaped_site_root", "missing_site_asset"})

    def test_valid_local_and_external_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            web = Path(tmp) / "website"
            web.mkdir()
            (web / "next.html").write_text("ok")
            (web / "index.html").write_text('<a href="next.html">Next</a><a href="https://example.org">External</a>')
            self.assertEqual(inspect(tmp), [])

if __name__ == "__main__":
    unittest.main()
