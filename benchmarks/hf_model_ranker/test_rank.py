import unittest

from benchmarks.hf_model_ranker.rank import load_catalog, rank


class HuggingFaceModelRankerTest(unittest.TestCase):
    def test_catalog_covers_tasks_and_ranks_without_downloads(self) -> None:
        catalog = load_catalog()
        self.assertGreaterEqual(len(catalog["models"]), 80)
        self.assertGreaterEqual(len({row["task"] for row in catalog["models"]}), 25)
        report = rank("code generation", catalog)
        self.assertGreaterEqual(len(report["ranked"]), 2)
        self.assertFalse(report["weights_downloaded"])
        self.assertFalse(report["production_ranked"])
        self.assertGreaterEqual(report["ranked"][0]["score"], report["ranked"][-1]["score"])


if __name__ == "__main__":
    unittest.main()
