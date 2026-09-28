"""The profile audit must fail on drift without changing canonical profiles."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import ensure_bots_production_ready as readiness


class ProfileReadinessTest(unittest.TestCase):
    def run_audit(self, mutate, apply=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / "App_bots"
            bots = root / "bots"
            app.mkdir()
            bots.mkdir()
            bot = {"slug": "fixture", "displayName": "Fixture"}
            readiness.ensure_bot_fields(bot, "Fixture")
            payload = {"division": "Fixture", "total": 1, "bots": [bot]}
            mutate(payload)
            source = app / "Fixture.json"
            source.write_text(json.dumps(payload))
            before = source.read_bytes()
            (bots / "fixture.md").write_text("Existing profile")
            with contextlib.ExitStack() as stack:
                for name, value in {"ROOT": root, "APP_BOTS": app, "BOTS_MD": bots,
                                    "OUT_JSON": root / "report.json", "OUT_MD": root / "report.md"}.items():
                    stack.enter_context(patch.object(readiness, name, value))
                stack.enter_context(patch("sys.argv", ["audit"] if apply else ["audit", "--check"]))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                result = readiness.main()
            self.assertEqual(source.read_bytes(), before)
            self.assertFalse((root / "outside.md").exists())
            return result

    def test_complete_profile_passes(self):
        self.assertEqual(self.run_audit(lambda payload: None), 0)

    def test_wrong_division_total_fails_check(self):
        self.assertEqual(self.run_audit(lambda payload: payload.update(total=99)), 1)

    def test_missing_production_pack_fails_check(self):
        self.assertEqual(self.run_audit(lambda payload: payload["bots"][0].pop("systemPrompt")), 1)

    def test_duplicate_slug_fails_check(self):
        self.assertEqual(self.run_audit(lambda payload: payload.update(total=2, bots=payload["bots"] * 2)), 1)

    def test_invalid_falsy_slug_is_not_replaced(self):
        for slug in (0, False, None):
            with self.subTest(slug=slug):
                self.assertEqual(self.run_audit(lambda payload: payload["bots"][0].update(slug=slug)), 1)

    def test_unsafe_slug_is_rejected_before_writing(self):
        self.assertEqual(self.run_audit(lambda payload: payload["bots"][0].update(slug="../outside"), apply=True), 1)

    def test_unsafe_slug_fails_check(self):
        self.assertEqual(self.run_audit(lambda payload: payload["bots"][0].update(slug="../outside")), 1)
