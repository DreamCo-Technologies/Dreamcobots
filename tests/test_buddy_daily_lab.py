import unittest
from buddy.certification.daily_lab import inspect

def row(name="one", kind="tool"):
    return {"id": name, "kind": kind, "contract": "input -> output", "version": "v1", "inputs": [], "outputs": []}

class DailyLabTests(unittest.TestCase):
    def test_unknown_not_mastered(self):
        x = inspect([row()])
        self.assertEqual(x["counts"]["verified"], 0)
        self.assertFalse(x["results"][0]["training_executed"])
        self.assertIsNone(x["results"][0]["frontier_gaps"])

    def test_duplicate_contract(self):
        x = inspect([row("one"), row("two")])
        self.assertEqual(x["counts"]["duplicates"], 1)
        self.assertEqual(x["results"][1]["duplicate_of"], "one")

    def test_different_kinds_not_duplicates(self):
        x = inspect([row("one"), row("two", "workflow")])
        self.assertEqual(x["counts"]["duplicates"], 0)

    def test_reject_unsupported_kind(self):
        with self.assertRaises(ValueError):
            inspect([row(kind="anything")])

    def test_unverified_frontier_does_not_count(self):
        x = inspect([row()], observations={"one": {"scores":{"correctness":1}}},
                    frontier={"one":{"scores":{"correctness":1}}})
        self.assertFalse(x["results"][0]["frontier_comparable"])

if __name__ == "__main__":
    unittest.main()
