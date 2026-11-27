"""Synthetic tests: receipt shape is never evidence of actual model quality."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.validate_buddy_evaluation_receipt import (
    MAX_BYTES, ReceiptError, parse_receipt, read_receipt, validate,
)


def example():
    return {
        "schema": "dreamco.buddy_evaluation_receipt_preflight.v1",
        "evaluation_id": "fictional_eval_0001",
        "model_revision_sha": "a" * 40,
        "checkpoint_sha256": "b" * 64,
        "dataset_manifest_sha256": "c" * 64,
        "holdout_set_sha256": "d" * 64,
        "independent_evaluator_receipt_id": None,
        "dataset_rights_receipt_id": None,
        "contains_raw_examples": False,
        "training_authorized": False,
        "promotion_authorized": False,
        "samples_evaluated": 0,
        "samples_correct": 0,
        "failed_safety_cases": 0,
        "median_latency_ms": None,
        "p95_latency_ms": None,
    }


class ReceiptPreflightTests(unittest.TestCase):
    def test_empty_proposal_is_not_training_or_promotion_evidence(self):
        report = validate(example())
        self.assertEqual(report["model_calls_performed_by_preflight"], 0)
        self.assertFalse(report["evaluator_independence_verified"])
        self.assertFalse(report["holdout_integrity_verified"])
        self.assertFalse(report["model_quality_verified"])
        self.assertFalse(report["eligible_for_model_promotion"])
        self.assertEqual(len(report["missing_receipt_references"]), 2)

    def test_self_reported_scores_do_not_promote_even_with_receipt_ids(self):
        data = example()
        data.update(
            samples_evaluated=10, samples_correct=10, failed_safety_cases=0,
            median_latency_ms=12.5, p95_latency_ms=19.0,
            independent_evaluator_receipt_id="fictional_evaluator_001",
            dataset_rights_receipt_id="fictional_rights_001",
        )
        report = validate(data)
        self.assertEqual(report["reported_samples_evaluated"], 10)
        self.assertEqual(report["missing_receipt_references"], [])
        self.assertFalse(report["model_quality_verified"])
        self.assertFalse(report["dataset_rights_verified"])
        self.assertFalse(report["eligible_for_model_promotion"])
        self.assertNotIn("fictional_evaluator_001", json.dumps(report))

    def test_rejects_raw_examples_and_unsafe_flags(self):
        for key in ("contains_raw_examples", "training_authorized", "promotion_authorized"):
            for bad in (True, 0, "false", None):
                with self.subTest(key=key, bad=bad):
                    data = example()
                    data[key] = bad
                    with self.assertRaises(ReceiptError):
                        validate(data)
        data = example()
        data["prompt"] = "do not store private holdout questions"
        with self.assertRaises(ReceiptError):
            validate(data)

    def test_rejects_bad_counts_and_latency(self):
        for key, value in (
            ("samples_evaluated", True), ("samples_evaluated", -1),
            ("samples_evaluated", 1000001), ("samples_correct", 1),
            ("failed_safety_cases", 1), ("samples_correct", 0.1),
            ("median_latency_ms", 1), ("p95_latency_ms", 1),
        ):
            with self.subTest(key=key, value=value):
                data = example()
                data[key] = value
                with self.assertRaises(ReceiptError):
                    validate(data)
        data = example()
        data.update(samples_evaluated=1, median_latency_ms=20, p95_latency_ms=10)
        with self.assertRaises(ReceiptError):
            validate(data)

    def test_rejects_bad_hashes_ids_and_duplicate_hashes(self):
        for key, value in (
            ("model_revision_sha", "not-a-commit"),
            ("checkpoint_sha256", "B" * 64),
            ("holdout_set_sha256", "b" * 64),
            ("evaluation_id", "has spaces"),
            ("independent_evaluator_receipt_id", "https://example.test/private"),
            ("dataset_rights_receipt_id", 123),
        ):
            with self.subTest(key=key):
                data = example()
                data[key] = value
                with self.assertRaises(ReceiptError):
                    validate(data)

    def test_strict_json_and_bounded_read(self):
        raw = json.dumps(example())
        self.assertEqual(validate(parse_receipt(raw))["reported_samples_evaluated"], 0)
        for bad in (
            '{"schema":"x","schema":"y"}',
            raw.replace('"samples_evaluated": 0', '"samples_evaluated": NaN'),
            '{"nested":{"key":1,"key":2}}',
        ):
            with self.subTest(bad=bad[:20]):
                with self.assertRaises(ReceiptError):
                    parse_receipt(bad)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_bytes(b" " * (MAX_BYTES + 1))
            with self.assertRaises(ReceiptError):
                read_receipt(path)
            path.write_bytes(b"\xff")
            with self.assertRaises(ReceiptError):
                read_receipt(path)

    def test_workflow_runs_preflight_tests_and_watches_files(self):
        workflow = (
            Path(__file__).resolve().parents[1]
            / ".github/workflows/buddy-teacher-coverage-audit.yml"
        ).read_text(encoding="utf-8")
        for path in (
            "tools/validate_buddy_evaluation_receipt.py",
            "tests/test_validate_buddy_evaluation_receipt.py",
        ):
            self.assertIn(f'      - "{path}"', workflow)
        self.assertIn("tests.test_validate_buddy_evaluation_receipt", workflow)


if __name__ == "__main__":
    unittest.main()
