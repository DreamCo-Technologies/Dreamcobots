"""Regression tests for FreeCodeCamp subject keyword boundaries."""

import unittest

from tools.sync_freecodecamp_catalog import categorize


class FreeCodeCampCategoryBoundaryTests(unittest.TestCase):
    def test_javascript_is_not_misclassified_as_java(self):
        categories = categorize("Dates - Beau teaches JavaScript")
        self.assertIn("javascript_and_typescript", categories)
        self.assertNotIn("java_and_jvm", categories)

    def test_java_course_is_classified_as_java(self):
        categories = categorize("Java Programming Full Course")
        self.assertIn("java_and_jvm", categories)

    def test_node_js_does_not_imply_java(self):
        categories = categorize("Build a Node.js API with Express")
        self.assertIn("javascript_and_typescript", categories)
        self.assertNotIn("java_and_jvm", categories)


if __name__ == "__main__":
    unittest.main()
