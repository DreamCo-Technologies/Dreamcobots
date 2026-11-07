import unittest
from buddy.bootcamp.provider_learning_libraries import LIBRARIES, catalog, search, validate

class ProviderLearningLibrariesTests(unittest.TestCase):
    def test_all_twelve_have_libraries(self):
        self.assertTrue(validate())
        self.assertEqual(len(catalog()), 12)
        self.assertTrue(all(item["resources"] for item in catalog()))

    def test_search_by_provider(self):
        items = search(provider="hugging_face")
        self.assertGreaterEqual(len(items), 3)
        self.assertTrue(all(row["provider_id"] == "hugging_face" for row in items))

    def test_search_by_topic(self):
        items = search(topic="autograd")
        self.assertTrue(any(row["provider_id"] == "pytorch" for row in items))

    def test_beginner_filter(self):
        items = search(level="beginner")
        self.assertTrue(items)
        self.assertTrue(all(row["level"] == "beginner" for row in items))

    def test_unknown_provider(self):
        with self.assertRaises(ValueError):
            search(provider="unknown")

    def test_not_claimed_live(self):
        self.assertTrue(all(not row["verified_live"] for item in catalog()
                            for row in item["resources"]))

if __name__ == "__main__":
    unittest.main()
