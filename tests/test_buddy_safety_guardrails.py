"""Regression tests for buddy/safety/guardrails.py key-prefix detection.

Key prefixes must start a token, so ordinary hyphenated words such as
"risk-", "task-" or "desk-" are allowed while key-shaped input is refused.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.safety.guardrails import review  # noqa: E402


class GuardrailKeyPrefixTests(unittest.TestCase):
    def test_hyphenated_words_are_not_keys(self):
        for text in ("risk-assessor task-runner desk-chrome", "a disk-image and a mask-layer", "ask-me-anything"):
            self.assertTrue(review(text)["allowed"], text)

    def test_key_shaped_tokens_are_refused(self):
        for text in ("token sk-live123", "key sk-abc123", "token ghp_abc", "use github_pat_abc",
                     "hf_abcdef", "AKIAABCDEFGHIJKLMNOP", "(sk-abc)", "x=hf_abc"):
            self.assertFalse(review(text)["allowed"], text)

    def test_existing_refusals_still_apply(self):
        self.assertFalse(review("please copy gpt weights")["allowed"])
        self.assertTrue(review("sort the mail")["allowed"])


if __name__ == "__main__":
    unittest.main()
