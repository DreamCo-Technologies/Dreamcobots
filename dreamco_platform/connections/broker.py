"""Secure connection planning for Buddy.

The broker prepares standards-based authentication flows without accepting raw
credentials. User-presence actions remain explicit handoffs, and public plan
serialization never exposes PKCE verifiers, tokens, passwords, or secret values.
"""

from __future__ import annotations

import base64
import hashlib
import re
import secrets
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
from urllib.parse import urlencode, urlsplit


class ConnectionBrokerError(ValueError):
    """Raised when a connection request violates the broker contract."""


class AuthMethod(str, Enum):
    OAUTH_PKCE = "oauth_pkce"
    OAUTH_DEVICE = "oauth_device"
    API_KEY = "api_key"
    WEBHOOK_HMAC = "webhook_hmac"
    PASSKEY = "passkey_webauthn"
    BROWSER_HANDOFF = "browser_session_handoff"
    OIDC_SAML = "oidc_saml"
    CUSTOM_REST = "custom_rest"


SECRET_PROVIDERS = {"environment", "os_keychain", "managed_vault"}
SECRET_LOCATOR = re.compile(r"^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$")
TOKEN_LIKE = re.compile(
    r"(?:github_pat_|ghs_|(?:sk|rk)_(?:live|test)_|-----BEGIN .*PRIVATE KEY-----)",
    re.IGNORECASE,
)
USER_PRESENCE_ACTIONS = {
    "accept_terms",
    "confirm_signup",
    "create_passkey",
    "enter_payment",
    "provide_identity",
    "recover_account",
    "solve_captcha",
    "verify_contact",
    "verify_mfa",
}
HIGH_IMPACT_ACTIONS = {
    "delete_account",
    "grant_admin",
    "publish_content",
    "send_message",
    "transfer_funds",
}


def _https_url(value: str, label: str, *, allow_localhost: bool = False) -> str:
    raw = value.strip()
    parsed = urlsplit(raw)
    local = allow_localhost and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if not parsed.netloc or (parsed.scheme != "https" and not (local and parsed.scheme == "http")):
        raise ConnectionBrokerError(f"{label} must be an HTTPS URL.")
    if parsed.username or parsed.password:
        raise ConnectionBrokerError(f"{label} must not contain embedded credentials.")
    return raw


def _pkce_value(size: int = 48) -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(size)).rstrip(b"=").decode("ascii")


@dataclass(frozen=True)
class SecretReference:
    provider: str
    locator: str

    def validate(self) -> None:
        if self.provider not in SECRET_PROVIDERS:
            raise ConnectionBrokerError("Secret provider must be an approved vault type.")
        if not SECRET_LOCATOR.fullmatch(self.locator) or TOKEN_LIKE.search(self.locator):
            raise ConnectionBrokerError("Use a secret name or vault locator, never a secret value.")
        if len(self.locator) >= 32 and re.fullmatch(r"[A-Za-z0-9_-]+", self.locator):
            raise ConnectionBrokerError("High-entropy values are not valid secret references.")
        if self.provider == "environment" and not re.fullmatch(r"[A-Z][A-Z0-9_]{2,127}", self.locator):
            raise ConnectionBrokerError("Environment secret references must use an uppercase variable name.")

    def to_public_dict(self) -> dict[str, str]:
        self.validate()
        return {"provider": self.provider, "locator": self.locator, "value": "never_collected"}


@dataclass(frozen=True)
class ConnectorSpec:
    connector_id: str
    display_name: str
    auth_methods: tuple[AuthMethod, ...]
    allowed_scopes: tuple[str, ...] = ()
    high_risk_scopes: tuple[str, ...] = ()
    authorization_endpoint: str = ""
    device_authorization_endpoint: str = ""
    token_endpoint: str = ""
    signup_url: str = ""
    public_client_id: str = ""
    supports_signup: bool = False

    def validate(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9-]{2,63}", self.connector_id):
            raise ConnectionBrokerError("Connector id must be a stable lowercase slug.")
        if len(self.display_name.strip()) < 2 or not self.auth_methods:
            raise ConnectionBrokerError("Connector name and at least one auth method are required.")
        if AuthMethod.OAUTH_PKCE in self.auth_methods:
            _https_url(self.authorization_endpoint, "Authorization endpoint")
            _https_url(self.token_endpoint, "Token endpoint")
            if not self.public_client_id.strip():
                raise ConnectionBrokerError("OAuth PKCE requires a configured public client id.")
        if AuthMethod.OAUTH_DEVICE in self.auth_methods:
            _https_url(self.device_authorization_endpoint, "Device authorization endpoint")
        if self.signup_url:
            _https_url(self.signup_url, "Signup URL")
        unknown_risk = set(self.high_risk_scopes) - set(self.allowed_scopes)
        if unknown_risk:
            raise ConnectionBrokerError("High-risk scopes must also appear in allowed scopes.")


@dataclass(frozen=True)
class ConnectionRequest:
    user_id: str
    auth_method: AuthMethod
    requested_scopes: tuple[str, ...] = ()
    redirect_uri: str = ""
    secret_ref: SecretReference | None = None


@dataclass(frozen=True)
class ActionDecision:
    allowed: bool
    status: str
    reason: str
    requires_user_presence: bool = False


@dataclass
class ConnectionPlan:
    plan_id: str
    connector_id: str
    auth_method: str
    status: str
    requested_scopes: list[str]
    approval_gates: list[dict[str, Any]]
    next_steps: list[str]
    authorization_url: str | None = None
    secret_reference: dict[str, str] | None = None
    created_at: float = field(default_factory=time.time)
    private_context: dict[str, str] = field(default_factory=dict, repr=False)

    def to_public_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("private_context", None)
        payload["schema"] = "dreamco.buddy_connection_plan.v1"
        payload["stores_raw_credentials"] = False
        payload["automatic_account_creation"] = False
        return payload


@dataclass(frozen=True)
class SignupRequest:
    app_name: str
    signup_url: str
    account_purpose: str


@dataclass
class SignupPlan:
    plan_id: str
    app_name: str
    official_origin: str
    account_purpose: str
    status: str
    user_presence_gates: list[dict[str, str]]
    next_steps: list[str]
    submit_allowed: bool = False

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "schema": "dreamco.buddy_signup_handoff.v1",
            **asdict(self),
            "stores_raw_credentials": False,
        }


class BuddyConnectionBroker:
    """Prepare scoped app access while preserving user control."""

    def create_connection_plan(
        self,
        spec: ConnectorSpec,
        request: ConnectionRequest,
    ) -> ConnectionPlan:
        spec.validate()
        if not request.user_id.strip():
            raise ConnectionBrokerError("A user id is required for the audit trail.")
        if request.auth_method not in spec.auth_methods:
            raise ConnectionBrokerError("The requested authentication method is not supported.")

        scopes = list(dict.fromkeys(scope.strip() for scope in request.requested_scopes if scope.strip()))
        unknown_scopes = set(scopes) - set(spec.allowed_scopes)
        if unknown_scopes:
            raise ConnectionBrokerError(
                "Requested scopes are not in the connector allowlist: "
                + ", ".join(sorted(unknown_scopes))
            )

        gates = [
            {
                "id": "scope_consent",
                "reason": "The user reviews the exact permissions before authorization.",
                "blocking": True,
            }
        ]
        high_risk = sorted(set(scopes) & set(spec.high_risk_scopes))
        if high_risk:
            gates.append(
                {
                    "id": "high_risk_scope_approval",
                    "reason": "High-impact permissions require approval for this connection.",
                    "blocking": True,
                    "scopes": high_risk,
                }
            )

        plan = ConnectionPlan(
            plan_id=f"connect-{uuid.uuid4().hex[:16]}",
            connector_id=spec.connector_id,
            auth_method=request.auth_method.value,
            status="user_action_required",
            requested_scopes=scopes,
            approval_gates=gates,
            next_steps=[],
        )

        if request.auth_method is AuthMethod.OAUTH_PKCE:
            redirect_uri = _https_url(request.redirect_uri, "Redirect URI", allow_localhost=True)
            verifier = _pkce_value()
            challenge = base64.urlsafe_b64encode(
                hashlib.sha256(verifier.encode("ascii")).digest()
            ).rstrip(b"=").decode("ascii")
            state = _pkce_value(32)
            plan.authorization_url = spec.authorization_endpoint + "?" + urlencode(
                {
                    "response_type": "code",
                    "client_id": spec.public_client_id,
                    "redirect_uri": redirect_uri,
                    "scope": " ".join(scopes),
                    "state": state,
                    "code_challenge": challenge,
                    "code_challenge_method": "S256",
                }
            )
            plan.private_context = {
                "pkce_verifier": verifier,
                "state": state,
                "storage": "encrypted_backend_session_only",
            }
            plan.next_steps = [
                "Open the provider authorization page.",
                "User signs in and approves the displayed scopes.",
                "Backend validates state and exchanges the code using the PKCE verifier.",
            ]
        elif request.auth_method is AuthMethod.OAUTH_DEVICE:
            plan.next_steps = [
                "Backend requests a short-lived device code.",
                "User opens the official verification page and enters the code.",
                "Backend polls within the provider interval and stores the resulting token in a vault.",
            ]
            plan.approval_gates.append(
                {
                    "id": "device_verification",
                    "reason": "The user must complete verification on the provider domain.",
                    "blocking": True,
                }
            )
        elif request.auth_method in {AuthMethod.API_KEY, AuthMethod.WEBHOOK_HMAC, AuthMethod.CUSTOM_REST}:
            if request.secret_ref is None:
                raise ConnectionBrokerError("This method requires a secret reference.")
            plan.secret_reference = request.secret_ref.to_public_dict()
            plan.status = "backend_configuration_required"
            plan.next_steps = [
                "Resolve the named secret inside the approved backend vault.",
                "Run the connector sandbox health check.",
                "Ask the user before enabling write or money-moving actions.",
            ]
        elif request.auth_method in {
            AuthMethod.PASSKEY,
            AuthMethod.BROWSER_HANDOFF,
            AuthMethod.OIDC_SAML,
        }:
            plan.next_steps = [
                "Open the official application sign-in page.",
                "User completes passkey, SSO, MFA, or session verification.",
                "Buddy receives only the resulting scoped connection status.",
            ]
            plan.approval_gates.append(
                {
                    "id": "user_presence",
                    "reason": "Authentication must be completed directly by the user.",
                    "blocking": True,
                }
            )
        else:
            raise ConnectionBrokerError("Unsupported authentication method.")

        return plan

    def create_signup_plan(self, request: SignupRequest) -> SignupPlan:
        if len(request.app_name.strip()) < 2:
            raise ConnectionBrokerError("App name is required.")
        if len(request.account_purpose.strip()) < 5:
            raise ConnectionBrokerError("A clear account purpose is required.")
        signup_url = _https_url(request.signup_url, "Signup URL")
        parsed = urlsplit(signup_url)
        gates = [
            ("official_domain_review", "User confirms the official application domain."),
            ("terms_and_privacy", "User reviews and accepts legal terms and privacy notices."),
            ("contact_verification", "User controls email or phone verification."),
            ("identity_or_business_check", "User supplies any required identity or business proof."),
            ("captcha", "User completes any human-verification challenge."),
            ("mfa_or_passkey", "User creates and retains recovery access for MFA or a passkey."),
            ("payment", "User approves any trial, subscription, purchase, or billing method."),
        ]
        return SignupPlan(
            plan_id=f"signup-{uuid.uuid4().hex[:16]}",
            app_name=request.app_name.strip(),
            official_origin=f"{parsed.scheme}://{parsed.netloc}",
            account_purpose=request.account_purpose.strip(),
            status="user_action_required",
            user_presence_gates=[{"id": gate_id, "reason": reason} for gate_id, reason in gates],
            next_steps=[
                "Buddy prepares the minimum account fields and requested permissions.",
                "User completes every identity, legal, security, and payment gate.",
                "Buddy connects the approved account through the least-privilege auth method.",
            ],
        )

    def decide_action(self, action: str, *, explicit_user_approval: bool = False) -> ActionDecision:
        normalized = action.strip().lower()
        if normalized in USER_PRESENCE_ACTIONS:
            return ActionDecision(
                allowed=False,
                status="user_presence_required",
                reason="This action must be completed directly by the user.",
                requires_user_presence=True,
            )
        if normalized in HIGH_IMPACT_ACTIONS and not explicit_user_approval:
            return ActionDecision(
                allowed=False,
                status="approval_required",
                reason="High-impact app actions require explicit approval for this run.",
            )
        if not normalized:
            return ActionDecision(False, "invalid", "An action name is required.")
        return ActionDecision(True, "allowed", "The action may proceed within its scoped connector.")
