import unittest
from buddy.local_core import route
from tools.audit_buddy_independence import build
class LocalIndependenceTests(unittest.TestCase):
    def test_local_core_never_invents_live_data(self):
        self.assertFalse(route('mark Aunt house with a note').external_data_required)
        self.assertTrue(route('find rentals and property history').external_data_required)
        self.assertTrue(route('show current earthquakes').external_data_required)
    def test_audit_separates_local_code_from_authoritative_dependencies(self):
        report=build();self.assertGreater(report['capabilities']['total'],1000);self.assertGreater(report['summary']['implemented_local_components'],0);self.assertGreater(report['summary']['external_authority_or_license_required'],0);self.assertIn('contract_only',report['model_connectors']['by_implementation_status'])
