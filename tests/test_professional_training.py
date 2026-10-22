import unittest

from buddy.bootcamp.professional_training import BenchmarkRun, build_training_manifest, distill_task, promotion_decision, public_summary


def example_record():
    return {"task_id":"task-1","profession":"developer","goal":"repair a form","source":"authorized demonstration","source_revision":"v1","wrapper_id":"browser-v2","mode":"observe","steps":["open form","submit fixture","verify saved record"],"result":"record saved and independently read back","customization":"add keyboard controls","split":"train","capture_consent":True,"training_consent":True,"rights_verified":True,"redacted":True,"outcome_verified":True}


class ProfessionalTrainingTests(unittest.TestCase):
    def test_distill_requires_every_attestation_and_excludes_private_fields(self):
        record=example_record(); record["training_consent"]=False
        with self.assertRaises(ValueError): distill_task(record)
        record=example_record(); record["token"]="never"
        with self.assertRaises(ValueError): distill_task(record)

    def test_distill_is_minimal_deterministic_and_customized(self):
        first=distill_task(example_record()); second=distill_task(example_record())
        self.assertEqual(first,second)
        self.assertEqual(first["customization"],"add keyboard controls")
        self.assertNotIn("capture_consent",first)

    def test_holdout_cannot_be_distilled(self):
        record=example_record(); record["split"]="hidden_test"
        with self.assertRaises(ValueError): distill_task(record)

    def test_promotion_needs_repetition_improvement_holdout_safety_and_regression(self):
        base=[BenchmarkRun(.6,.6,.9,60,0,2)]*3
        candidate=[BenchmarkRun(.9,.85,.95,30,0,1,.01)]*3
        holdout=[BenchmarkRun(.85,.8,.95,40,0,1,.01)]*3
        self.assertTrue(promotion_decision(base,candidate,holdout)["promote"])
        self.assertFalse(promotion_decision(base,candidate[:2],holdout)["promote"])
        regressed=[BenchmarkRun(.9,.85,.95,30,0,1,.03)]*3
        self.assertFalse(promotion_decision(base,regressed,holdout)["promote"])

    def test_training_manifest_is_a_handoff_without_weights_or_private_rows(self):
        row=distill_task(example_record())
        request={"run_id":"run-1","method":"LoRA","base_model":"example/base","base_revision":"abc123","base_license":"apache-2.0","dataset_license":"owner-approved","hardware":"l4x1","max_cost_usd":10,"output_repo":"owner/private-model","owner_approved":True}
        manifest=build_training_manifest(request,[row])
        self.assertFalse(manifest["weights_trained_by_this_function"])
        self.assertNotIn("examples",manifest)
        self.assertEqual(public_summary(manifest)["example_count"],1)


if __name__ == "__main__": unittest.main()
