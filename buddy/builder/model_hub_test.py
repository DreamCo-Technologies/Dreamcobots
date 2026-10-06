import unittest

from buddy.builder.model_hub import approve


class ModelHubTest(unittest.TestCase):
    def test_approval_does_not_download(self) -> None:
        report = approve("open-weight", True)
        self.assertTrue(report["approved"])
        self.assertFalse(report["weights_downloaded"])
        self.assertFalse(report["frontier_claim"])


if __name__ == "__main__":
    unittest.main()
