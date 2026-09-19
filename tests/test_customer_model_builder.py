#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from foundry.customer_model_builder import build_plan  # noqa: E402
from tools.build_customer_model_plan import main  # noqa: E402


class CustomerModelBuilderTest(unittest.TestCase):
    def test_three_tracks(self):
        oss = build_plan("open_source")
        ow = build_plan("open_weights")
        fr = build_plan("frontier")
        self.assertTrue(oss["publishes_code"])
        self.assertTrue(ow["publishes_weights"])
        self.assertFalse(fr["publishes_weights"])
        self.assertFalse(oss["trained_weights_exist"])
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
