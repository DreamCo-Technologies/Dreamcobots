"""CPU-only tests for the DreamCo Media Director; no model weights or GPU required."""
from __future__ import annotations
import importlib.util, json, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTOR_PATH = ROOT / "stages" / "08_media_studio" / "director.py"
SPEC = importlib.util.spec_from_file_location("dreamco_media_director", DIRECTOR_PATH)
assert SPEC and SPEC.loader
DIRECTOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DIRECTOR
SPEC.loader.exec_module(DIRECTOR)

class FakeAdapter:
    def render_shot(self, shot, context):
        return {"asset_uri": f"memory://{context['job_id']}/{shot['shot_id']}.mp4"}

class MediaDirectorTests(unittest.TestCase):
    def request(self):
        return {"media_type": "youtube", "title": "Demo episode", "shots": [
            {"shot_id": "s1", "duration_sec": 5, "visual_prompt": "A sunrise over a city."},
            {"shot_id": "s2", "duration_sec": 7, "visual_prompt": "A studio host speaks.", "dialogue_line": "Hello."},
        ]}

    def test_plan_sums_durations_and_is_not_rendered(self):
        plan = DIRECTOR.build_production_plan(self.request(), job_id="job-test")
        self.assertEqual(plan.total_duration_sec, 12.0)
        self.assertEqual(plan.to_dict()["status"], "planned_not_rendered")

    def test_rejects_empty_shot_list(self):
        request = self.request(); request["shots"] = []
        with self.assertRaises(DIRECTOR.MediaPlanError): DIRECTOR.build_production_plan(request)

    def test_rejects_duplicate_shot_ids(self):
        request = self.request(); request["shots"][1]["shot_id"] = "s1"
        with self.assertRaises(DIRECTOR.MediaPlanError): DIRECTOR.build_production_plan(request)

    def test_rejects_nonpositive_duration(self):
        request = self.request(); request["shots"][0]["duration_sec"] = 0
        with self.assertRaises(DIRECTOR.MediaPlanError): DIRECTOR.build_production_plan(request)

    def test_rejects_unknown_media_type(self):
        request = self.request(); request["media_type"] = "unbounded"
        with self.assertRaises(DIRECTOR.MediaPlanError): DIRECTOR.build_production_plan(request)

    def test_plan_writes_atomically(self):
        plan = DIRECTOR.build_production_plan(self.request(), job_id="job-file")
        with tempfile.TemporaryDirectory() as folder:
            target = DIRECTOR.write_plan(plan, Path(folder) / "plan.json")
            self.assertEqual(json.loads(target.read_text())["job_id"], "job-file")
            self.assertFalse(target.with_suffix(".json.tmp").exists())

    def test_render_requires_explicit_rights_manifest(self):
        plan = DIRECTOR.build_production_plan(self.request())
        with self.assertRaises(DIRECTOR.MediaRightsError):
            DIRECTOR.render_production(plan, assets=[], adapters={"fake": FakeAdapter()},
                                       context={"default_backend": "fake"})

    def test_unknown_rights_asset_is_blocked(self):
        with self.assertRaises(DIRECTOR.MediaRightsError):
            DIRECTOR.authorize_render_assets([{"asset_id": "unknown", "ownership_class": "unknown_do_not_publish"}])

    def test_render_uses_adapter_after_rights_gate(self):
        asset = {"asset_id": "dreamco-asset-1", "source_type": "generated",
            "source": "DreamCo original generation", "collection_date": "2026-11-27",
            "owner": "DreamCo", "license": "DREAMCO_INTERNAL_OWNED",
            "ownership_class": "synthetic_generated_by_dreamco",
            "commercial_redistribution_allowed": True, "attribution_required": False,
            "share_alike_required": False, "transformation_history": [],
            "provenance_hash": "sha256:test-fixture", "review_status": "approved"}
        request = self.request()
        for shot in request["shots"]: shot["video_backend"] = "fake"
        plan = DIRECTOR.build_production_plan(request, job_id="job-render")
        result = DIRECTOR.render_production(plan, assets=[asset], adapters={"fake": FakeAdapter()})
        self.assertEqual(result["status"], "rendered")
        self.assertEqual(len(result["shots"]), 2)
        self.assertTrue(result["plan_sha256"])

if __name__ == "__main__": unittest.main()
