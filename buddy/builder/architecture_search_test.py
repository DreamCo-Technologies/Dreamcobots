import unittest

from buddy.builder.architecture_search import METHODS, choose, missing


class ArchitectureSearchTest(unittest.TestCase):
    def test_run_is_off_and_runtime_fields_stay_missing(self) -> None:
        self.assertGreater(len(METHODS), 8)
        report = choose(METHODS[0], False)
        self.assertFalse(report["run"])
        self.assertFalse(report["started"])
        self.assertIn("success_rate", missing({}))


if __name__ == "__main__":
    unittest.main()
