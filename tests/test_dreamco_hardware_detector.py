import unittest
from unittest.mock import patch
from scripts.dreamco_hardware_detector import detect

class HardwareDetectorTests(unittest.TestCase):
    def test_report_is_advisory_and_never_starts_training(self):
        with patch.dict("sys.modules", {"torch": None}):
            result = detect()
        self.assertEqual(result["schema"], "dreamco.hardware_preflight.v1")
        self.assertTrue(result["selection_is_advisory"])
        self.assertFalse(result["training_started"])
        self.assertIn("candidate_tiers", result)

if __name__ == "__main__":
    unittest.main()
