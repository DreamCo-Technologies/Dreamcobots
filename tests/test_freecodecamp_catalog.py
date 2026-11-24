import unittest
from tools.sync_freecodecamp_catalog import CATEGORIES, build_catalog, categorize

class FreeCodeCampCatalogTests(unittest.TestCase):
    def test_taxonomy_has_unique_categories(self):
        ids = [row[0] for row in CATEGORIES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 20)

    def test_video_can_map_to_multiple_subjects(self):
        tags = categorize("Build a RAG AI Agent with Python, PostgreSQL and Docker")
        self.assertIn("python_and_automation", tags)
        self.assertIn("databases_and_sql", tags)
        self.assertIn("generative_ai_and_llms", tags)
        self.assertIn("ai_agents_and_mcp", tags)
        self.assertIn("cloud_devops_and_ci_cd", tags)

    def test_unknown_video_is_preserved_for_manual_review(self):
        self.assertEqual(categorize("A completely new topic"), ["other_or_unclassified"])

    def test_catalog_truth_and_rights_boundaries(self):
        catalog = build_catalog([{
            "video_id": "abc123", "title": "Learn Python", "url": "https://www.youtube.com/watch?v=abc123",
            "categories": categorize("Learn Python"), "discovery_source": "public_channel_metadata",
            "rights_status": "review_required", "learning_status": "not_studied",
            "all_divisions_foundation": True, "duration_seconds": None, "upload_date": None, "description": ""
        }])
        self.assertEqual(catalog["inventory_status"], "complete")
        self.assertEqual(catalog["video_count"], 1)
        self.assertFalse(catalog["rights_policy"]["media_download_enabled"])
        self.assertFalse(catalog["rights_policy"]["transcript_ingestion_enabled"])
        self.assertIn("not watched", catalog["truth_boundary"])

if __name__ == "__main__":
    unittest.main()
