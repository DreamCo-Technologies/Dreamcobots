"""Synthetic development-grader checks; no model inference or hidden holdouts."""
import copy
import json
import unittest

from tools.score_buddy_dev_fixtures import PINNED, score_dev_responses


def catalog():
    return {"schema": "dreamco.buddy_model_benchmarks.v1",
            "suites": [{"id": k, **copy.deepcopy(v)} for k, v in PINNED.items()]}


class PublicDevelopmentSmokeTests(unittest.TestCase):
    def test_three_public_fixtures_pass_without_claiming_model_quality(self):
        rows = [
            {"suite_id": "structured_output", "response": '{"result":42,"confidence":0.5}'},
            {"suite_id": "instruction_following", "response": "READY"},
            {"suite_id": "arithmetic_reasoning", "response": "42"},
        ]
        report = score_dev_responses(rows, catalog())
        self.assertEqual(report["passed_public_dev_fixtures"], 3)
        self.assertEqual(report["model_calls"], 0)
        self.assertFalse(report["model_quality_verified"])
        self.assertFalse(report["eligible_for_model_promotion"])
        self.assertEqual(report["independent_holdout_receipts"], 0)
        self.assertNotIn("READY", json.dumps(report))
        self.assertNotIn("confidence", json.dumps(report))

    def test_incorrect_answers_are_not_counted(self):
        rows = [
            {"suite_id": "instruction_following", "response": "Ready"},
            {"suite_id": "arithmetic_reasoning", "response": "42 items"},
            {"suite_id": "structured_output", "response": '{"result":43,"confidence":0.9}'},
        ]
        self.assertEqual(score_dev_responses(rows, catalog())["passed_public_dev_fixtures"], 0)

    def test_structured_output_rejects_bool_nonfinite_and_extra_fields(self):
        for answer in (
            '{"result":true,"confidence":0.5}',
            '{"result":42,"confidence":NaN}',
            '{"result":42,"confidence":2}',
            '{"result":42,"confidence":0.5,"private":"value"}',
            'not json',
        ):
            with self.subTest(answer=answer):
                result = score_dev_responses([{"suite_id": "structured_output", "response": answer}], catalog())
                self.assertEqual(result["passed_public_dev_fixtures"], 0)

    def test_structured_output_rejects_duplicate_json_keys(self):
        # Default json.loads silently keeps the last value, so an ambiguous
        # result could otherwise be incorrectly graded as passing.
        for answer in (
            '{"result":43,"result":42,"confidence":0.5}',
            '{"result":42,"confidence":0.9,"confidence":0.5}',
            '{"result":42,"confidence":0.5,"metadata":{"x":1,"x":2}}',
        ):
            with self.subTest(answer=answer):
                report = score_dev_responses(
                    [{"suite_id": "structured_output", "response": answer}], catalog()
                )
                self.assertEqual(report["passed_public_dev_fixtures"], 0)

    def test_changed_fixture_fails_closed(self):
        data = catalog()
        data["suites"][0]["prompt_fixture"] = "Different public prompt"
        with self.assertRaisesRegex(ValueError, "fixture changed"):
            score_dev_responses([{"suite_id": "instruction_following", "response": "READY"}], data)

    def test_duplicate_or_unsupported_suites_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate development"):
            score_dev_responses([{"suite_id": "instruction_following", "response": "READY"}] * 2, catalog())
        with self.assertRaisesRegex(ValueError, "unsupported"):
            score_dev_responses([{"suite_id": "hidden_test", "response": "leak"}], catalog())

    def test_extra_metadata_or_raw_private_fields_fail(self):
        with self.assertRaisesRegex(ValueError, "only suite_id and response"):
            score_dev_responses([{"suite_id": "instruction_following", "response": "READY", "api_key": "secret"}], catalog())

    def test_response_text_and_digest_are_not_persisted(self):
        report = score_dev_responses(
            [{"suite_id": "instruction_following", "response": "private-example-123"}],
            catalog(),
        )
        serialized = json.dumps(report)
        self.assertNotIn("private-example-123", serialized)
        self.assertNotIn("response_sha256", serialized)

    def test_invalid_unicode_rejected_as_input_error(self):
        with self.assertRaisesRegex(ValueError, "valid UTF-8"):
            score_dev_responses(
                [{"suite_id": "instruction_following", "response": "\ud800"}],
                catalog(),
            )

    def test_workflow_includes_scorer_and_its_tests_in_path_filters(self):
        from pathlib import Path

        workflow = (
            Path(__file__).resolve().parents[1]
            / ".github/workflows/buddy-teacher-coverage-audit.yml"
        ).read_text(encoding="utf-8")
        for path in (
            "tools/score_buddy_dev_fixtures.py",
            "tests/test_score_buddy_dev_fixtures.py",
        ):
            with self.subTest(path=path):
                self.assertIn(f'      - "{path}"', workflow)


if __name__ == "__main__":
    unittest.main()
