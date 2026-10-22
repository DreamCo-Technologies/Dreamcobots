import unittest
from buddy.bootcamp.training_methods_hub import METHODS, PROVIDERS
from buddy.bootcamp.training_taxonomy import CATEGORIES, PROVIDER_CATEGORIES, BootcampQuery, lesson, search

class TrainingTaxonomyTests(unittest.TestCase):
    def test_all_methods_categorized(self):
        self.assertEqual(set(METHODS), {name for values in CATEGORIES.values() for name in values})

    def test_all_providers_categorized(self):
        self.assertEqual(set(PROVIDERS), {name for values in PROVIDER_CATEGORIES.values() for name in values})

    def test_tokenization_search(self):
        result = search(BootcampQuery(category="tokenization_vocabulary"))
        self.assertEqual({m["id"] for m in result["methods"]}, {"tokenizer_training", "continued_pretraining"})

    def test_free_filter_and_source_status(self):
        result = search(BootcampQuery(free_only=True))
        self.assertTrue(result["providers"])
        self.assertTrue(all(not x["live_access_verified"] for x in result["providers"]))
        self.assertFalse(any(x["id"] == "runpod" for x in result["providers"]))

    def test_lessons_are_reviewable_not_executed(self):
        result = lesson("qlora", "intermediate")
        self.assertEqual(result["assessment"]["status"], "not_attempted")
        self.assertFalse(result["training_executed"])

    def test_invalid_filters(self):
        with self.assertRaises(ValueError):
            search(BootcampQuery(category="nonexistent"))
        with self.assertRaises(ValueError):
            lesson("nonexistent")

if __name__ == "__main__":
    unittest.main()
