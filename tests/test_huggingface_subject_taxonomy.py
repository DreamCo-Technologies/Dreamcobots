import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.discover_huggingface_subject_taxonomy import plain, values_under


class FakeHub:
    def get_model_tags(self):
        return {"pipeline_tags": [{"id": "text-generation"}, {"id": "image-classification"}]}

    def get_dataset_tags(self):
        return {"task_categories": [{"label": "audio-classification"}]}

    def get_space_tags(self):
        return {"tags": [{"id": "gradio"}, {"id": "computer-vision"}]}


class FakeHubWithoutSpaces:
    def get_model_tags(self):
        return {"pipeline_tags": [{"id": "text-generation"}]}

    def get_dataset_tags(self):
        return {"task_categories": [{"label": "audio-classification"}]}


class HuggingFaceTaxonomyTests(unittest.TestCase):
    def test_plain_and_recursive_taxonomy_extraction(self):
        payload = {"pipeline_tags": [{"id": "text-generation"}], "nested": {"task_categories": ["audio"]}}
        self.assertEqual(plain(payload), payload)
        found = values_under(payload, {"pipeline_tags", "task_categories"})
        self.assertIn("text-generation", found)
        self.assertIn("audio", found)

    def test_refresh_includes_models_datasets_and_spaces(self):
        import sys
        import types
        fake_module = types.SimpleNamespace(HfApi=FakeHub)
        with tempfile.TemporaryDirectory() as temp, patch.dict(sys.modules, {"huggingface_hub": fake_module}), patch("sys.argv", ["discover", "--out", str(Path(temp) / "taxonomy.json")]):
            from tools.discover_huggingface_subject_taxonomy import main
            self.assertEqual(main(), 0)
            result = json.loads((Path(temp) / "taxonomy.json").read_text())
        self.assertIn("text-generation", result["subject_terms"])
        self.assertIn("audio-classification", result["subject_terms"])
        self.assertIn("computer-vision", result["subject_terms"])
        self.assertEqual(result["counts"]["space_subject_terms"], 2)
        self.assertTrue(result["capabilities"]["spaces"])

    def test_missing_spaces_taxonomy_is_reported_not_hidden(self):
        import sys
        import types
        fake_module = types.SimpleNamespace(HfApi=FakeHubWithoutSpaces)
        with tempfile.TemporaryDirectory() as temp, patch.dict(sys.modules, {"huggingface_hub": fake_module}), patch("sys.argv", ["discover", "--out", str(Path(temp) / "taxonomy.json")]):
            from tools.discover_huggingface_subject_taxonomy import main
            self.assertEqual(main(), 0)
            result = json.loads((Path(temp) / "taxonomy.json").read_text())
        self.assertFalse(result["capabilities"]["spaces"])
        self.assertIn("spaces_taxonomy_unavailable", result["status"])


if __name__ == "__main__":
    unittest.main()
