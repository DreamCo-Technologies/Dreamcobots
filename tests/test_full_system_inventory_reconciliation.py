"""Synthetic, offline inventory-consistency regressions; not bot-readiness tests."""
import copy
import unittest

from tools.build_full_system_certification import unified_inventory_consistent


def example():
    canonical = [{'slug': 'alpha'}, {'slug': 'beta'}]
    supplemental = [{'slug': 'gamma'}]
    unified = {
        'canonical_bots': canonical + supplemental,
        'legacy_candidates': [],
        'canonical_bot_count': 3,
        'legacy_pending_candidate_count': 0,
        'total_accounted_worker_records': 3,
    }
    accounting = {
        'canonical_profiles': canonical,
        'supplemental_profiles': supplemental,
        'canonical_bot_count': 2,
        'supplemental_bot_count': 1,
        'total_profile_count': 3,
        'accounting_complete': True,
        'duplicate_slugs': [],
        'declared_total_mismatches': [],
        'supplemental_division_mismatches': [],
    }
    return copy.deepcopy(unified), copy.deepcopy(accounting)


class InventoryConsistencyTests(unittest.TestCase):
    def test_expanded_inventory_matches_accounting(self):
        self.assertTrue(unified_inventory_consistent(*example()))

    def test_duplicate_unified_id_is_rejected(self):
        u, a = example()
        u['canonical_bots'][2]['slug'] = 'alpha'
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_duplicate_across_cohorts_is_rejected(self):
        u, a = example()
        a['supplemental_profiles'][0]['slug'] = 'alpha'
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_missing_supplemental_profile_is_rejected(self):
        u, a = example()
        a['supplemental_profiles'] = []
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_mismatched_unified_count_is_rejected(self):
        u, a = example()
        u['canonical_bot_count'] = 1051
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_boolean_count_is_rejected(self):
        u, a = example()
        u['canonical_bot_count'] = True
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_unaccounted_pending_candidate_is_rejected(self):
        u, a = example()
        u['legacy_candidates'].append({'slug': 'pending'})
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_malformed_pending_candidate_is_rejected(self):
        u, a = example()
        u['legacy_candidates'] = [None]
        u['legacy_pending_candidate_count'] = 1
        u['total_accounted_worker_records'] = 4
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_accounting_not_complete_is_rejected(self):
        u, a = example()
        a['accounting_complete'] = False
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_duplicate_flag_is_rejected(self):
        u, a = example()
        a['duplicate_slugs'] = ['alpha']
        self.assertFalse(unified_inventory_consistent(u, a))

    def test_malformed_or_empty_records_are_rejected(self):
        u, a = example()
        self.assertFalse(unified_inventory_consistent({}, a))
        self.assertFalse(unified_inventory_consistent(u, None))

    def test_unique_new_supplemental_profile_is_supported(self):
        u, a = example()
        u['canonical_bots'].append({'slug': 'delta'})
        u['canonical_bot_count'] += 1
        u['total_accounted_worker_records'] += 1
        a['supplemental_profiles'].append({'slug': 'delta'})
        a['supplemental_bot_count'] += 1
        a['total_profile_count'] += 1
        self.assertTrue(unified_inventory_consistent(u, a))


if __name__ == '__main__':
    unittest.main()
