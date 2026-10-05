import unittest

from buddy.learning.interaction_learning import InteractionLedger, picker
from buddy.learning.permissioned_views import PermissionError, grant
from benchmarks.hf_model_ranker.category_sandbox import probe
from benchmarks.hf_model_ranker.rank import load_catalog


class InteractionAndCategoryTest(unittest.TestCase):
    def test_user_course_and_video_need_several_angles(self) -> None:
        ledger = InteractionLedger()
        grants = [grant("train", "buddy-a", True)]
        ledger.record("user", "buddy-a", "chat", "use one model")
        with self.assertRaises(PermissionError):
            ledger.perspective("buddy-a", grants)
        ledger.record("course", "buddy-a", "https://example.edu/course", "compare sources", "agree")
        ledger.record("youtube", "buddy-a", "https://www.youtube.com/watch?v=example", "show the conflict", "conflict")
        report = ledger.perspective("buddy-a", grants)
        self.assertGreaterEqual(report["views"], 3)
        self.assertFalse(report["copied_media"])

    def test_picker_shows_weights_and_every_category_is_sandboxed(self) -> None:
        catalog = load_catalog()
        shown = picker(catalog)
        self.assertEqual(shown["shown"], len(catalog["models"]))
        self.assertFalse(shown["downloaded"])
        report = probe(catalog)
        self.assertGreaterEqual(report["categories"], 25)
        self.assertEqual(report["failed"], 0)
        self.assertFalse(report["weights_downloaded"])


if __name__ == "__main__":
    unittest.main()
