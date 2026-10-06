"""Pages feature audit: features a page advertises must link to real code, data or routes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import audit_pages_features as apf  # noqa: E402


def test_verdicts_on_a_synthetic_site(tmp_path, monkeypatch):
    site = tmp_path / "website"
    (site / "data").mkdir(parents=True)
    pages = {
        "ok.html": '<button id="go">Go</button><script src="ok.js"></script>',
        "dead.html": '<button id="nothing">Nothing</button>',
        "api.html": "<script>fetch('/api/x')</script>",
        "missing.html": "<script>fetch('data/none.json')</script>",
        "form.html": '<form id="f"><button id="s" type="submit">Send</button></form>'
                     '<script>document.getElementById("f").addEventListener("submit",()=>0)</script>',
        "soon.html": "<main><p>Coming soon</p></main>",
    }
    for name, html in pages.items():
        (site / name).write_text("<!doctype html><html><body>" + html + "</body></html>")
    (site / "ok.js").write_text("document.getElementById('go').addEventListener('click',()=>fetch('data/a.json'))")
    (site / "data/a.json").write_text("{}")
    monkeypatch.setattr(apf, "SITE", site)
    rows = {r["page"]: r for r in apf.build()["rows"]}
    got = {name: rows[name]["verdict"] for name in rows}
    assert got == {"ok.html": "working", "dead.html": "stub", "api.html": "stub", "missing.html": "broken",
                   "form.html": "working", "soon.html": "stub"}, got


def test_committed_audit_is_current_and_has_no_regressions():
    assert apf.main(["--check", "--check-regressions"]) == 0


def test_page_truth_marks_stubs_from_the_audit_on_every_nav_page():
    nav = (ROOT / "website/nav.js").read_text()
    truth = (ROOT / "website/page-truth.js").read_text()
    assert "page-truth.js" in nav
    assert "data/pages-feature-audit.json" in truth and "stub" in truth
    audit = json.loads((ROOT / "website/data/pages-feature-audit.json").read_text())
    assert audit["pages"] == len([p for p in (ROOT / "website").rglob("*.html") if "node_modules" not in p.parts])
    assert {r["verdict"] for r in audit["rows"]} <= set(apf.VERDICT_RANK)
