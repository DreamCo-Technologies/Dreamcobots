import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from buddy.datasets import sources


class ResearchMetadataAdapterTests(unittest.TestCase):
    def test_openalex_returns_metadata_only_references(self):
        response = {"results": [{
            "id": "https://openalex.org/W123",
            "display_name": "A research work",
            "doi": "https://doi.org/10.0000/example",
            "publication_year": 2025,
            "type": "article",
        }]}
        with patch.object(sources, "_get_json", return_value=response) as mocked:
            rows = sources.search_openalex("model training", limit=2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "openalex")
        self.assertEqual(rows[0]["rights_status"], "REFERENCE_METADATA_ONLY_REQUIRES_FULL_TEXT_AND_SUPPLEMENTARY_RIGHTS_REVIEW")
        self.assertIsNone(rows[0]["license"])
        self.assertIn("api.openalex.org/works", mocked.call_args.args[0])
        self.assertFalse(any("content" in row for row in rows))

    def test_crossref_returns_metadata_only_references(self):
        response = {"message": {"items": [{
            "DOI": "10.0000/example",
            "title": ["A scholarly title"],
            "URL": "https://doi.org/10.0000/example",
            "publisher": "Example Publisher",
            "type": "journal-article",
        }]}}
        with patch.object(sources, "_get_json", return_value=response) as mocked:
            rows = sources.search_crossref("model evaluation", limit=4)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "crossref")
        self.assertEqual(rows[0]["id"], "10.0000/example")
        self.assertEqual(rows[0]["rights_status"], "REFERENCE_METADATA_ONLY_REQUIRES_FULL_TEXT_AND_SUPPLEMENTARY_RIGHTS_REVIEW")
        self.assertIsNone(rows[0]["license"])
        query = parse_qs(urlparse(mocked.call_args.args[0]).query)
        self.assertEqual(query["rows"], ["4"])

    def test_discovery_includes_research_metadata_without_approving_training(self):
        with patch.object(sources, "search_huggingface", return_value=[]), \
             patch.object(sources, "search_openml", return_value=[]), \
             patch.object(sources, "search_uci", return_value=[]), \
             patch.object(sources, "search_github", return_value=[]), \
             patch.object(sources, "search_zenodo", return_value=[]), \
             patch.object(sources, "search_datagov", return_value=[]), \
             patch.object(sources, "search_kaggle", return_value=[]), \
             patch.object(sources, "search_openalex", return_value=[{"source":"openalex","id":"W1"}]), \
             patch.object(sources, "search_crossref", return_value=[{"source":"crossref","id":"10.0000/x"}]), \
             patch.object(sources, "search_huggingface_models", return_value=[]):
            result = sources.discover("research", limit=2)
        self.assertEqual({x["source"] for x in result["results"]}, {"openalex", "crossref"})
        self.assertFalse(result["training_approved"])
        self.assertFalse(result["downloaded_files"])


if __name__ == "__main__":
    unittest.main()
