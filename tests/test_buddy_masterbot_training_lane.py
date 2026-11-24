import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import buddy_masterbot_training_lane as lane
import aggregate_masterbot_training_runs as aggregator


class MasterBotTrainingPlanTests(unittest.TestCase):
    def test_emits_plan_not_checkpoint_or_trained_weights(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            registry = root / "registry.json"
            registry.write_text(json.dumps({
                "divisions": [{"id": 1, "name": "DreamFinance"}],
                "training_lifecycle": ["rights_review", "baseline", "train"],
            }), encoding="utf-8")
            output = io.StringIO()
            with (
                patch.object(lane, "REGISTRY", registry),
                patch.object(lane, "OUT", root / "artifacts"),
                patch.dict(os.environ, {
                    "MASTERBOT_NAME": "DreamFinance",
                    "GITHUB_RUN_ID": "12345",
                    "GITHUB_RUN_ATTEMPT": "1",
                }, clear=True),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(lane.main(), 0)

            division_dir = root / "artifacts" / "DreamFinance"
            plan_path = division_dir / "latest-plan.json"
            self.assertTrue(plan_path.is_file())
            self.assertFalse((division_dir / "latest-checkpoint.json").exists())
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["schema"], "dreamco.masterbot_training_plan.v1")
            self.assertEqual(plan["artifact_kind"], "PLAN_ONLY_NOT_A_MODEL_CHECKPOINT")
            self.assertEqual(plan["status"], "PLAN_ONLY_NOT_EXECUTED")
            self.assertEqual(plan["lifecycle"], ["rights_review", "baseline", "train"])
            self.assertFalse(plan["weights_trained"])
            self.assertFalse(plan["training_job_executed"])
            self.assertFalse(plan["compute_consumed"])
            self.assertEqual(plan["mastery_claim"], "not_claimed_without_evidence")

    def test_aggregator_reads_plan_and_legacy_checkpoint_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plan_dir = root / "new" / "DreamFinance"
            legacy_dir = root / "legacy" / "DreamData"
            plan_dir.mkdir(parents=True)
            legacy_dir.mkdir(parents=True)
            plan = {
                "schema": "dreamco.masterbot_training_plan.v1",
                "artifact_kind": "PLAN_ONLY_NOT_A_MODEL_CHECKPOINT",
                "masterbot_id": 1,
                "masterbot": "DreamFinance",
                "run_id": "1",
                "weights_trained": False,
                "training_job_executed": False,
                "compute_consumed": False,
            }
            legacy = {
                "schema": "dreamco.masterbot_training_checkpoint.v2",
                "masterbot_id": 7,
                "masterbot": "DreamData",
                "run_id": "2",
                "weights_trained": False,
            }
            (plan_dir / "latest-plan.json").write_text(json.dumps(plan), encoding="utf-8")
            (legacy_dir / "latest-checkpoint.json").write_text(json.dumps(legacy), encoding="utf-8")
            output = root / "queue.json"
            with patch("sys.argv", [
                "aggregate_masterbot_training_runs.py",
                "--input", str(root),
                "--output", str(output),
            ]):
                self.assertEqual(aggregator.main(), 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["records_received"], 2)
            self.assertEqual(result["unique_divisions_reported"], 2)
            self.assertEqual(result["status"], "AGGREGATED_RUN_EVIDENCE_NOT_MODEL_TRAINING")
            self.assertFalse(any(row.get("weights_trained") for row in result["records"]))

    def test_unknown_masterbot_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            registry = Path(temp) / "registry.json"
            registry.write_text(json.dumps({"divisions": [{"id": 1, "name": "DreamFinance"}]}))
            with (
                patch.object(lane, "REGISTRY", registry),
                patch.dict(os.environ, {"MASTERBOT_NAME": "NotARealDivision"}, clear=True),
            ):
                with self.assertRaisesRegex(SystemExit, "Unknown MasterBot"):
                    lane.main()

    def test_missing_masterbot_name_is_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(SystemExit, "MASTERBOT_NAME is required"):
                lane.main()


if __name__ == "__main__":
    unittest.main()
