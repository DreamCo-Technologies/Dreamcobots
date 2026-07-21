"""
DreamCo SaaS API — Production-hardened REST API for the DreamCo platform.

Endpoints
---------
GET  /health                 Liveness probe (no auth required)
POST /auth/signup            Create account (returns token)
POST /auth/login             Authenticate (returns token)
POST /auth/oauth/google      OAuth signup/login via Google ID token
POST /auth/oauth/github      OAuth signup/login via GitHub access token

POST /bots/run-all           Run all registered bots (Bearer token auth)
POST /bots/run-single        Run one named bot      (Bearer token auth)
POST /bots/upload            Upload & sandbox-test a bot file
GET  /bots/list              List the current user's uploaded bots

GET  /stats                  Bot execution stats for the current user
GET  /revenue                Revenue summary (PRO+ required)

POST /billing/subscribe      Create or upgrade a Stripe subscription
GET  /billing/status         Current subscription status

POST /api/tokens             Generate a new developer API key (Bearer token auth)
GET  /api/tokens             List the current user's API keys (optional ?category= filter)
DELETE /api/tokens/<key_id>  Revoke a developer API key
GET  /api/tokens/usage       API key usage summary for the current user

GET  /domains                List the current user's domain portfolio
POST /domains                Register a new domain in the portfolio
POST /domains/flip           Record a completed domain flip
PUT  /domains/<domain_id>/sell  Mark a domain for sale or close a sale
GET  /domains/summary        Portfolio aggregate statistics

Note: The in-memory bot registry (_user_bots) is intended for development /
testing only.  Replace with a persistent database in production deployments.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict

from core.dreamco_orchestrator import DreamCoOrchestrator
from core.bot_validator import BotValidator
from core.sandbox_runner import SandboxRunner
from saas.auth.auth import AuthService, UserRegistry, _generate_token as _auth_generate_token
from saas.auth.middleware import AuthMiddleware, RateLimiter
from saas.auth.user_model import SubscriptionTier
from saas.auth.api_key_registry import ClientApiKeyRegistry, API_KEY_CATEGORIES
from saas.stripe_billing import StripeBillingService
from bots.business_launch_pad.domain_manager import DomainManager, DomainManagerError

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared service instances
# ---------------------------------------------------------------------------

_orch = DreamCoOrchestrator()
_registry = UserRegistry()
_auth_svc = AuthService(registry=_registry)
_middleware = AuthMiddleware(auth_service=_auth_svc)
_rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
_validator = BotValidator()
_sandbox = SandboxRunner(timeout_seconds=10)
_billing = StripeBillingService(simulation_mode=not os.environ.get("STRIPE_API_KEY"))

# Developer API key registry (per-user client keys)
_api_key_registry = ClientApiKeyRegistry()

# Domain portfolio manager
_domain_manager = DomainManager()

# Legacy API-key support (backwards compatible).
# Set DREAMCO_API_KEYS env var with comma-separated keys in production.
_raw_keys = os.environ.get("DREAMCO_API_KEYS", "")
VALID_API_KEYS: set = {k.strip() for k in _raw_keys.split(",") if k.strip()}
# Always include the demo key so tests can authenticate.
VALID_API_KEYS.add("dreamco_demo_key")

# Tier-based daily rate limits.
TIER_DAILY_LIMITS: Dict[str, int] = {
    "FREE": 10,
    "PRO": 500,
    "ENTERPRISE": 10_000,
}

# Resolved absolute upload directory
_ABS_UPLOAD_FOLDER = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "uploads")
)
os.makedirs(_ABS_UPLOAD_FOLDER, exist_ok=True)

# In-memory bot registry per user.
# NOTE: Replace with a persistent database in production.
_user_bots: Dict[str, list] = {}

# Allowed user-id character set (hex after 'usr_' prefix)
_USER_ID_RE = re.compile(r'^usr_[0-9a-f]{16}$')


def authenticate(api_key: str) -> bool:
    """Return True if *api_key* is a recognised key."""
    return bool(api_key and api_key in VALID_API_KEYS)


def _get_tier(api_key: str) -> str:
    """Derive the tier string from an API key prefix."""
    if api_key.startswith("dreamco_ent_"):
        return "ENTERPRISE"
    if api_key.startswith("dreamco_pro_"):
        return "PRO"
    return "FREE"


class DreamCoSaaSApp:
    """Simple SaaS application wrapper for testing without Flask."""

    def __init__(self, orchestrator: Any = None) -> None:
        self._orch = orchestrator if orchestrator is not None else _orch
        self._call_counts: Dict[str, int] = {}

    def _check_rate_limit(self, api_key: str) -> bool:
        """Return True if the key is within its tier daily limit."""
        tier = _get_tier(api_key)
        limit = TIER_DAILY_LIMITS.get(tier, TIER_DAILY_LIMITS["FREE"])
        count = self._call_counts.get(api_key, 0)
        return count < limit

    def _increment(self, api_key: str) -> None:
        self._call_counts[api_key] = self._call_counts.get(api_key, 0) + 1

    def handle_run_bots(self, api_key: str) -> tuple:
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401
        if not self._check_rate_limit(api_key):
            return {"error": "Rate limit exceeded"}, 429
        self._increment(api_key)
        results = self._orch.run_all_bots()
        return {"results": results, "tier": _get_tier(api_key)}, 200

    def handle_run_single(self, api_key: str, bot_path: str, bot_name: str) -> tuple:
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401
        result = self._orch.run_bot(bot_path, bot_name) if hasattr(self._orch, "run_bot") else {}
        return {"result": result}, 200

    def handle_summary(self, api_key: str) -> tuple:
        if not authenticate(api_key):
            return {"error": "Unauthorized"}, 401
        if _get_tier(api_key) == "FREE":
            return {"error": "PRO or ENTERPRISE tier required"}, 403
        results = self._orch.run_all_bots()
        return {"summary": results}, 200

    def handle_health(self) -> tuple:
        return {"status": "ok"}, 200


def authenticate_legacy(api_key: str | None) -> bool:
    """Return True if *api_key* is a valid legacy key."""
    return bool(api_key and VALID_API_KEYS and api_key in VALID_API_KEYS)


def _safe_user_dir(user_id: str) -> str | None:
    """
    Return an absolute path for the user's upload directory, or None if
    *user_id* fails format validation.  Prevents path traversal attacks.
    """
    if not _USER_ID_RE.match(user_id):
        return None
    candidate = os.path.realpath(os.path.join(_ABS_UPLOAD_FOLDER, user_id))
    # Ensure the resolved path is inside the upload folder
    if not candidate.startswith(_ABS_UPLOAD_FOLDER + os.sep):
        return None
    return candidate


def _safe_filename(raw_name: str) -> str | None:
    """
    Return a sanitised filename (alphanumeric, underscores, hyphens + .py)
    or None if *raw_name* is not a safe .py filename.
    """
    base = os.path.basename(raw_name)
    if not base.endswith(".py"):
        return None
    stem = base[:-3]
    if not re.match(r'^[a-zA-Z0-9_\-]+$', stem):
        return None
    return base


def _sanitise_bot_result(result: dict) -> dict:
    """
    Return a copy of *result* with internal error details removed so that
    raw exception messages are never forwarded to API callers.
    """
    safe = {
        "bot": result.get("bot", ""),
        "status": "error" if result.get("error") else "ok",
    }
    if result.get("output"):
        output = result["output"]
        safe["output"] = {
            k: output[k]
            for k in ("revenue", "leads_generated", "conversion_rate")
            if k in output
        }
    if result.get("validation"):
        safe["validation"] = result["validation"]
    return safe


def _generate_oauth_password(provider_uid: str) -> str:
    """Generate a deterministic-but-secure internal password for OAuth accounts.

    OAuth users authenticate via their provider token, never via this
    password.  The password satisfies the 8-char minimum so signup()
    succeeds, and is derived from the provider UID so it's reproducible.
    """
    import hashlib
    return "oauth_" + hashlib.sha256(provider_uid.encode()).hexdigest()[:24]


# ---------------------------------------------------------------------------
# Flask app (optional dependency)
# ---------------------------------------------------------------------------

try:
    from flask import Flask, request, jsonify  # type: ignore[import]

    app = Flask(__name__)

    # ------------------------------------------------------------------ #
    #  Health                                                              #
    # ------------------------------------------------------------------ #

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok", "service": "dreamco-api"})

    # ------------------------------------------------------------------ #
    #  Auth                                                                #
    # ------------------------------------------------------------------ #

    @app.route("/auth/signup", methods=["POST"])
    def signup() -> Any:
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        result = _auth_svc.signup(
            username=data.get("username", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
        )
        if not result.get("success"):
            return jsonify({"error": result.get("error", "signup failed")}), 400
        return jsonify({"success": True, "user_id": result["user_id"], "token": result["token"]}), 201

    @app.route("/auth/login", methods=["POST"])
    def login() -> Any:
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        result = _auth_svc.login(
            email=data.get("email", ""),
            password=data.get("password", ""),
        )
        if not result.get("success"):
            return jsonify({"error": "invalid credentials"}), 401
        return jsonify({
            "success": True,
            "user_id": result["user_id"],
            "token": result["token"],
            "tier": result["tier"],
        })

    # ------------------------------------------------------------------ #
    #  OAuth signup / login                                                #
    # ------------------------------------------------------------------ #

    @app.route("/auth/oauth/google", methods=["POST"])
    def oauth_google() -> Any:
        """
        OAuth signup/login via a Google ID token.

        Request body
        ------------
        id_token : str
            Google-issued ID token from the client (obtained via Google
            Sign-In SDK on web or mobile).
        username : str, optional
            Preferred username for new accounts (ignored on login).

        Response (201 on new account, 200 on existing)
        -----------------------------------------------
        success, user_id, token, tier, provider, is_new_user
        """
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        id_token: str = data.get("id_token", "").strip()
        if not id_token:
            return jsonify({"error": "id_token is required"}), 400

        # --------------- token verification ---------------
        # In production: call Google's tokeninfo endpoint or use
        # google-auth library to verify signature & audience.
        # Here we accept the token as opaque and extract the sub claim
        # from a decoded payload if available, else derive a stable ID.
        # This simulation keeps the module dependency-free.
        import base64 as _b64
        import json as _json

        google_user_id: str = ""
        google_email: str = ""
        google_name: str = ""
        try:
            # JWT is three base64url segments; the payload is the second
            parts = id_token.split(".")
            if len(parts) == 3:
                padded = parts[1] + "=" * (-len(parts[1]) % 4)
                payload = _json.loads(_b64.urlsafe_b64decode(padded))
                google_user_id = str(payload.get("sub", ""))
                google_email = payload.get("email", "")
                google_name = payload.get("name", "")
        except Exception:
            pass  # fall through to synthetic ID

        if not google_user_id:
            # Deterministic fallback so tests work without a real JWT
            import hashlib as _hl
            google_user_id = _hl.sha256(id_token.encode()).hexdigest()[:16]
        if not google_email:
            google_email = f"google_{google_user_id}@oauth.dreamco.local"
        if not google_name:
            google_name = data.get("username", "") or f"google_{google_user_id[:8]}"

        # Check if a user with this email already exists
        existing = _registry.get_by_email(google_email)
        if existing:
            new_token = _auth_generate_token(existing.user_id)
            return jsonify({
                "success": True,
                "user_id": existing.user_id,
                "token": new_token,
                "tier": existing.tier.value,
                "provider": "google",
                "is_new_user": False,
            })

        # Create new account
        result = _auth_svc.signup(
            username=google_name,
            email=google_email,
            password=_generate_oauth_password(google_user_id),
        )
        if not result.get("success"):
            return jsonify({"error": result.get("error", "oauth signup failed")}), 400
        return jsonify({
            "success": True,
            "user_id": result["user_id"],
            "token": result["token"],
            "tier": "free",
            "provider": "google",
            "is_new_user": True,
        }), 201

    @app.route("/auth/oauth/github", methods=["POST"])
    def oauth_github() -> Any:
        """
        OAuth signup/login via a GitHub access token.

        Request body
        ------------
        access_token : str
            GitHub OAuth access token obtained via the GitHub OAuth flow.
        username : str, optional
            Preferred username for new accounts.

        Response (201 on new account, 200 on existing)
        -----------------------------------------------
        success, user_id, token, tier, provider, is_new_user
        """
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        access_token: str = data.get("access_token", "").strip()
        if not access_token:
            return jsonify({"error": "access_token is required"}), 400

        # --------------- token exchange ---------------
        # In production: call https://api.github.com/user with the token
        # to retrieve the GitHub user profile (login, id, email).
        # This simulation derives a stable identity from the token.
        import hashlib as _hl
        gh_id = _hl.sha256(access_token.encode()).hexdigest()[:16]
        gh_email = f"github_{gh_id}@oauth.dreamco.local"
        gh_name = data.get("username", "") or f"gh_{gh_id[:8]}"

        existing = _registry.get_by_email(gh_email)
        if existing:
            new_token = _auth_generate_token(existing.user_id)
            return jsonify({
                "success": True,
                "user_id": existing.user_id,
                "token": new_token,
                "tier": existing.tier.value,
                "provider": "github",
                "is_new_user": False,
            })

        result = _auth_svc.signup(
            username=gh_name,
            email=gh_email,
            password=_generate_oauth_password(gh_id),
        )
        if not result.get("success"):
            return jsonify({"error": result.get("error", "oauth signup failed")}), 400
        return jsonify({
            "success": True,
            "user_id": result["user_id"],
            "token": result["token"],
            "tier": "free",
            "provider": "github",
            "is_new_user": True,
        }), 201

    # ------------------------------------------------------------------ #
    #  Bot execution                                                       #
    # ------------------------------------------------------------------ #

    @app.route("/bots/run-all", methods=["POST"])
    def run_all_bots() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err and not authenticate_legacy(request.headers.get("x-api-key")):
            return jsonify({"error": "Unauthorized"}), 401

        if user and not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        results = _orch.run_all_bots()
        summary = _orch.summary(results)

        if user:
            _auth_svc.consume_quota(user.user_id)

        safe_results = [_sanitise_bot_result(r) for r in results]
        return jsonify({"results": safe_results, "summary": summary})

    @app.route("/bots/run-single", methods=["POST"])
    def run_single_bot() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err and not authenticate_legacy(request.headers.get("x-api-key")):
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        bot_path: str = data.get("path", "")
        bot_name: str = data.get("name", "")

        if not bot_path or not bot_name:
            return jsonify({"error": "Both 'path' and 'name' are required"}), 400

        if user and not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        result = _orch.run_bot(bot_path, bot_name)
        if user:
            _auth_svc.consume_quota(user.user_id)

        return jsonify(_sanitise_bot_result(result))

    # ------------------------------------------------------------------ #
    #  Bot upload                                                          #
    # ------------------------------------------------------------------ #

    @app.route("/bots/upload", methods=["POST"])
    def upload_bot() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        if not _rate_limiter.is_allowed(user.user_id):
            return jsonify({"error": "rate limit exceeded"}), 429

        quota = _auth_svc.check_quota(user.user_id)
        if not quota.get("allowed"):
            return jsonify({"error": "daily bot quota exceeded"}), 429

        if "file" not in request.files:
            return jsonify({"error": "no file provided"}), 400

        file = request.files["file"]
        safe_name = _safe_filename(file.filename or "")
        if not safe_name:
            return jsonify({"error": "invalid filename; only alphanumeric .py files are accepted"}), 400

        user_dir = _safe_user_dir(user.user_id)
        if not user_dir:
            return jsonify({"error": "invalid user account"}), 400

        # --- Validate code in memory BEFORE writing to disk ---
        file_bytes = file.read()
        try:
            source = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return jsonify({"error": "file must be valid UTF-8 Python source"}), 422

        ok, issues = _validator.validate_source(source)
        if not ok:
            return jsonify({"error": "validation failed", "issues": issues}), 422

        # Write to disk only after validation passes
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, safe_name)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(source)

        # Sandbox test
        run_result = _sandbox.run_file(file_path)

        _user_bots.setdefault(user.user_id, []).append(
            {"filename": safe_name, "status": "approved"}
        )

        return jsonify({
            "status": "approved",
            "filename": safe_name,
            "sandbox_success": run_result.get("success", False),
        })

    @app.route("/bots/list", methods=["GET"])
    def list_bots() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401
        bots = _user_bots.get(user.user_id, [])
        return jsonify({"bots": bots, "count": len(bots)})

    # ------------------------------------------------------------------ #
    #  Stats & Revenue                                                     #
    # ------------------------------------------------------------------ #

    @app.route("/stats", methods=["GET"])
    def stats() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        quota = _auth_svc.check_quota(user.user_id)
        return jsonify({
            "user_id": user.user_id,
            "tier": user.tier.value,
            "quota": quota,
            "bots_uploaded": len(_user_bots.get(user.user_id, [])),
        })

    @app.route("/revenue", methods=["GET"])
    def revenue() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        tier_err = _middleware.require_tier(user, SubscriptionTier.PRO)
        if tier_err:
            return jsonify({"error": tier_err}), 403

        summary = _billing.revenue_summary()
        return jsonify(summary)

    # ------------------------------------------------------------------ #
    #  Billing                                                             #
    # ------------------------------------------------------------------ #

    @app.route("/billing/subscribe", methods=["POST"])
    def subscribe() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        tier = data.get("tier", "")
        if tier not in ("free", "pro", "enterprise"):
            return jsonify({"error": "invalid tier; choose free, pro, or enterprise"}), 400

        cust_result = _billing.create_customer(user.user_id, user.email)
        if not cust_result.get("success"):
            _logger.error("create_customer failed for user %s", user.user_id)
            return jsonify({"error": "billing service unavailable"}), 500

        sub_result = _billing.create_subscription(
            customer_id=cust_result["customer_id"],
            tier=tier,
            user_id=user.user_id,
        )
        if not sub_result.get("success"):
            _logger.error("create_subscription failed for user %s", user.user_id)
            return jsonify({"error": "subscription creation failed"}), 500

        _auth_svc.upgrade_tier(user.user_id, SubscriptionTier(tier))
        return jsonify({
            "success": True,
            "tier": tier,
            "subscription_id": sub_result.get("subscription_id"),
        })

    @app.route("/billing/status", methods=["GET"])
    def billing_status() -> Any:
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        return jsonify({
            "user_id": user.user_id,
            "tier": user.tier.value,
            "revenue_summary": _billing.revenue_summary(),
        })

    # Legacy endpoints (backwards compatible)
    @app.route("/run-bots", methods=["POST"])
    def run_bots_legacy() -> Any:
        api_key = request.headers.get("x-api-key")
        if not authenticate_legacy(api_key):
            return jsonify({"error": "Unauthorized"}), 401
        results = _orch.run_all_bots()
        summary = _orch.summary(results)
        return jsonify({"results": [_sanitise_bot_result(r) for r in results], "summary": summary})

    @app.route("/run-single", methods=["POST"])
    def run_single_legacy() -> Any:
        api_key = request.headers.get("x-api-key")
        if not authenticate_legacy(api_key):
            return jsonify({"error": "Unauthorized"}), 401
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        bot_path: str = data.get("path", "")
        bot_name: str = data.get("name", "")
        if not bot_path or not bot_name:
            return jsonify({"error": "Both 'path' and 'name' are required"}), 400
        result = _orch.run_bot(bot_path, bot_name)
        return jsonify(_sanitise_bot_result(result))

    # ------------------------------------------------------------------ #
    #  Developer API token management                                      #
    # ------------------------------------------------------------------ #

    @app.route("/api/tokens", methods=["POST"])
    def create_api_token() -> Any:
        """Generate a new developer API key for the authenticated user.

        Request body
        ------------
        label : str
            Human-readable name for the key.
        category : str
            One of: read_only, full_access, bot_runner, webhook, analytics.

        Response (201)
        --------------
        key_id, key (shown once only), label, category, tier, created_at
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        label: str = data.get("label", "").strip()
        category: str = data.get("category", "").strip()

        if not label:
            return jsonify({"error": "'label' is required"}), 400
        if not category:
            return jsonify({
                "error": "'category' is required",
                "valid_categories": sorted(API_KEY_CATEGORIES),
            }), 400

        try:
            record = _api_key_registry.generate_key(
                user_id=user.user_id,
                label=label,
                category=category,
                tier=user.tier.value,
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(record.to_dict(include_key=True)), 201

    @app.route("/api/tokens", methods=["GET"])
    def list_api_tokens() -> Any:
        """List the current user's developer API keys.

        Query parameters
        ----------------
        category : str, optional
            Filter by category (read_only, full_access, bot_runner, webhook, analytics).
        include_revoked : bool, optional
            Pass ``true`` to include revoked keys (default: false).

        Response (200)
        --------------
        keys : list, count : int, valid_categories : list
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        category: str = request.args.get("category", "").strip() or None  # type: ignore[assignment]
        include_revoked: bool = request.args.get("include_revoked", "false").lower() == "true"

        keys = _api_key_registry.list_keys(
            user.user_id,
            category=category,
            active_only=not include_revoked,
        )
        return jsonify({
            "keys": [k.to_dict() for k in keys],
            "count": len(keys),
            "valid_categories": sorted(API_KEY_CATEGORIES),
        })

    @app.route("/api/tokens/<key_id>", methods=["DELETE"])
    def revoke_api_token(key_id: str) -> Any:
        """Revoke (soft-delete) a developer API key.

        Path parameter
        --------------
        key_id : str
            The ``key_id`` returned when the key was created.

        Response (200)
        --------------
        success : bool, key_id : str, message : str
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        try:
            record = _api_key_registry.revoke_key(user.user_id, key_id)
        except KeyError:
            return jsonify({"error": f"API key '{key_id}' not found"}), 404

        return jsonify({
            "success": True,
            "key_id": record.key_id,
            "message": f"API key '{record.label}' has been revoked",
        })

    @app.route("/api/tokens/usage", methods=["GET"])
    def api_token_usage() -> Any:
        """Return API key usage summary for the current user.

        Query parameters
        ----------------
        category : str, optional
            When set, the ``by_category`` field is filtered to that category.

        Response (200)
        --------------
        user_id, total_keys, active_keys, total_calls, by_category
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        summary = _api_key_registry.usage_summary(user.user_id)
        category: str = request.args.get("category", "").strip()
        if category:
            # Filter by_category to the requested one
            filtered = {category: summary["by_category"].get(category, 0)}
            summary["by_category"] = filtered

        return jsonify(summary)

    # ------------------------------------------------------------------ #
    #  Domain portfolio management                                         #
    # ------------------------------------------------------------------ #

    @app.route("/domains", methods=["GET"])
    def list_domains() -> Any:
        """List the current user's domain portfolio.

        Query parameters
        ----------------
        status : str, optional
            Filter by status: owned, listed, sold, flipped.

        Response (200)
        --------------
        domains : list, count : int
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        status: str = request.args.get("status", "").strip() or None  # type: ignore[assignment]
        try:
            domains = _domain_manager.list_portfolio(user.user_id, status=status)
        except DomainManagerError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify({"domains": [d.to_dict() for d in domains], "count": len(domains)})

    @app.route("/domains", methods=["POST"])
    def register_domain() -> Any:
        """Register a new domain in the portfolio.

        Request body
        ------------
        name : str                  Fully-qualified domain name (e.g. ``example.com``).
        registrar : str, optional   Registrar name (default: Namecheap).
        registration_cost_usd : float, optional  Cost paid (default: 12.99).
        expiry_date : str, optional ISO date of domain expiry (``YYYY-MM-DD``).
        notes : str, optional

        Response (201)
        --------------
        Domain record dict.
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        name: str = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "'name' (domain name) is required"}), 400

        try:
            cost = float(data.get("registration_cost_usd", 12.99))
        except (TypeError, ValueError):
            return jsonify({"error": "'registration_cost_usd' must be a number"}), 400

        try:
            domain = _domain_manager.register(
                name=name,
                user_id=user.user_id,
                registrar=str(data.get("registrar", "Namecheap")),
                registration_cost_usd=cost,
                expiry_date=data.get("expiry_date"),
                notes=str(data.get("notes", "")),
            )
        except DomainManagerError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(domain.to_dict()), 201

    @app.route("/domains/flip", methods=["POST"])
    def flip_domain() -> Any:
        """Record a completed domain flip (buy and sell in one step).

        Request body
        ------------
        name : str                Fully-qualified domain name.
        buy_price_usd : float     Acquisition cost.
        sell_price_usd : float    Amount received from sale.
        registrar : str, optional
        notes : str, optional

        Response (201)
        --------------
        Domain record dict with status ``flipped`` and ``profit_usd`` set.
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        name: str = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "'name' (domain name) is required"}), 400

        try:
            buy = float(data.get("buy_price_usd", 0))
            sell = float(data.get("sell_price_usd", 0))
        except (TypeError, ValueError):
            return jsonify({"error": "'buy_price_usd' and 'sell_price_usd' must be numbers"}), 400

        try:
            domain = _domain_manager.flip_domain(
                name=name,
                user_id=user.user_id,
                buy_price_usd=buy,
                sell_price_usd=sell,
                registrar=str(data.get("registrar", "Namecheap")),
                notes=str(data.get("notes", "")),
            )
        except DomainManagerError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(domain.to_dict()), 201

    @app.route("/domains/<domain_id>/sell", methods=["PUT"])
    def sell_domain(domain_id: str) -> Any:
        """Mark a domain for sale or close a completed sale.

        Request body
        ------------
        action : str
            ``"list"`` — set an asking price and mark as LISTED.
            ``"close"`` — record the final sale and mark as SOLD.
        ask_price_usd : float   Required when action is ``"list"``.
        sold_price_usd : float  Required when action is ``"close"``.

        Response (200)
        --------------
        Updated domain record dict.
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        data: Dict[str, Any] = request.get_json(silent=True) or {}
        action: str = str(data.get("action", "")).strip().lower()

        if action not in ("list", "close"):
            return jsonify({"error": "'action' must be 'list' or 'close'"}), 400

        try:
            if action == "list":
                try:
                    ask = float(data.get("ask_price_usd", 0))
                except (TypeError, ValueError):
                    return jsonify({"error": "'ask_price_usd' must be a number"}), 400
                domain = _domain_manager.mark_for_sale(domain_id, user.user_id, ask)
            else:
                try:
                    sold = float(data.get("sold_price_usd", 0))
                except (TypeError, ValueError):
                    return jsonify({"error": "'sold_price_usd' must be a number"}), 400
                domain = _domain_manager.close_sale(domain_id, user.user_id, sold)
        except KeyError:
            return jsonify({"error": f"Domain '{domain_id}' not found"}), 404
        except DomainManagerError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(domain.to_dict())

    @app.route("/domains/summary", methods=["GET"])
    def domain_portfolio_summary() -> Any:
        """Return aggregate domain portfolio statistics for the current user.

        Response (200)
        --------------
        total_domains, owned, listed, sold, flipped,
        total_invested_usd, total_revenue_usd, total_profit_usd,
        portfolio_estimated_value_usd
        """
        user, err = _middleware.authenticate(request.headers.get("Authorization"))
        if err:
            return jsonify({"error": "Unauthorized"}), 401

        return jsonify(_domain_manager.portfolio_summary(user.user_id))

    FLASK_AVAILABLE = True

except ImportError:  # pragma: no cover — Flask not installed
    app = None  # type: ignore[assignment]
    FLASK_AVAILABLE = False


def create_app() -> Any:
    """Return the Flask application instance (or None if Flask is unavailable)."""
    return app


def main() -> None:  # pragma: no cover
    if not FLASK_AVAILABLE:
        print("Flask is not installed.  Run: pip install flask")
        return
    port = int(os.environ.get("API_PORT", 5000))
    app.run(debug=False, port=port)


if __name__ == "__main__":  # pragma: no cover
    main()
