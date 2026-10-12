"""tools/build_system_progress_status.py must publish the file website/system-progress.html reads."""
from __future__ import annotations

import json
import re
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build_system_progress_status as progress  # noqa: E402


class SystemProgressStatusTests(unittest.TestCase):
    def test_page_reads_the_public_copy(self):
        page = (ROOT / "website" / "system-progress.html").read_text(encoding="utf-8")
        fetched = re.search(r"fetch\('\./(data/[^']+)'\)", page).group(1)
        self.assertEqual(ROOT / "website" / fetched, progress.PUBLIC_OUT)

    def test_writes_internal_and_public_copies(self):
        with TemporaryDirectory() as tmp:
            out, public = Path(tmp) / "config.json", Path(tmp) / "website" / "data" / "status.json"
            with mock.patch.object(progress, "OUT", out), mock.patch.object(progress, "PUBLIC_OUT", public), \
                    mock.patch.object(progress, "ROOT", Path(tmp)), \
                    mock.patch.object(progress, "GAPS", Path(tmp) / "missing-gap-plan.json"), redirect_stdout(StringIO()):
                self.assertEqual(progress.main(), 0)
            self.assertEqual(out.read_text(encoding="utf-8"), public.read_text(encoding="utf-8"))
            data = json.loads(public.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "dreamco.system_progress_status.v3")
        for key in ("system_build_status", "gap_count", "average_gap_percent", "gauges"):
            self.assertIn(key, data)
        # Without runtime evidence the status can never be green, and a missing gap plan is not 100%.
        self.assertNotEqual(data["system_build_status"], "green")
        self.assertEqual(data["gap_plan_status"], "not_generated")
        self.assertIsNone(data["average_gap_percent"])

    def test_committed_public_copy_is_valid(self):
        data = json.loads(progress.PUBLIC_OUT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "dreamco.system_progress_status.v3")
        self.assertIn(data["system_build_status"], {"red", "yellow", "green"})


if __name__ == "__main__":
    unittest.main()
