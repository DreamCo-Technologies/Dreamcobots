"""Stable Buddy ids, personality traits, context tone, and free asset presets."""

from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any


class BuddyCustomizationError(ValueError):
    """Raised when a Buddy customization is unsafe or ambiguous."""


TRAITS = {"warmth", "directness", "curiosity", "humor", "patience", "energy", "formality", "creativity"}
PROFESSIONAL_CONTEXTS = {"business_deal", "sales_call", "legal", "medical", "financial", "emergency", "government_filing"}


@dataclass(frozen=True)
class PersonalityProfile:
    traits: dict[str, float]
    adapt_slang: bool = True
    professional_context_override: bool = True

    def validate(self) -> None:
        if set(self.traits) - TRAITS or not self.traits:
            raise BuddyCustomizationError("Use only supported personality traits.")
        if any(not isinstance(value, (int, float)) or value < 0 or value > 1 for value in self.traits.values()):
            raise BuddyCustomizationError("Personality trait values must be between 0 and 1.")

    def tone_for(self, context: str) -> dict[str, Any]:
        self.validate()
        professional = self.professional_context_override and context in PROFESSIONAL_CONTEXTS
        return {
            "context": context,
            "traits": self.traits,
            "slang_allowed": self.adapt_slang and not professional,
            "professional_override": professional,
            "disclosure": "Buddy remains an AI assistant and does not impersonate the user.",
        }


@dataclass(frozen=True)
class BuddyProfile:
    owner_user_id: str
    label: str
    personality: PersonalityProfile
    voice_preset_id: str = "voice-neutral-guide"
    avatar_preset_id: str = "avatar-signal-cobalt"

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", self.owner_user_id) or len(self.label.strip()) < 2:
            raise BuddyCustomizationError("Owner id and Buddy label are required.")
        self.personality.validate()
        catalog = build_asset_catalog()
        if self.voice_preset_id not in {item["id"] for item in catalog["voices"]}:
            raise BuddyCustomizationError("Unknown voice preset.")
        if self.avatar_preset_id not in {item["id"] for item in catalog["avatars"]}:
            raise BuddyCustomizationError("Unknown avatar preset.")

    def to_public_dict(self) -> dict[str, Any]:
        self.validate()
        instance_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"dreamco:buddy:{self.owner_user_id}:{self.label}")
        return {
            "schema": "dreamco.user_buddy_profile.v1",
            "buddy_instance_id": f"buddy-{instance_uuid}",
            "label": self.label,
            "personality": asdict(self.personality),
            "voice_preset_id": self.voice_preset_id,
            "avatar_preset_id": self.avatar_preset_id,
            "owner_user_id": self.owner_user_id,
            "traceable": True,
            "transferable_ownership": False,
        }


def build_asset_catalog() -> dict[str, Any]:
    voice_styles = [
        ("neutral-guide", "Neutral Guide", 1.0, 1.0),
        ("calm-coach", "Calm Coach", 0.90, 0.94),
        ("bright-builder", "Bright Builder", 1.08, 1.06),
        ("deep-narrator", "Deep Narrator", 0.86, 0.82),
        ("clear-teacher", "Clear Teacher", 0.94, 1.02),
        ("focused-operator", "Focused Operator", 1.02, 0.92),
        ("gentle-companion", "Gentle Companion", 0.88, 1.04),
        ("stage-presenter", "Stage Presenter", 1.04, 0.98),
        ("story-reader", "Story Reader", 0.92, 1.08),
        ("studio-director", "Studio Director", 0.98, 0.88),
        ("patient-tutor", "Patient Tutor", 0.84, 1.02),
        ("quick-assistant", "Quick Assistant", 1.14, 1.04),
    ]
    palettes = [
        ("signal-cobalt", "#2057d4", "#f7f9ff"),
        ("mint-charcoal", "#1b8f73", "#17211f"),
        ("coral-ink", "#e45f51", "#1c2028"),
        ("gold-graphite", "#c99728", "#24262b"),
        ("orchid-forest", "#9a5cb4", "#19382d"),
        ("sky-crimson", "#3c8fd4", "#b92f4a"),
        ("lime-navy", "#93bd32", "#152a47"),
        ("rose-steel", "#c45e7d", "#364250"),
        ("aqua-plum", "#2ca5a5", "#5e345d"),
        ("amber-indigo", "#d18b24", "#343b83"),
        ("jade-wine", "#2f8b61", "#7b2f49"),
        ("ice-onyx", "#8ccfe0", "#1c1f23"),
    ]
    return {
        "schema": "dreamco.buddy_free_asset_presets.v1",
        "voices": [
            {
                "id": f"voice-{slug}",
                "name": name,
                "rate": rate,
                "pitch": pitch,
                "kind": "synthetic_parameter_preset",
                "real_person_reference": False,
                "audio_included": False,
            }
            for slug, name, rate, pitch in voice_styles
        ],
        "avatars": [
            {
                "id": f"avatar-{slug}",
                "name": slug.replace("-", " ").title(),
                "primary": primary,
                "accent": accent,
                "kind": "original_geometric_avatar_preset",
                "real_person_reference": False,
            }
            for slug, primary, accent in palettes
        ],
        "license": "DreamCo original parameter presets; local rendering engine required",
    }
