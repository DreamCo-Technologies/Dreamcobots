import unittest
from buddy.bootcamp.resource_categories import (
    CATEGORIES, STUDY_PATHS, bootcamp_path, search_resources, validate_taxonomy,
)

class ResourceCategoryTests(unittest.TestCase):
    def test_complete_unique_coverage(self):
        self.assertTrue(validate_taxonomy())
        self.assertEqual(len(search_resources()), 12)

    def test_free_notebook_filter(self):
        ids = {r["id"] for r in search_resources(category="free_gpu_notebooks", cost="free")}
        self.assertEqual(ids, {"colab", "kaggle"})

    def test_topic_search(self):
        self.assertIn("pytorch", {r["id"] for r in search_resources("autograd")})
        self.assertEqual(search_resources("not-a-real-topic"), [])

    def test_paid_marketplaces(self):
        self.assertEqual({r["id"] for r in search_resources(category="gpu_marketplaces", cost="paid")},
                         {"runpod", "vast"})

    def test_study_paths(self):
        self.assertIn("train_vocabulary", STUDY_PATHS)
        plan = bootcamp_path("train_vocabulary")
        self.assertFalse(plan["training_started"])
        self.assertTrue(plan["requires_user_selection"])

    def test_invalid_categories(self):
        with self.assertRaises(ValueError):
            search_resources(category="does-not-exist")
        with self.assertRaises(ValueError):
            bootcamp_path("does-not-exist")

if __name__ == "__main__":
    unittest.main()
