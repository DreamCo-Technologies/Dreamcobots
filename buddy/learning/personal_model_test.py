import unittest

from buddy.learning.permissioned_views import PermissionError, grant
from buddy.learning.personal_model import add_source, personal_model


class PersonalModelTest(unittest.TestCase):
    def test_own_model_needs_permission_and_three_sources(self) -> None:
        grants = [grant("train", "user-buddy", True)]
        sources = [
            add_source("internet", "user-buddy", "https://example.com/article", "cite the source"),
            add_source("book", "user-buddy", "Author, Example Book", "compare the claim"),
            add_source("youtube", "user-buddy", "https://www.youtube.com/watch?v=example", "keep the conflict"),
        ]
        report = personal_model("user-buddy", sources, grants)
        self.assertTrue(report["own_model"])
        self.assertFalse(report["weights_downloaded"])
        with self.assertRaises(PermissionError):
            personal_model("user-buddy", sources, [])


if __name__ == "__main__":
    unittest.main()
