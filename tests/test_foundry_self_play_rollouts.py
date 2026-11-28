"""Offline tests for self-play isolation and candidate validation."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "stages" / "05_model_foundry" / "generate_self_play_rollouts.py"
SPEC = importlib.util.spec_from_file_location("dreamco_selfplay_rollouts", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


class SelfPlayRolloutTests(unittest.TestCase):
    def test_requires_single_python_code_fence(self):
        self.assertEqual(MOD.python_block("```python\ndef answer(): return 42\n```").strip(),
                         "def answer(): return 42")
        with self.assertRaises(ValueError):
            MOD.python_block("def answer(): return 42")

    def test_requires_real_solution_importing_tests(self):
        MOD.validate_tests("import solution\ndef test_answer(): assert solution.answer() == 42")
        with self.assertRaises(ValueError):
            MOD.validate_tests("def test_placeholder(): assert True")
        with self.assertRaises(ValueError):
            MOD.validate_tests("def test_answer(): assert True")

    def test_docker_is_the_only_execution_path(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn('"--network=none"', source)
        self.assertIn('"--read-only"', source)
        self.assertIn('"--cap-drop=ALL"', source)
        self.assertIn("rootless", source)
        self.assertNotIn("subprocess.run([\"python\"", source)

    def test_no_automatic_teachback_or_training_certification(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn('"teach_back_status": "NOT_VERIFIED"', source)
        self.assertIn('"eligible_for_training": False', source)
        self.assertIn('"training_approval": False', source)


if __name__ == "__main__":
    unittest.main()
