import unittest

from tools.validate_checkpoint import finite_positive


class CheckpointMetricValidationTests(unittest.TestCase):
    def test_finite_positive_accepts_valid_metrics(self):
        self.assertEqual(finite_positive(12.5, "tokens_per_second"), 12.5)
        self.assertEqual(finite_positive(0, "peak_vram_mb", allow_zero=True), 0.0)

    def test_zero_and_negative_required_metrics_are_rejected(self):
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    finite_positive(value, "tokens_per_second")

    def test_nan_and_infinity_are_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    finite_positive(value, "validation_perplexity")


if __name__ == "__main__":
    unittest.main()
