import unittest

from tools.repository_health_audit import is_redirect_stub, should_check_page_controls, is_dedicated_generated_json


class RedirectCompatibilityPageTests(unittest.TestCase):
    def test_meta_refresh_stub_delegates_to_destination(self):
        html = '<html><head><meta http-equiv="refresh" content="0; url=website/page.html"></head><body><a href="website/page.html">Open</a></body></html>'
        self.assertTrue(is_redirect_stub(html))

    def test_javascript_redirect_stub_delegates_to_destination(self):
        self.assertTrue(is_redirect_stub("<script>window.location.replace('website/page.html')</script>"))

    def test_generated_pages_index_uses_its_dedicated_validator(self):
        self.assertTrue(is_dedicated_generated_json("website/data/pages-connection-index.json"))
        self.assertFalse(is_dedicated_generated_json("website/data/other.json"))

    def test_root_redirect_compatibility_page_is_not_a_served_page(self):
        html = '<html><head><meta http-equiv="refresh" content="0; url=website/page.html"></head></html>'
        self.assertFalse(should_check_page_controls("missing-original-bots.html", html))

    def test_real_website_page_requires_shared_controls(self):
        html = '<html><body><main><h1>Page</h1></main></body></html>'
        self.assertTrue(should_check_page_controls("website/page.html", html))

    def test_website_redirect_does_not_require_shared_controls(self):
        html = '<html><head><meta http-equiv="refresh" content="0; url=buddy.html"></head></html>'
        self.assertFalse(should_check_page_controls("website/index.html", html))

    def test_real_page_is_not_misclassified_as_redirect_stub(self):
        html = '<html><body><nav><a href="home.html">Home</a></nav><main><h1>Page</h1></main></body></html>'
        self.assertFalse(is_redirect_stub(html))


if __name__ == "__main__":
    unittest.main()
