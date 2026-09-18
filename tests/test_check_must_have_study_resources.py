#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.check_must_have_study_resources import main  # noqa: E402


class MustHaveStudyTest(unittest.TestCase):
    def test_one_hundred_unique(self):
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
