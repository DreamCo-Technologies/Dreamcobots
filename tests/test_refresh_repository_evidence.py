"""Tests for deterministic convergence of interdependent repository inventories."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import refresh_repository_evidence as refresh


class RepositoryEvidenceRefreshTests(unittest.TestCase):
    def test_prospectuses_repeat_until_both_checks_pass(self):
        calls = []
        state = {"file_generations": 0, "actions_generations": 0}

        def fake_run(*args, check=True):
            calls.append(args)
            if args == ("tools/build_file_prospectus.py",):
                state["file_generations"] += 1
            elif args == ("tools/build_actions_prospectus.py",):
                state["actions_generations"] += 1
            elif args == ("tools/build_file_prospectus.py", "--check"):
                return SimpleNamespace(returncode=0 if state["actions_generations"] >= 2 else 1)
            elif args == ("tools/build_actions_prospectus.py", "--check", "--check-buttons"):
                return SimpleNamespace(returncode=0 if state["file_generations"] >= 2 else 1)
            return SimpleNamespace(returncode=0)

        with patch.object(refresh, "run", side_effect=fake_run):
            attempts = refresh.converge_prospectuses(max_attempts=3)

        self.assertEqual(attempts, 2)
        self.assertEqual(state["file_generations"], 2)
        self.assertEqual(state["actions_generations"], 2)
        self.assertEqual(calls.count(("tools/build_file_prospectus.py", "--check")), 2)
        self.assertEqual(
            calls.count(("tools/build_actions_prospectus.py", "--check", "--check-buttons")),
            2,
        )

    def test_non_converging_prospectuses_fail_closed(self):
        def fake_run(*args, check=True):
            if "--check" in args:
                return SimpleNamespace(returncode=1)
            return SimpleNamespace(returncode=0)

        with patch.object(refresh, "run", side_effect=fake_run):
            with self.assertRaises(SystemExit):
                refresh.converge_prospectuses(max_attempts=2)


if __name__ == "__main__":
    unittest.main()
