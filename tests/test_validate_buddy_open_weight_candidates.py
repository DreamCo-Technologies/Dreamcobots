"""Synthetic tests for research-only open-weight shortlist; no downloads."""
import copy
import json
import unittest
from pathlib import Path

from tools.validate_buddy_open_weight_candidates import CandidateError, parse, validate

REGISTRY = Path(__file__).resolve().parents[1] / "config/buddy-open-weight-candidate-research.json"


class CandidatePreflightTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_current_research_registry_is_blocked(self):
        report = validate(self.data)
        self.assertEqual(report["candidate_count"], 3)
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["commercial_and_derivative_rights_verified"])
        self.assertFalse(report["independent_holdouts_completed"])

    def test_rejects_duplicate_json_keys(self):
        with self.assertRaisesRegex(CandidateError, "duplicate JSON key"):
            parse('{"status":"research_only_no_download_or_training","status":"production"}')

    def test_rejects_nonfinite_json_constants(self):
        with self.assertRaisesRegex(CandidateError, "nonfinite"):
            parse('{"latency":NaN}')

    def test_rejects_duplicate_normalized_model_ids(self):
        p = copy.deepcopy(self.data)
        p["candidates"].append(copy.deepcopy(p["candidates"][0]))
        p["candidates"][-1]["id"] = p["candidates"][0]["id"].upper()
        p["candidates"][-1]["model_card_url"] = "https://huggingface.co/" + p["candidates"][-1]["id"]
        with self.assertRaisesRegex(CandidateError, "duplicate normalized"):
            validate(p)

    def test_rejects_mismatched_model_card_or_unsafe_metadata(self):
        for field, value in (
            ("model_card_url", "https://example.invalid/model"),
            ("advertised_parameter_class", "unknown"),
            ("source_checked_date", "2026-10-25"),
            ("local_latency_ms", 10),
            ("model_trained", True),
            ("production_ready", True),
            ("commercial_rights_reviewed", True),
        ):
            with self.subTest(field=field):
                p = copy.deepcopy(self.data)
                p["candidates"][0][field] = value
                with self.assertRaises(CandidateError):
                    validate(p)

    def test_rejects_training_or_release_authorization(self):
        for field, value in (
            ("selected_for_training", "Qwen/Qwen3-0.6B"),
            ("training_authorized", True),
            ("model_promotion_authorized", True),
            ("release_authorized", True),
        ):
            with self.subTest(field=field):
                p = copy.deepcopy(self.data)
                p["decision"][field] = value
                with self.assertRaises(CandidateError):
                    validate(p)

    def test_rejects_undeclared_fields(self):
        p = copy.deepcopy(self.data)
        p["candidates"][0]["secret"] = "not allowed"
        with self.assertRaisesRegex(CandidateError, "invalid candidate fields"):
            validate(p)


if __name__ == "__main__":
    unittest.main()
