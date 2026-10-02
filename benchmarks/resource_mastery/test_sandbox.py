import unittest

from benchmarks.resource_mastery.sandbox import ResourceSandbox, discover


class ResourceMasterySandboxTest(unittest.TestCase):
    def test_every_catalog_resource_is_sandboxed(self) -> None:
        resources = discover()
        self.assertGreaterEqual(len(resources), 100)
        report = ResourceSandbox(resources).benchmark()
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["live_calls"], 0)
        self.assertGreater(report["third_party_offered"], 0)
        self.assertTrue(all(row["catalog_mastered"] and not row["production_mastered"] for row in report["results"]))
        self.assertTrue(all(row["third_party_required"] is False for row in report["results"]))


if __name__ == "__main__":
    unittest.main()
