import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import buddy_masterbot_training_lane as lane
import aggregate_masterbot_training_runs as aggregator

class MasterBotTrainingPlanTests(unittest.TestCase):
    def test_emits_plan_not_checkpoint_or_trained_weights(self):
        with tempfile.TemporaryDirectory() as temp:
            output=io.StringIO()
            with patch.object(lane,"OUT",Path(temp)), patch.dict(os.environ,{
                "MASTERBOT_NAME":"DreamFinance","GITHUB_RUN_ID":"12345","GITHUB_RUN_ATTEMPT":"1"
            },clear=True), contextlib.redirect_stdout(output):
                self.assertEqual(lane.main(),0)
            path=Path(temp)/"DreamFinance"/"latest-plan.json"
            self.assertTrue(path.is_file())
            record=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(record["schema"],"dreamco.masterbot_training_plan.v1")
            self.assertEqual(record["artifact_kind"],"PLAN_ONLY_NOT_A_MODEL_CHECKPOINT")
            self.assertEqual(record["status"],"PLAN_ONLY_NOT_EXECUTED")
            self.assertFalse(record["weights_trained"])
            self.assertFalse((Path(temp)/"DreamFinance"/"latest-checkpoint.json").exists())

    def test_aggregator_reads_new_plan_and_legacy_artifact_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            new_dir=root/"new"/"DreamFinance";new_dir.mkdir(parents=True)
            old_dir=root/"old"/"DreamData";old_dir.mkdir(parents=True)
            base={"masterbot_id":1,"masterbot":"DreamFinance","run_id":"1","weights_trained":False}
            (new_dir/"latest-plan.json").write_text(json.dumps(base),encoding="utf-8")
            legacy={**base,"masterbot_id":7,"masterbot":"DreamData","run_id":"2"}
            (old_dir/"latest-checkpoint.json").write_text(json.dumps(legacy),encoding="utf-8")
            output=root/"queue.json"
            with patch("sys.argv",["aggregate_masterbot_training_runs.py","--input",str(root),"--output",str(output)]):
                self.assertEqual(aggregator.main(),0)
            result=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["records_received"],2)
            self.assertEqual(result["unique_divisions_reported"],2)
            self.assertEqual(result["status"],"AGGREGATED_RUN_EVIDENCE_NOT_MODEL_TRAINING")

    def test_unknown_masterbot_is_rejected(self):
        with patch.dict(os.environ,{"MASTERBOT_NAME":"NotARealDivision"},clear=True):
            with self.assertRaisesRegex(SystemExit,"Unknown MasterBot"):
                lane.main()

    def test_missing_masterbot_name_is_rejected(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(SystemExit,"MASTERBOT_NAME is required"):
                lane.main()

if __name__=="__main__":
    unittest.main()
