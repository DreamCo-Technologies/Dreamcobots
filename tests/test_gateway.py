"""Focused tests for explicit, server-side BuddyGateway configuration."""
from __future__ import annotations

import os
import unittest
from unittest import mock

from buddy.openrouter.gateway import BuddyGateway, ClientPolicy


class BuddyGatewayTests(unittest.TestCase):
    def test_explicit_credentials_do_not_require_mutating_process_environment(self):
        policy = ClientPolicy(client_id="gateway-test", allowed_models=frozenset())
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "process-key"}):
            gateway = BuddyGateway(
                policy,
                api_key="injected-test-key",
                base_url="https://gateway.example.test/v1",
            )

        self.assertEqual(gateway.api_key, "injected-test-key")
        self.assertEqual(gateway.base_url, "https://gateway.example.test/v1")

    def test_missing_explicit_or_environment_key_fails_closed(self):
        policy = ClientPolicy(client_id="gateway-test", allowed_models=frozenset())
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENROUTER_API_KEY"):
                BuddyGateway(policy)


if __name__ == "__main__":
    unittest.main()
