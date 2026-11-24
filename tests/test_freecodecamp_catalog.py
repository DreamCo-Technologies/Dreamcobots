import json
import unittest

from tools.sync_freecodecamp_catalog import (
    CATEGORIES,
    build_catalog,
    categorize,
    parse_discovery_payload,
    render_catalog,
)


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

    def test_discovery_requires_matching_upstream_playlist_count(self):
        payload = {
            "playlist_count": 2,
            "entries": [
                {"id": "video-a", "title": "Learn Python", "url": "https://www.youtube.com/watch?v=video-a"},
                {"id": "video-b", "title": "Learn SQL", "url": "https://www.youtube.com/watch?v=video-b"},
            ],
        }
        videos, inventory = parse_discovery_payload(payload, "2026.11.23")
        self.assertEqual(len(videos), 2)
        self.assertTrue(inventory["complete"])
        self.assertEqual(inventory["expected_entry_count"], 2)
        self.assertEqual(inventory["observed_entry_count"], 2)

    def test_discovery_rejects_count_mismatch_nulls_and_duplicate_ids(self):
        with self.assertRaisesRegex(RuntimeError, "expected 2 entries"):
            parse_discovery_payload({"playlist_count": 2, "entries": [{"id": "a"}]}, "2026.11.23")
        with self.assertRaisesRegex(RuntimeError, "missing or malformed"):
            parse_discovery_payload({"playlist_count": 1, "entries": [None]}, "2026.11.23")
        with self.assertRaisesRegex(RuntimeError, "duplicate video ID"):
            parse_discovery_payload(
                {"playlist_count": 2, "entries": [{"id": "a"}, {"id": "a"}]},
                "2026.11.23",
            )

    def test_catalog_without_completeness_evidence_is_partial(self):
        catalog = build_catalog([{
            "video_id": "abc123",
            "title": "Learn Python",
            "url": "https://www.youtube.com/watch?v=abc123",
            "categories": categorize("Learn Python"),
            "discovery_source": "public_channel_metadata",
            "rights_status": "review_required",
            "learning_status": "not_studied",
            "all_divisions_foundation": True,
            "duration_seconds": None,
            "upload_date": None,
            "description": "",
        }])
        self.assertEqual(catalog["inventory_status"], "partial")
        self.assertFalse(catalog["inventory"]["complete"])

    def test_catalog_renderer_compacts_video_rows_and_round_trips(self):
        videos = [{
            "video_id": "abc123", "title": "Learn Python",
            "url": "https://www.youtube.com/watch?v=abc123",
            "description": "", "duration_seconds": 42, "upload_date": None,
            "categories": ["python_and_automation"],
            "discovery_source": "public_channel_metadata",
            "rights_status": "review_required", "learning_status": "not_studied",
            "all_divisions_foundation": True,
        }]
        catalog = build_catalog(videos)
        rendered = render_catalog(catalog)
        self.assertEqual(json.loads(rendered), catalog)
        self.assertEqual(sum(line.startswith('    {"video_id"') for line in rendered.splitlines()), 1)

    def test_catalog_truth_and_rights_boundaries(self):
        videos = [{
            "video_id": "abc123",
            "title": "Learn Python",
            "url": "https://www.youtube.com/watch?v=abc123",
            "categories": categorize("Learn Python"),
            "discovery_source": "public_channel_metadata",
            "rights_status": "review_required",
            "learning_status": "not_studied",
            "all_divisions_foundation": True,
            "duration_seconds": None,
            "upload_date": None,
            "description": "",
        }]
        inventory = {
            "enumerator": "yt-dlp",
            "enumerator_version": "2026.11.23",
            "expected_entry_count": 1,
            "observed_entry_count": 1,
            "null_entry_count": 0,
            "duplicate_video_id_count": 0,
            "complete": True,
            "completeness_basis": "test fixture count matches all entries",
        }
        catalog = build_catalog(videos, inventory)
        self.assertEqual(catalog["inventory_status"], "complete")
        self.assertEqual(catalog["video_count"], 1)
        self.assertEqual(catalog["inventory"]["enumerator_version"], "2026.11.23")
        self.assertFalse(catalog["rights_policy"]["media_download_enabled"])
        self.assertFalse(catalog["rights_policy"]["transcript_ingestion_enabled"])
        self.assertIn("not watched", catalog["truth_boundary"])


if __name__ == "__main__":
    unittest.main()
