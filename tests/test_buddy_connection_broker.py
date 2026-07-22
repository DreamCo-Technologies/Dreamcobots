from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.connections import (
    AuthMethod,
    BuddyConnectionBroker,
    ConnectionBrokerError,
    ConnectionRequest,
    ConnectorSpec,
    SecretReference,
    SignupRequest,
    TokenKind,
    TokenTransferRequest,
)


def oauth_spec() -> ConnectorSpec:
    return ConnectorSpec(
        connector_id="sample-app",
        display_name="Sample App",
        auth_methods=(AuthMethod.OAUTH_PKCE,),
        allowed_scopes=("profile.read", "items.read", "items.write"),
        high_risk_scopes=("items.write",),
        authorization_endpoint="https://accounts.example.com/oauth/authorize",
        token_endpoint="https://accounts.example.com/oauth/token",
        signup_url="https://accounts.example.com/signup",
        public_client_id="public-client-id",
        supports_signup=True,
    )


class BuddyConnectionBrokerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.broker = BuddyConnectionBroker()

    def test_oauth_pkce_plan_is_scoped_and_hides_verifier(self):
        plan = self.broker.create_connection_plan(
            oauth_spec(),
            ConnectionRequest(
                user_id="owner-1",
                auth_method=AuthMethod.OAUTH_PKCE,
                requested_scopes=("profile.read", "items.write"),
                redirect_uri="https://buddy.example.com/oauth/callback",
            ),
        )
        query = parse_qs(urlsplit(plan.authorization_url or "").query)
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertIn("state", query)
        self.assertIn("pkce_verifier", plan.private_context)
        public = plan.to_public_dict()
        self.assertNotIn("private_context", public)
        self.assertNotIn(plan.private_context["pkce_verifier"], json.dumps(public))
        self.assertTrue(any(gate["id"] == "high_risk_scope_approval" for gate in public["approval_gates"]))

    def test_unknown_scope_and_embedded_credentials_are_rejected(self):
        with self.assertRaisesRegex(ConnectionBrokerError, "allowlist"):
            self.broker.create_connection_plan(
                oauth_spec(),
                ConnectionRequest(
                    user_id="owner-1",
                    auth_method=AuthMethod.OAUTH_PKCE,
                    requested_scopes=("account.admin",),
                    redirect_uri="https://buddy.example.com/oauth/callback",
                ),
            )
        with self.assertRaisesRegex(ConnectionBrokerError, "embedded credentials"):
            ConnectorSpec(
                connector_id="unsafe-app",
                display_name="Unsafe App",
                auth_methods=(AuthMethod.OAUTH_PKCE,),
                authorization_endpoint="https://user:password@example.com/oauth",
                token_endpoint="https://example.com/token",
                public_client_id="client",
            ).validate()

    def test_api_key_flow_accepts_only_secret_references(self):
        spec = ConnectorSpec(
            connector_id="api-service",
            display_name="API Service",
            auth_methods=(AuthMethod.API_KEY,),
            allowed_scopes=("records.read",),
        )
        with self.assertRaisesRegex(ConnectionBrokerError, "secret reference"):
            self.broker.create_connection_plan(
                spec,
                ConnectionRequest(
                    user_id="owner-1",
                    auth_method=AuthMethod.API_KEY,
                    requested_scopes=("records.read",),
                ),
            )
        with self.assertRaisesRegex(ConnectionBrokerError, "never a secret value"):
            SecretReference("managed_vault", "sk_live_1234567890123456").validate()
        with self.assertRaisesRegex(ConnectionBrokerError, "High-entropy"):
            SecretReference("managed_vault", "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6").validate()

        plan = self.broker.create_connection_plan(
            spec,
            ConnectionRequest(
                user_id="owner-1",
                auth_method=AuthMethod.API_KEY,
                requested_scopes=("records.read",),
                secret_ref=SecretReference("environment", "APP_API_KEY"),
            ),
        )
        self.assertEqual(plan.status, "backend_configuration_required")
        self.assertEqual(plan.to_public_dict()["secret_reference"]["value"], "never_collected")

    def test_signup_is_always_an_assisted_user_handoff(self):
        plan = self.broker.create_signup_plan(
            SignupRequest(
                app_name="Example Workspace",
                signup_url="https://app.example.com/signup",
                account_purpose="Manage an approved client project",
            )
        )
        self.assertFalse(plan.submit_allowed)
        self.assertEqual(plan.status, "user_action_required")
        gate_ids = {gate["id"] for gate in plan.user_presence_gates}
        self.assertTrue({"terms_and_privacy", "captcha", "payment", "mfa_or_passkey"} <= gate_ids)
        self.assertEqual(plan.official_origin, "https://app.example.com")

    def test_user_presence_and_high_impact_actions_are_gated(self):
        captcha = self.broker.decide_action("solve_captcha", explicit_user_approval=True)
        self.assertFalse(captcha.allowed)
        self.assertTrue(captcha.requires_user_presence)
        money = self.broker.decide_action("transfer_funds")
        self.assertFalse(money.allowed)
        self.assertEqual(money.status, "approval_required")
        approved = self.broker.decide_action("transfer_funds", explicit_user_approval=True)
        self.assertTrue(approved.allowed)

    def test_token_transfer_is_reference_only_same_audience_and_short_lived(self):
        plan = self.broker.create_token_transfer_plan(
            TokenTransferRequest(
                user_id="owner-1",
                connector_id="client-app",
                token_kind=TokenKind.OAUTH_ACCESS_TOKEN,
                source_ref=SecretReference("environment", "CLIENT_ACCESS_TOKEN"),
                destination_ref=SecretReference("managed_vault", "clients/client-app/access-token"),
                source_audience="https://app.example.com/oauth",
                destination_audience="https://app.example.com/api",
                reason="Move the approved connection into managed storage.",
                scopes=("profile.read",),
                ttl_seconds=60,
                explicit_user_approval=True,
            )
        )
        public = plan.to_public_dict()
        self.assertEqual(public["status"], "backend_vault_execution_required")
        self.assertTrue(public["one_time"])
        self.assertFalse(public["raw_token_accepted"])
        self.assertNotIn("source_locator", str(public))
        self.assertNotIn("CLIENT_ACCESS_TOKEN", str(public))

    def test_token_transfer_blocks_cross_app_and_unwritable_destinations(self):
        base = dict(
            user_id="owner-1",
            connector_id="client-app",
            token_kind=TokenKind.API_TOKEN,
            source_ref=SecretReference("environment", "CLIENT_API_TOKEN"),
            destination_ref=SecretReference("managed_vault", "clients/client-app/api-token"),
            source_audience="https://app.example.com",
            destination_audience="https://other.example.com",
            reason="Move an approved API token.",
        )
        with self.assertRaisesRegex(ConnectionBrokerError, "between app audiences"):
            self.broker.create_token_transfer_plan(TokenTransferRequest(**base))

        base["destination_audience"] = "https://app.example.com"
        base["destination_ref"] = SecretReference("environment", "DESTINATION_API_TOKEN")
        with self.assertRaisesRegex(ConnectionBrokerError, "writable keychain"):
            self.broker.create_token_transfer_plan(TokenTransferRequest(**base))

    def test_registry_generation_stays_in_sync(self):
        result = subprocess.run(
            [sys.executable, "tools/generate_buddy_connection_catalog.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
