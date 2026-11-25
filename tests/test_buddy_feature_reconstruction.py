import unittest
from tools.buddy_feature_reconstruction import create_spec

class FeatureReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.request = {"target":"example editor","authorized":True,"source_type":"documented_api",
                        "license_reviewed":True,"features":["edit text"],
                        "customizations":["custom keyboard shortcuts"]}

    def test_customization_required(self):
        with self.assertRaises(ValueError):
            create_spec({**self.request,"customizations":[]})

    def test_unauthorized_blocked(self):
        with self.assertRaises(PermissionError):
            create_spec({**self.request,"authorized":False})

    def test_proprietary_copy_blocked(self):
        with self.assertRaises(PermissionError):
            create_spec({**self.request,"copy_proprietary_code":True})

    def test_original_brief(self):
        spec = create_spec(self.request)
        self.assertTrue(spec["user_customizations_required"])
        self.assertFalse(spec["production_ready"])

if __name__ == "__main__":
    unittest.main()
