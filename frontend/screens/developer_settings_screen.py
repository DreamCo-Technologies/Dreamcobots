"""
DreamCo Money OS — Developer Settings Screen

FlutterFlow-style screen for managing developer API keys and OAuth provider
connections.  Provides buttons to:
    • Generate a new API key (POST /api/tokens)
    • List, filter, and revoke existing API keys
    • Connect with Google OAuth (POST /auth/oauth/google)
    • Connect with GitHub OAuth (POST /auth/oauth/github)
"""

from datetime import datetime


class DeveloperSettingsScreen:
    """
    Developer settings panel with API key management and OAuth provider buttons.

    Fields
    ------
    user_id          : Authenticated user's ID.
    user_tier        : Subscription tier string (free/pro/enterprise).
    api_keys         : List of API key records for the current user.
    selected_category: Category filter applied to the key list.
    oauth_providers  : Dict of provider → connected status.
    last_updated     : ISO timestamp.
    """

    SCREEN_NAME = "DeveloperSettingsScreen"
    ROUTE = "/settings/developer"

    VALID_CATEGORIES = ["read_only", "full_access", "bot_runner", "webhook", "analytics"]

    def __init__(
        self,
        user_id: str = "",
        user_tier: str = "FREE",
        api_keys: list = None,
        selected_category: str = "all",
        oauth_providers: dict = None,
    ):
        self.user_id = user_id
        self.user_tier = user_tier
        self.api_keys = api_keys or []
        self.selected_category = selected_category
        self.oauth_providers = oauth_providers or {"google": False, "github": False}
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> dict:
        """Return the screen's UI data model for FlutterFlow rendering."""
        filtered_keys = (
            [k for k in self.api_keys if k.get("category") == self.selected_category]
            if self.selected_category != "all"
            else self.api_keys
        )

        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "header": {
                    "title": "Developer Settings",
                    "subtitle": "Manage API keys and OAuth integrations",
                },
                # ---- OAuth provider buttons ----
                "oauth_section": {
                    "title": "Sign in / connect with a provider",
                    "buttons": [
                        {
                            "id": "btn_oauth_google",
                            "label": "Connect with Google",
                            "icon": "google",
                            "action": "POST /auth/oauth/google",
                            "connected": self.oauth_providers.get("google", False),
                            "color": "#4285F4",
                        },
                        {
                            "id": "btn_oauth_github",
                            "label": "Connect with GitHub",
                            "icon": "github",
                            "action": "POST /auth/oauth/github",
                            "connected": self.oauth_providers.get("github", False),
                            "color": "#24292E",
                        },
                    ],
                },
                # ---- API key generation button ----
                "api_key_generate_section": {
                    "title": "Generate API Key",
                    "button": {
                        "id": "btn_generate_key",
                        "label": "Generate New API Key",
                        "icon": "key",
                        "action": "POST /api/tokens",
                        "color": "primary",
                    },
                    "category_picker": {
                        "label": "Key category",
                        "options": self.VALID_CATEGORIES,
                        "selected": self.selected_category if self.selected_category != "all" else "full_access",
                    },
                    "label_input": {
                        "placeholder": "Enter a label for this key (e.g. My Bot Runner)",
                    },
                },
                # ---- API key list ----
                "api_keys_section": {
                    "title": "Your API Keys",
                    "filter_row": {
                        "categories": ["all"] + self.VALID_CATEGORIES,
                        "selected": self.selected_category,
                        "action": "GET /api/tokens?category=<category>",
                    },
                    "usage_button": {
                        "id": "btn_view_usage",
                        "label": "View Usage by Category",
                        "action": "GET /api/tokens/usage",
                        "icon": "bar_chart",
                    },
                    "keys_list": {
                        "count": len(filtered_keys),
                        "items": [
                            {
                                "key_id": k.get("key_id"),
                                "label": k.get("label"),
                                "category": k.get("category"),
                                "tier": k.get("tier"),
                                "call_count": k.get("call_count", 0),
                                "is_active": k.get("is_active", True),
                                "created_at": k.get("created_at"),
                                "revoke_button": {
                                    "id": f"btn_revoke_{k.get('key_id')}",
                                    "label": "Revoke",
                                    "action": f"DELETE /api/tokens/{k.get('key_id')}",
                                    "color": "danger",
                                },
                            }
                            for k in filtered_keys
                        ],
                    },
                },
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        """Serialise all screen state to a plain dict."""
        return {
            "screen": self.SCREEN_NAME,
            "user_id": self.user_id,
            "user_tier": self.user_tier,
            "api_keys": self.api_keys,
            "selected_category": self.selected_category,
            "oauth_providers": self.oauth_providers,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "DeveloperSettingsScreen":
        """Return a pre-populated demo instance."""
        return cls(
            user_id="usr_demo0000000000",
            user_tier="PRO",
            api_keys=[
                {
                    "key_id": "kid_a1b2c3d4",
                    "label": "Main Bot Runner",
                    "category": "bot_runner",
                    "tier": "pro",
                    "call_count": 1240,
                    "is_active": True,
                    "created_at": 1_700_000_000.0,
                },
                {
                    "key_id": "kid_e5f6a7b8",
                    "label": "Analytics Readonly",
                    "category": "analytics",
                    "tier": "pro",
                    "call_count": 320,
                    "is_active": True,
                    "created_at": 1_710_000_000.0,
                },
                {
                    "key_id": "kid_c9d0e1f2",
                    "label": "Webhook Notifier",
                    "category": "webhook",
                    "tier": "pro",
                    "call_count": 88,
                    "is_active": False,
                    "created_at": 1_705_000_000.0,
                },
            ],
            selected_category="all",
            oauth_providers={"google": True, "github": False},
        )
