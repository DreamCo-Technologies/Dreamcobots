from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.games import BuddyGameLab, GameBuildBrief, GameLabError, LearningDesign


class TinyGame:
    name = "tiny-test-game"
    owner_authorized = True
    sandboxed = True

    def reset(self, seed):
        self.position = seed % 2
        return {"position": self.position}

    def legal_actions(self, _observation):
        return ["advance"]

    def step(self, action):
        self.position += 1
        done = self.position >= 3
        return {"position": self.position}, 1.0, done, {"action_valid": action == "advance"}


class BuddyGameLabTests(unittest.TestCase):
    def test_builds_epic_game_as_verified_milestones(self):
        plan = BuddyGameLab().build_plan(GameBuildBrief(
            title="City of Choices",
            concept="A large open-world civic simulation driven by player decisions and evolving neighborhoods.",
            audience="Adults and college learners",
            target_platforms=("desktop", "console"),
            scope="epic",
            multiplayer=True,
        ))
        self.assertIn("vertical_slice", [phase["phase"] for phase in plan["phases"]])
        self.assertTrue(plan["architecture"]["world_streaming"])
        self.assertTrue(plan["architecture"]["rollback_checkpoints"])
        self.assertIn("multiple approved milestones", plan["scope_truth"])

    def test_builds_teacher_controlled_learning_game(self):
        plan = BuddyGameLab().build_plan(GameBuildBrief(
            title="Fraction Harbor",
            concept="Learners solve fraction comparison challenges to safely guide boats through a harbor.",
            audience="Grades 4 and 5",
            scope="indie",
            learning=LearningDesign(
                learning_objective="Compare fractions with unlike denominators using visual evidence.",
                age_or_level="Grades 4 and 5",
                evidence_of_learning="Three correct explanations across increasing difficulty.",
            ),
        ))
        self.assertIn("misconception report", plan["learning_design"]["teacher_dashboard"])
        self.assertIn("minimal student data", plan["learning_design"]["student_safety"])

    def test_plays_only_through_authorized_sandbox_adapter(self):
        result = BuddyGameLab().play_test(TinyGame(), max_steps=10, seed=2)
        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["policy"]["anti_cheat_bypass"])

        game = TinyGame()
        game.owner_authorized = False
        with self.assertRaisesRegex(GameLabError, "owner-authorized"):
            BuddyGameLab().play_test(game)


if __name__ == "__main__":
    unittest.main()
