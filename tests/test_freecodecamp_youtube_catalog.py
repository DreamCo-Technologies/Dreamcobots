import unittest
from unittest.mock import patch
from urllib.error import URLError
import traceback
from tools.catalog_freecodecamp_youtube import catalog_all, classify_video, _api_get, YouTubeAPIError


class FreeCodeCampCatalogTests(unittest.TestCase):

    def test_api_key_is_redacted_from_request_errors(self):
        secret = "private-youtube-api-key"
        with patch("tools.catalog_freecodecamp_youtube.urlopen",
                   side_effect=URLError(f"https://www.googleapis.com/youtube/v3/videos?key={secret}")):
            with self.assertRaises(YouTubeAPIError) as caught:
                _api_get("videos", {"part": "snippet"}, secret)
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(secret, "".join(traceback.format_exception(caught.exception)))

    def test_video_gets_multiple_subject_categories(self):
        result = classify_video("Build a Python RAG app with FastAPI", "Learn retrieval augmented generation and REST APIs")
        self.assertIn("python", result["categories"])
        self.assertIn("generative_ai", result["categories"])
        self.assertIn("backend_apis", result["categories"])
        self.assertTrue(result["human_review_required"])

    def test_unknown_video_is_sent_to_review(self):
        result = classify_video("A conversation with a software founder")
        self.assertEqual(result["categories"], ["other_needs_review"])
        self.assertEqual(result["skill_level"], "unknown")

    def test_missing_metadata_is_individually_accounted_for(self):
        responses = [
            {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "uploads123"}}}]},
            {"items": [
                {"contentDetails": {"videoId": "videoA"}},
                {"contentDetails": {"videoId": "videoB"}},
            ]},
            {"items": [
                {"id": "videoA", "snippet": {"title": "Python foundations", "description": "", "publishedAt": "2026-01-01T00:00:00Z", "tags": []}, "contentDetails": {"duration": "PT1H"}}
            ]},
        ]
        with patch("tools.catalog_freecodecamp_youtube._api_get", side_effect=responses):
            result = catalog_all("test-key", sleep_seconds=0)
        self.assertEqual(result["metadata_returned_count"], 1)
        self.assertEqual(result["metadata_unavailable_video_ids"], ["videoB"])
        self.assertTrue(result["metadata_fetch_complete"])
        self.assertTrue(result["catalog_complete"])

    def test_catalog_paginates_and_marks_reference_only(self):
        responses = [
            {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "uploads123"}}}]},
            {"items": [{"contentDetails": {"videoId": "videoA"} }], "nextPageToken": "page2"},
            {"items": [{"contentDetails": {"videoId": "videoB"} }]},
            {"items": [
                {"id": "videoA", "snippet": {"title": "Python for beginners", "description": "Build a Python app", "publishedAt": "2026-01-01T00:00:00Z", "tags": ["python"]}, "contentDetails": {"duration": "PT1H"}},
                {"id": "videoB", "snippet": {"title": "Learn React", "description": "Frontend course", "publishedAt": "2026-02-01T00:00:00Z", "tags": ["react"]}, "contentDetails": {"duration": "PT2H"}}
            ]}
        ]
        with patch("tools.catalog_freecodecamp_youtube._api_get", side_effect=responses):
            result = catalog_all("test-key", sleep_seconds=0)
        self.assertTrue(result["pagination_exhausted"])
        self.assertEqual(result["video_id_count"], 2)
        self.assertEqual(result["metadata_returned_count"], 2)
        self.assertEqual(result["metadata_unavailable_video_ids"], [])
        self.assertTrue(result["metadata_fetch_complete"])
        self.assertTrue(result["catalog_complete"])
        self.assertEqual(result["videos"][0]["content_rights"], "THIRD_PARTY_REFERENCE_ONLY")
        self.assertEqual(result["videos"][0]["training_permission"], "NOT_GRANTED")
        self.assertFalse(result["videos"][0]["video_downloaded"])
        self.assertEqual(result["videos"][1]["transcript_status"], "NOT_FETCHED")


if __name__ == "__main__":
    unittest.main()
