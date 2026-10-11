"""Per-file prospectus generator: coverage, purpose extraction, references and drift check."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import build_file_prospectus as bfp  # noqa: E402

INDEX = json.loads((ROOT / "config/generated/file-prospectus/index.json").read_text())


def test_committed_index_is_current():
    assert bfp.main(["--check"]) == 0


def test_every_repository_file_has_exactly_one_prospectus():
    rows = []
    for shard in INDEX["shards"]:
        rows += json.loads((ROOT / "config/generated/file-prospectus" / shard["url"]).read_text())["rows"]
    paths = [r[0] for r in rows]
    assert len(paths) == len(set(paths)) == INDEX["files"]
    assert set(paths) == set(bfp.list_files())
    for row in rows:
        rec = bfp.decode_row(INDEX, row)
        assert rec["purpose"] and rec["owner"] and rec["readiness"] and rec["type"], rec["path"]
        assert rec["purpose_source"] in {"docstring", "header", "readme", "auto-summary", "owner"}
        if rec["purpose_source"] == "auto-summary":
            assert rec["purpose"].startswith("auto-summary:")


def test_no_per_file_markdown_blobs():
    out = ROOT / "config/generated/file-prospectus"
    assert not list(out.glob("*.md")) and len(list(out.glob("*.json"))) == len(INDEX["shards"]) + 1


def test_purpose_extraction():
    assert bfp.header_purpose("a.py", "python", '"""Build the thing. More text."""\n')[0] == "Build the thing."
    assert bfp.header_purpose("a.ts", "typescript", "// Routes requests to bots.\nexport {}\n")[0] == "Routes requests to bots."
    md = "# Smart Factory\n\n> **Division:** X | **Tier:** Y\n\n## Description\nIndustry 4.0 platform with IoT.\n"
    assert bfp.header_purpose("bots/x.md", "markdown", md)[0] == "Smart Factory: Industry 4.0 platform with IoT."
    assert bfp.header_purpose("a.json", "json", '{"description": "Registry of jobs"}')[0] == "Registry of jobs"
    assert bfp.header_purpose("a.html", "html", "<title>Files</title>")[0] == "Files"
    assert bfp.header_purpose("a.json", "json", "[1,2]") is None
    assert bfp.auto_summary("tests/test_widget_maker.py", "test/python") == "auto-summary: tests for widget maker"


def test_purpose_redacts_credentials():
    assert "[redacted]" in bfp.clean("token sk-abcdefghijklmnop leaked")


def test_reference_graph_python_js_alias_and_html():
    files = ["pkg/__init__.py", "pkg/core.py", "app.py", "client/src/lib/util.ts", "client/src/page.tsx",
             "shared/schema.ts", "server/x.ts", "website/index.html", "website/app.js", "tests/test_core.py", "big.json"]
    files += [f"x{i}/y.py" for i in range(200)]
    types = {f: bfp.file_type(f) for f in files}
    texts = {
        "app.py": "from pkg.core import run\nimport pkg\n",
        "client/src/page.tsx": "import { u } from '@/lib/util';\nimport s from '@shared/schema';\n",
        "server/x.ts": "import { s } from '../shared/schema';\n",
        "website/index.html": '<script src="app.js"></script>',
        "tests/test_core.py": "from pkg import core\n",
        "big.json": json.dumps({"paths": [f"pkg/core.py"] + [f"x{i}/y.py" for i in range(200)]}),
        **{f"x{i}/y.py": "" for i in range(200)},
        "pkg/core.py": "", "pkg/__init__.py": "", "client/src/lib/util.ts": "", "shared/schema.ts": "", "website/app.js": "",
    }
    used = bfp.build_references(files, types, texts)
    assert used["pkg/core.py"] == {"app.py", "tests/test_core.py"}
    assert used["client/src/lib/util.ts"] == {"client/src/page.tsx"}
    assert used["shared/schema.ts"] == {"client/src/page.tsx", "server/x.ts"}
    assert used["website/app.js"] == {"website/index.html"}


def test_bot_specs_are_owned_by_their_bot_with_auditor_readiness():
    rows = json.loads((ROOT / "config/generated/file-prospectus/bots.json").read_text())["rows"]
    rec = bfp.decode_row(INDEX, next(r for r in rows if r[0] == "bots/ad-copy.md"))
    assert rec["owner"] == "bot:ad-copy" and rec["owner_source"] == "manifest"
    status = json.loads((ROOT / "website/data/fleet-runtime-status.json").read_text())
    state = next(r[4] for r in status["bots"] if r[0] == "ad-copy")
    assert rec["readiness"] == state


def test_case_colliding_templates_use_their_distinct_tracked_contents():
    import subprocess
    for path in ('.github/PULL_REQUEST_TEMPLATE.md', '.github/pull_request_template.md'):
        expected = subprocess.check_output(['git', 'show', ':' + path], cwd=ROOT).decode('utf-8')
        assert bfp.read_text(path) == expected
