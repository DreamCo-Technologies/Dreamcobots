"""Synthetic security tests; no training, network or model inference."""
import copy
import json
import unittest
from pathlib import Path
from tools.validate_buddy_lora_proposal import ProposalError, parse_proposal, validate

TEMPLATE = Path(__file__).resolve().parents[1] / "config/buddy-lora-experiment-proposal.json"


class ProposalPreflightTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_rejects_duplicate_authorization_key_before_validation(self):
        # A duplicate field must not be resolved by "last value wins".
        raw = json.dumps(self.p).replace(
            '"execution_authorized": false',
            '"execution_authorized": true, "execution_authorized": false',
            1,
        )
        with self.assertRaisesRegex(ProposalError, "duplicate JSON key"):
            parse_proposal(raw)

    def test_rejects_nested_duplicate_receipt_keys(self):
        raw = '{"metadata":{"receipt":"first","receipt":"second"}}'
        with self.assertRaisesRegex(ProposalError, "duplicate JSON key"):
            parse_proposal(raw)

    def test_rejects_nonfinite_json_constants(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                raw = json.dumps(self.p).replace(
                    '"compute_budget_usd": 0', '"compute_budget_usd": ' + constant, 1
                )
                with self.assertRaisesRegex(ProposalError, "nonfinite JSON constant"):
                    parse_proposal(raw)

    def test_rejects_overflowed_exponent_and_nonfinite_hyperparameters(self):
        # JSON 1e999 is valid syntax but Python decodes it as infinity.
        # NaN/Infinity can also arrive through direct validate() calls.
        for field in ("dropout", "learning_rate"):
            with self.subTest(field=field, case="json_exponent_overflow"):
                raw = json.dumps(self.p).replace(
                    f'"{field}": {self.p[field]}', f'"{field}": 1e999', 1
                )
                with self.assertRaisesRegex(ProposalError, "invalid " + field):
                    validate(parse_proposal(raw))
            for value in (float("nan"), float("inf"), -float("inf")):
                with self.subTest(field=field, case=str(value)):
                    p = copy.deepcopy(self.p)
                    p[field] = value
                    with self.assertRaisesRegex(ProposalError, "invalid " + field):
                        validate(p)

    def test_valid_proposal_json_parses_without_authorizing_training(self):
        parsed = parse_proposal(json.dumps(self.p))
        self.assertEqual(parsed, self.p)
        self.assertFalse(validate(parsed)["training_authorized"])

    def test_default_is_explicitly_blocked(self):
        report = validate(self.p)
        self.assertEqual(report["missing_evidence_count"], 15)
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["eligible_for_model_promotion"])
        self.assertFalse(report["rights_and_consent_verified"])

    def test_refuses_execution_download_and_publication(self):
        for field in ("execution_authorized", "download_authorized", "publish_weights_authorized"):
            with self.subTest(field=field):
                p = copy.deepcopy(self.p)
                p[field] = True
                with self.assertRaisesRegex(ProposalError, field):
                    validate(p)

    def test_rejects_ambiguous_bool_numeric_fields(self):
        for field in ("seed", "rank", "epochs", "compute_budget_usd"):
            with self.subTest(field=field):
                p = copy.deepcopy(self.p)
                p[field] = True
                with self.assertRaises(ProposalError):
                    validate(p)

    def test_no_spend_or_unknown_fields(self):
        p = copy.deepcopy(self.p)
        p["compute_budget_usd"] = 1
        with self.assertRaisesRegex(ProposalError, "zero-dollar"):
            validate(p)
        p = copy.deepcopy(self.p)
        p["api_key"] = "secret"
        with self.assertRaisesRegex(ProposalError, "exactly"):
            validate(p)

    def test_invalid_pins_and_receipts(self):
        for field, value in (("base_revision_full_commit_sha", "main"),
                             ("dataset_sha256", "not-a-hash"),
                             ("base_model", "../../private"),
                             ("sealed_holdout_receipt", {"leaked": "answer"}),
                             ("target_modules", ["q_proj", "q_proj"])):
            with self.subTest(field=field):
                p = copy.deepcopy(self.p)
                p[field] = value
                with self.assertRaisesRegex(ProposalError, "invalid " + field):
                    validate(p)

    def test_rejects_same_train_validation_split(self):
        p = copy.deepcopy(self.p)
        p["train_split_sha256"] = "a" * 64
        p["validation_split_sha256"] = "a" * 64
        with self.assertRaisesRegex(ProposalError, "must differ"):
            validate(p)

    def test_populated_metadata_never_proves_rights_or_readiness(self):
        p = copy.deepcopy(self.p)
        for field in ("dataset_sha256", "train_split_sha256", "validation_split_sha256",
                      "checkpoint_artifact_sha256", "rollback_artifact_sha256"):
            p[field] = ("b" if field == "validation_split_sha256" else "a") * 64
        p["base_model"] = "ExampleOrg/ExampleModel"
        p["base_revision_full_commit_sha"] = "c" * 40
        p["target_modules"] = ["q_proj", "v_proj"]
        for field in ("base_license_and_notice_review_receipt",
                      "dataset_consent_and_rights_receipt", "sealed_holdout_receipt",
                      "hardware_and_memory_preflight_receipt", "baseline_evaluation_receipt",
                      "post_training_evaluation_receipt", "human_release_approval_receipt"):
            p[field] = "review/receipt-123"
        report = validate(p)
        self.assertEqual(report["missing_evidence_count"], 0)
        self.assertFalse(report["evidence_contents_verified"])
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["model_quality_verified"])


if __name__ == "__main__":
    unittest.main()
