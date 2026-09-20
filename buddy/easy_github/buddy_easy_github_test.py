#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from buddy_easy_github import translate_sentence

HERE = Path(__file__).resolve().parent

class EasyGithubTests(unittest.TestCase):
    def test_glossary_loads(self):
        data = json.loads((HERE / "glossary.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["terms"]), 10)

    def test_ticket_phrase(self):
        out = translate_sentence("what's broken")
        self.assertIn("ticket", out["buddy_means"].lower())

    def test_save_phrase(self):
        out = translate_sentence("save my work")
        self.assertIn("commit", out["buddy_means"].lower())

    def test_review_phrase(self):
        out = translate_sentence("review this change")
        self.assertIn("pull request", out["buddy_means"].lower())

if __name__ == "__main__":
    unittest.main()
