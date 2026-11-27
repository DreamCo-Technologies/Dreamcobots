import json
import unittest

from tools.build_dreamco_institute_catalog import build


class DreamCoInstituteCatalogBuildTests(unittest.TestCase):
    def test_generated_payload_matches_canonical_schema_and_scope(self):
        payload = json.loads(build())
        self.assertEqual(payload["schema"], "dreamco.institute.academic_catalog.v1")
        self.assertEqual(len(payload["colleges"]), 5)
        self.assertEqual(len(payload["division_crosswalk"]["academic_assignments"]), 55)


if __name__ == "__main__":
    unittest.main()
