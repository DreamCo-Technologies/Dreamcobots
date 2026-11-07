import unittest
from buddy.certification.engine import validate_manifest, run_suite

class CertificationTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"capabilities": [{"id":"example","domain":"coding","description":"example",
                          "owner":"test","target":"verified","test_module":""}]}

    def test_inventory_does_not_claim_mastery(self):
        r = run_suite(self.manifest, repo_root=".", execute=False)
        self.assertEqual(r["summary"]["independently_verified"], 0)
        self.assertEqual(r["results"][0]["observed"], "unverified")
        self.assertFalse(r["results"][0]["production_certified"])

    def test_duplicate_ids_rejected(self):
        self.manifest["capabilities"].append(dict(self.manifest["capabilities"][0]))
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

    def test_invalid_domain_rejected(self):
        self.manifest["capabilities"][0]["domain"] = "everything"
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

    def test_disallow_untrusted_test_modules(self):
        self.manifest["capabilities"][0]["test_module"] = "os.system"
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

    def test_stable_receipt_digest(self):
        r = run_suite(self.manifest, repo_root=".", execute=False)
        self.assertEqual(len(r["report_sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
