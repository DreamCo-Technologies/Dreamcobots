"""Tests for DataForgeBot."""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


class TestDataForgeBot(unittest.TestCase):
    """Test cases for DataForgeBot."""

    def setUp(self):
        """Set up test fixtures."""
        from bots.dataforge.dataforge_bot import DataForgeBot
        self.bot = DataForgeBot()

    def test_init(self):
        """Test DataForgeBot initialization."""
        self.assertEqual(self.bot.bot_id, "dataforge-001")
        self.assertEqual(self.bot.bot_name, "DataForge AI Bot")

    def test_collect_from_bots(self):
        """Test that collect_from_bots returns a dict."""
        result = self.bot.collect_from_bots()
        self.assertIsInstance(result, dict)

    def test_generate_synthetic_data(self):
        """Test that synthetic data generation produces correct counts."""
        result = self.bot.generate_synthetic_data()
        self.assertIn("voice", result)
        self.assertIn("facial", result)
        self.assertIn("items", result)
        self.assertIn("behavioral", result)
        self.assertIn("emotion", result)
        self.assertEqual(len(result["voice"]), 100)
        self.assertEqual(len(result["facial"]), 200)
        self.assertEqual(len(result["items"]), 500)

    def test_package_datasets(self):
        """Test that dataset packaging produces output files."""
        self.bot.generate_synthetic_data()
        result = self.bot.package_datasets()
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_list_for_sale(self):
        """Test that list_for_sale returns results for all channels."""
        self.bot.generate_synthetic_data()
        result = self.bot.list_for_sale()
        self.assertIsInstance(result, dict)
        self.assertIn("huggingface_voice", result)


if __name__ == "__main__":
    unittest.main()
