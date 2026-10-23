import tempfile
import unittest
from pathlib import Path
from buddy.certification.repository_discovery import discover
from buddy.certification.model_benchmarks import Task, FixtureAdapter, benchmark
from buddy.certification.training_gate import evaluate_training

class DiscoveryBenchmarksTests(unittest.TestCase):
    def test_static_discovery(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "demo.py").write_text("def hello(): return 1\nclass Thing: pass\n")
            x = discover(p)
            self.assertEqual(x["counts"]["symbols"], 2)
            self.assertTrue(all(y["status"] == "discovered_not_tested" for y in x["items"]))

    def test_excludes_vendor(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "node_modules"
            p.mkdir()
            (p / "hidden.py").write_text("def ignored(): pass\n")
            self.assertEqual(discover(Path(d))["counts"]["symbols"], 0)

    def test_model_requires_approval(self):
        with self.assertRaises(PermissionError):
            benchmark([Task("a", "hi", "hi")], [FixtureAdapter()], dataset_rights="owned")

    def test_repeatable_task_hash(self):
        args = ([Task("a", "hi", "hi")], [FixtureAdapter()])
        x = benchmark(*args, dataset_rights="owned", approved=True)
        y = benchmark(*args, dataset_rights="owned", approved=True)
        self.assertEqual(x["task_set_hash"], y["task_set_hash"])
        self.assertEqual(x["results"][0]["accuracy"], 1.0)
        self.assertFalse(x["results"][0]["independent_verified"])

    def test_training_not_launched(self):
        x = evaluate_training({"owner_approved": True})
        self.assertFalse(x["ready_for_review"])
        self.assertFalse(x["training_started"])

if __name__ == "__main__":
    unittest.main()
