import unittest
from buddy.genealogy_gedcom import parse_gedcom

SAMPLE = """0 HEAD
1 SOUR DEMO
0 @I1@ INDI
1 NAME Ada /Example/
1 BIRT
2 DATE 1 JAN 1890
1 DEAT
2 DATE 1 JAN 1970
1 SOUR @S1@
0 @I2@ INDI
1 NAME Living /Person/
1 BIRT
2 DATE 1 JAN 2000
0 TRLR
"""

class GedcomTests(unittest.TestCase):
    def test_privacy_default(self):
        result = parse_gedcom(SAMPLE)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["withheld_without_death_evidence"], 1)
        self.assertEqual(result["people"][0]["name"], "Ada /Example/")
        self.assertFalse(result["people"][0]["verified"])

    def test_explicit_include(self):
        self.assertEqual(parse_gedcom(SAMPLE, include_living=True)["count"], 2)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            parse_gedcom("0 @I1@ INDI\n0 @I1@ INDI")

    def test_invalid_rejected(self):
        with self.assertRaises(ValueError):
            parse_gedcom("not gedcom")

    def test_size_limit(self):
        with self.assertRaises(ValueError):
            parse_gedcom("x" * 2_000_001)

    def test_sources(self):
        self.assertEqual(parse_gedcom(SAMPLE)["people"][0]["sources"], ["@S1@"])

if __name__ == "__main__":
    unittest.main()
