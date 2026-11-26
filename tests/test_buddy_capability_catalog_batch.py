from __future__ import annotations

import unittest

from buddy_os.intelligence.capability_catalog_batch_801_1000 import (
    CAPABILITIES,
    get_capability,
    search_capabilities,
)


class CapabilityCatalogBatchTests(unittest.TestCase):
    def test_batch_contains_exactly_ids_801_through_1000(self):
        self.assertEqual(len(CAPABILITIES), 200)
        self.assertEqual([item.id for item in CAPABILITIES], list(range(801, 1001)))

    def test_lookup_and_search_return_catalog_entries(self):
        self.assertEqual(get_capability(801), CAPABILITIES[0])
        self.assertEqual(get_capability(1000), CAPABILITIES[-1])
        self.assertIsNone(get_capability(1001))
        self.assertTrue(search_capabilities("Bayesian"))
        self.assertTrue(all(item in CAPABILITIES for item in search_capabilities("probabilistic")))


if __name__ == "__main__":
    unittest.main()
