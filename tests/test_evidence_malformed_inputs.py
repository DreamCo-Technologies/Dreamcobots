"""Fail-closed synthetic evidence regression tests; not model mastery evidence."""
from __future__ import annotations

import copy
import unittest

from buddy_os.evaluation.evidence import assess, calibration
from tests.test_general_intelligence import bundle


class MalformedEvidenceTests(unittest.TestCase):
    def test_malformed_json_like_inputs_are_rejected_not_crashes(self):
        mutations = (
            ("unhashable capability", lambda r: r.update(capability=["reasoning"])),
            ("nonnumeric timestamp", lambda r: r.update(timestamp=12345)),
            ("malformed calibration item", lambda r: r.update(calibration=[None])),
            ("calibration object instead of list", lambda r: r.update(calibration={"confidence": 1.0})),
            ("unhashable case split", lambda r: r["cases"][0].update(split=["holdout"])),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                run = bundle()
                mutate(run)
                result = assess(run)
                self.assertFalse(result["eligible"])
                self.assertTrue(result["errors"])

    def test_provenance_and_artifact_paths_require_nonempty_strings(self):
        mutations = (
            ("reviewer list", lambda r: r["license_review"].update(reviewer=["untrusted"])),
            ("reviewer blank", lambda r: r["license_review"].update(reviewer="  ")),
            ("source object", lambda r: r["license_review"].update(source={"url": "fixture"})),
            ("source blank", lambda r: r["license_review"].update(source="  ")),
            ("contamination scope list", lambda r: r["contamination"].update(scope=["fixture"])),
            ("contamination scope blank", lambda r: r["contamination"].update(scope="  ")),
            ("artifact path list", lambda r: r["artifacts"][0].update(path=["trace.json"])),
            ("artifact path blank", lambda r: r["artifacts"][0].update(path="  ")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                run = bundle()
                mutate(run)
                result = assess(run)
                self.assertFalse(result["eligible"])
                self.assertTrue(result["errors"])

    def test_repetition_indices_are_exact_and_preregistered(self):
        for offset in (-3, 10):
            with self.subTest(offset=offset):
                run = copy.deepcopy(bundle())
                for case in run["cases"]:
                    case["repetition"] += offset
                result = assess(run)
                self.assertFalse(result["eligible"])
                self.assertIn("invalid or missing preregistered repetitions", result["errors"])

    def test_calibration_rejects_nonrecord_inputs(self):
        for sample in ([None], [42], {"confidence": 1}, "not-calibration"):
            with self.subTest(sample=sample):
                with self.assertRaises(ValueError):
                    calibration(sample)

    def test_canonical_fixture_still_eligible(self):
        self.assertTrue(assess(bundle())["eligible"])


if __name__ == "__main__":
    unittest.main()
