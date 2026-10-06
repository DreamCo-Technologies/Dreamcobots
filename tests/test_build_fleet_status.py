#!/usr/bin/env python3
"""Offline tests for tools/build_fleet_status.py (network is always mocked)."""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import tools.build_fleet_status as fleet  # noqa: E402


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def _fake_api(url_map):
    def urlopen(req, timeout=None):
        url = req.full_url
        for key, payload in url_map.items():
            if key in url:
                return _Resp(json.dumps(payload).encode())
        raise urllib.error.URLError("no fixture")
    return urlopen


class FleetStatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        packs = self.root / "study_packs"
        (packs / "pack.code" / "evidence").mkdir(parents=True)
        (packs / "pack.code" / "CARD.md").write_text("# pack.code\n")
        (packs / "pack.code" / "evidence" / "run.json").write_text("{}\n")
        (packs / "hub").mkdir()
        (self.root / "config").mkdir()
        (self.root / "config" / "huggingface-capability-packs.json").write_text(
            json.dumps({"packs": [{"id": "pack.code"}, {"id": "pack.reason"}]}))
        self.report = self.root / "reports" / "FLEET_STATUS.md"
        patches = [
            mock.patch.object(fleet, "ROOT", self.root),
            mock.patch.object(fleet, "REPORT", self.report),
            mock.patch.dict("os.environ", {"GITHUB_TOKEN": "", "GH_TOKEN": ""}),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)

    def run_main(self) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = fleet.main()
        return code, self.report.read_text(encoding="utf-8")

    def test_network_down_still_writes_report_and_labels_unavailable(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("offline")) as op:
            code, text = self.run_main()
        self.assertTrue(op.called)
        self.assertEqual(code, 0)
        self.assertTrue(self.report.exists())
        self.assertIn("# Fleet Status", text)
        self.assertIn("open PRs: unavailable (URLError", text)
        self.assertIn("workflow runs: unavailable (URLError", text)
        self.assertIn("declared capability packs (config): 2", text)
        self.assertIn("pack folders in study_packs/: 2 (with CARD.md: 1)", text)
        self.assertIn("evidence files under study_packs/**/evidence: 1", text)

    def test_mocked_api_reports_pr_and_ci_states(self):
        fixtures = {
            "pulls?state=open": [
                {"number": 7, "title": "a | b", "draft": True, "head": {"ref": "feat/x"}, "updated_at": "t"},
                {"number": 8, "title": "c", "draft": False, "head": {"ref": "feat/y"}, "updated_at": "t"},
            ],
            "pulls?state=closed": [{"merged_at": "t"}, {"merged_at": None}],
            "actions/runs": {"workflow_runs": [
                {"name": "CI", "conclusion": "failure", "head_branch": "main", "html_url": "u1"},
                {"name": "CI", "conclusion": "success", "head_branch": "main", "html_url": "u0"},
                {"name": "Pages", "conclusion": "success", "head_branch": "main", "html_url": "u2"},
            ]},
        }
        with mock.patch("urllib.request.urlopen", side_effect=_fake_api(fixtures)):
            code, text = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("open: **2** (draft: 1, ready: 1)", text)
        self.assertIn("last 2 closed: merged 1, closed unmerged 1", text)
        self.assertIn("a \\| b", text)
        self.assertIn("failure: 1, success: 1", text)  # latest run per workflow only
        self.assertIn("| CI | failure | `main` | u1 |", text)
        self.assertNotIn("unavailable", text)

    def test_rejected_token_retries_anonymously(self):
        calls = []

        def urlopen(req, timeout=None):
            calls.append(req.get_header("Authorization"))
            if req.get_header("Authorization"):
                raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)
            return _Resp(b"[]")

        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "bad"}), \
                mock.patch("urllib.request.urlopen", side_effect=urlopen):
            data, err = fleet.gh_get("pulls?state=open")
        self.assertEqual((data, err), ([], None))
        self.assertEqual(calls, ["Bearer bad", None])

    def test_section_crash_is_labelled_not_fatal(self):
        def pr_section():
            raise RuntimeError("boom")

        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("offline")), \
                mock.patch.object(fleet, "pr_section", pr_section):
            code, text = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("unavailable (RuntimeError: boom)", text)


if __name__ == "__main__":
    unittest.main()
