import json
import tempfile
import unittest
from pathlib import Path

from tools import verify_buddy_parameter_learning as verifier


class ParameterLearningVerificationTests(unittest.TestCase):
    def test_actual_training_roundtrip_preserves_repository_evidence(self):
        before = {name: verifier.digest(verifier.ROOT / name) for name in verifier.PROTECTED_FILES}
        original_weights = verifier.note_model.WEIGHTS
        original_report = verifier.note_model.REPORT
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            self.assertEqual(verifier.main(["--output-dir", str(output), "--steps", "80", "--seed", "1"]), 0)
            raw = (output / "learning-verification.json").read_text()
            report = json.loads(raw)
            self.assertTrue(report["verified"])
            self.assertTrue(all(report["checks"].values()))
            self.assertTrue(all(delta > 0 for delta in report["parameter_l2_changes"].values()))
            self.assertEqual(len(report["checkpoint_sha256"]), 64)
            self.assertLess(report["training_report"]["end_loss"], report["training_report"]["start_loss"])
            self.assertLess(report["fixed_training_sample"]["after"]["cross_entropy"], report["fixed_training_sample"]["before"]["cross_entropy"])
            self.assertFalse(report["fixed_training_sample"]["held_out"])
            self.assertFalse(report["boundaries"]["buddy_chat_model_updated"])
            self.assertEqual(report["boundaries"]["webpages_read_by_this_run"], 0)
            self.assertFalse(report["temporary_checkpoint_retained"])
            self.assertEqual({path.name for path in output.iterdir()}, {"learning-verification.json"})
            self.assertTrue(all(set(record) == {"title", "result", "limit"} for record in report["records"]))
            self.assertNotIn(str(verifier.ROOT), raw)
            self.assertNotIn(temporary, raw)
        self.assertEqual(before, {name: verifier.digest(verifier.ROOT / name) for name in verifier.PROTECTED_FILES})
        self.assertEqual(verifier.note_model.WEIGHTS, original_weights)
        self.assertEqual(verifier.note_model.REPORT, original_report)


if __name__ == "__main__":
    unittest.main()
