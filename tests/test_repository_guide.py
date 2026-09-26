import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from generate_repository_guide import render

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        if tag in ('a', 'script', 'link'):
            for key, value in attrs:
                if key in ('href', 'src'): self.urls.append(value)

class RepositoryGuideTests(unittest.TestCase):
    def test_nested_pages_and_titles_are_safe_and_exclusions_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, content in {
                'website/nested/a b.html': '<title>A &amp; B &lt;script&gt;</title>',
                'docs/HELLO WORLD.md': '# Hello',
                'node_modules/private/index.html': '<title>DO NOT INCLUDE</title>',
                'server/private.ts': 'SECRET_BODY_NOT_FOR_PUBLICATION',
            }.items():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            html = render(root)
            self.assertIn('href="nested/a%20b.html"', html)
            self.assertIn('A &amp; B &lt;script&gt;', html)
            self.assertIn('/blob/main/docs/HELLO%20WORLD.md', html)
            self.assertNotIn('DO NOT INCLUDE', html)
            self.assertNotIn('SECRET_BODY_NOT_FOR_PUBLICATION', html)

    def test_every_discovered_page_is_linked_and_local_targets_exist(self):
        html = render(ROOT)
        parser = Links()
        parser.feed(html)
        local = [unquote(urlsplit(url).path) for url in parser.urls if not urlsplit(url).scheme and not url.startswith('#')]
        for target in local:
            self.assertTrue((ROOT / 'website' / target).is_file(), target)
        for page in (ROOT / 'website').rglob('*.html'):
            self.assertIn(page.relative_to(ROOT / 'website').as_posix(), local)

    def test_guide_describes_consolidated_publisher_and_incomplete_chat_sources(self):
        html = render(ROOT)
        self.assertIn('shared deployment workflow combines rendered documentation', html)
        self.assertIn('49-record conversation index', html)
        self.assertIn('incomplete sources stay open', html)
        self.assertNotIn('Two workflows currently publish', html)

if __name__ == '__main__': unittest.main()
