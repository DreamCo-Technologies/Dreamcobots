import json, os, sys, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gate"))
from cert_gate import check_card

def load(n):
    with open(os.path.join(ROOT, "examples", n)) as fh: return json.load(fh)

class TestCertGate(unittest.TestCase):
    def test_valid_f2(self):
        ok, r = check_card(load("valid_certified_f2.json")); self.assertTrue(ok, r)
    def test_valid_f4(self):
        ok, r = check_card(load("valid_certified_f4.json")); self.assertTrue(ok, r)
    def _bad(self, n, needle):
        ok, r = check_card(load(n)); self.assertFalse(ok); self.assertTrue(any(needle in x for x in r), r)
    def test_no_benches(self): self._bad("invalid_cert_no_benches.json", "no bench results")
    def test_overclaim(self): self._bad("invalid_overclaim_f3.json", "exceeds evidence-supported floor F2")
    def test_leakage(self): self._bad("invalid_leakage_failed.json", "leakage check not passed")
    def test_missing_ref(self): self._bad("invalid_missing_evidence_ref.json", "ghost does not resolve")
    def test_f4_too_soon(self): self._bad("invalid_f4_retest_too_soon.json", ">= 30 days")
    def test_f4_self_graded(self): self._bad("invalid_f4_self_graded.json", "independent of issuer")
    def test_schema(self):
        try: import jsonschema
        except ImportError: self.skipTest("jsonschema not installed")
        with open(os.path.join(ROOT, "schema", "course_evidence_card.schema.json")) as fh: s = json.load(fh)
        for n in os.listdir(os.path.join(ROOT, "examples")):
            if n.endswith(".json"): jsonschema.validate(load(n), s)

if __name__ == "__main__": unittest.main()
