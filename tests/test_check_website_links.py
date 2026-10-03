#!/usr/bin/env python3
"""Tests for tools/check_website_links.py using throwaway temp sites."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_website_links.py"


def make_site(base: Path, nav_target: str) -> Path:
    site = base / "website"
    (site / "sub").mkdir(parents=True)
    (site / "good.html").write_text("<html><body>ok</body></html>\n")
    (site / "nav.js").write_text(
        "const links = [{ href: 'good.html' }, { href: 'https://example.com' }, { href: '#top' }];\n")
    (site / "index.html").write_text(
        f'<html><body><nav><a href="good.html">Good</a><a href="{nav_target}">Target</a></nav>'
        '<a href="not-in-nav.html">outside nav is ignored</a></body></html>\n')
    (site / "sub" / "page.html").write_text('<nav><a href="../good.html?x=1#y">Up</a></nav>\n')
    return site


def run_check(site: Path) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(SCRIPT), "--site", str(site)],
                          capture_output=True, text=True, timeout=60)
    return proc.returncode, json.loads(proc.stdout)


class CheckWebsiteLinksTest(unittest.TestCase):
    def test_good_nav_links_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, result = run_check(make_site(Path(tmp), "good.html#section"))
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(result["broken_count"], 0)
        self.assertEqual(result["nav_links_checked"], 4)

    def test_broken_nav_link_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, result = run_check(make_site(Path(tmp), "missing.html"))
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["broken"], [{"source": "website/index.html", "href": "missing.html"}])

    def test_missing_site_folder_is_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run([sys.executable, str(SCRIPT), "--site", str(Path(tmp) / "nope")],
                                  capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
