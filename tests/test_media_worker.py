"""CPU-only tests for the provider-neutral media planning worker."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER_PATH = ROOT / "stages" / "08_media_studio" / "worker" / "server.py"
sys.path.insert(0, str(WORKER_PATH.parent))
SPEC = importlib.util.spec_from_file_location("dreamco_media_worker", WORKER_PATH)
assert SPEC and SPEC.loader
WORKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORKER)


class MediaWorkerTests(unittest.TestCase):
    def request(self):
        return {"media_type": "youtube", "title": "Worker test", "shots": [
            {"shot_id": "shot-1", "duration_sec": 4, "visual_prompt": "A quiet lake at dawn."}
        ]}

    def test_readiness_requires_token_and_writable_spool(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(WORKER.worker_ready(folder, None), (False, "worker_auth_not_configured"))
            self.assertEqual(WORKER.worker_ready(folder, "test-token"), (True, "ready"))

    def test_persists_generated_job_id_under_spool(self):
        with tempfile.TemporaryDirectory() as folder:
            result = WORKER.persist_plan(self.request(), folder)
            self.assertEqual(result["status"], "planned_not_rendered")
            self.assertEqual(result["plan_path"], f"{result['job_id']}/plan.json")
            saved = json.loads((Path(folder) / result["plan_path"]).read_text())
            self.assertEqual(saved["job_id"], result["job_id"])
            self.assertEqual(saved["status"], "planned_not_rendered")

    def test_rejects_invalid_plan(self):
        request = self.request()
        request["shots"] = []
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(WORKER.MediaPlanError):
                WORKER.persist_plan(request, folder)


if __name__ == "__main__":
    unittest.main()
