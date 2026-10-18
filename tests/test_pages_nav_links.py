"""Every shared-nav link points at a real website page that is also in the sitemap."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "website"


class PagesNavLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nav = (WEB / "nav.js").read_text()
        cls.hrefs = re.findall(r"\{\s*href:\s*'([^']+\.html)'", nav)
        cls.sitemap = (WEB / "sitemap.xml").read_text()

    def test_every_nav_link_is_an_existing_page(self):
        missing = [h for h in self.hrefs if not (WEB / h).is_file()]
        self.assertEqual(missing, [])

    def test_nav_links_are_unique(self):
        self.assertEqual(len(self.hrefs), len(set(self.hrefs)))

    def test_linked_product_pages_are_in_sitemap(self):
        for page in ["buddy-bootcamp.html", "buddy-live-demos.html", "bot-scores.html",
                     "three-categories.html", "go-live.html", "production-checklist.html",
                     "fail-closed-routes.html", "division-status.html"]:
            self.assertIn(page, self.hrefs)
            self.assertIn("/Dreamcobots/website/" + page, self.sitemap)


if __name__ == "__main__":
    unittest.main()
