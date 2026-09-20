#!/usr/bin/env python3
from __future__ import annotations
import unittest
from beginner_buddy import first_run, load_skills, match, say

class BeginnerBuddyTests(unittest.TestCase):
    def test_two_hundred_skills(self) -> None:
        skills = load_skills()
        self.assertEqual(len(skills), 200)
        ids = [s["id"] for s in skills]
        self.assertEqual(len(ids), len(set(ids)))
        for skill in skills:
            self.assertTrue(skill.get("reply"))
            self.assertTrue(skill.get("triggers"))
            self.assertIn(skill.get("kind"), {"define", "workflow", "explainer", "checklist", "coach"})

    def test_say_new(self) -> None:
        out = say("i'm new")
        self.assertFalse(out["did_change_github"])
        self.assertTrue(out["buddy_says"])

    def test_save_path(self) -> None:
        out = say("save my work")
        self.assertTrue(out["id"].startswith("bf"))
        self.assertIn("save", (out["title"] + out["buddy_says"]).lower())

    def test_error_explainer(self) -> None:
        out = say("permission denied")
        self.assertTrue(out["buddy_says"])

    def test_match_ranks(self) -> None:
        self.assertGreaterEqual(len(match("what's broken")), 1)

    def test_tour(self) -> None:
        tour = first_run()
        self.assertGreaterEqual(len(tour["steps"]), 4)

if __name__ == "__main__":
    unittest.main()
