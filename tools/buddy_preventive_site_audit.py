"""Read-only regression checks for Buddy public pages and resource governance."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json

class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value)

def inspect(root):
    root = Path(root).resolve()
    website = root / "website"
    findings = []
    for page in website.rglob("*.html"):
        parser = PageLinks()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc or link.startswith(("#", "//")):
                continue
            if not parts.path:
                continue
            target = unquote(parts.path)
            dest = website / target.lstrip("/") if target.startswith("/") else page.parent / target
            dest = dest.resolve()
            if not dest.is_relative_to(website):
                findings.append({"kind":"escaped_site_root","page":page.relative_to(root).as_posix(),"link":link})
            elif not dest.exists():
                findings.append({"kind":"missing_site_asset","page":page.relative_to(root).as_posix(),"link":link})
    return findings

if __name__ == "__main__":
    import sys
    findings = inspect(Path(__file__).resolve().parents[1])
    print(json.dumps({"findings":findings,"scope":"static website links only"},indent=2))
    sys.exit(1 if findings else 0)
