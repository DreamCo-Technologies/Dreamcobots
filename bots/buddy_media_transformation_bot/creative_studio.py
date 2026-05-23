from __future__ import annotations

from datetime import datetime
from typing import Any

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.buddy_media_transformation_bot.buddy_media_transformation_bot import BuddyMediaTransformationBot
from bots.buddy_media_transformation_bot.tiers import Tier
from bots.photo_editing_bot.photo_editing_bot import PhotoEditingBot
from bots.photo_editing_bot.tiers import Tier as PhotoTier
from bots.professional_music_editing_bot.professional_music_editing_bot import ProfessionalMusicEditingBot
from bots.professional_music_editing_bot.tiers import Tier as MusicTier
from bots.professional_video_editing_bot.professional_video_editing_bot import ProfessionalVideoEditingBot
from bots.professional_video_editing_bot.tiers import Tier as VideoTier


_PROJECT_TEMPLATES = {
    "youtube_baby_song": {
        "personal": {"music_style": "nursery-pop", "video_style": "family-friendly animated"},
        "business": {"music_style": "nursery-pop branded", "video_style": "educational kids promo"},
    },
    "commercial": {
        "personal": {"music_style": "uplifting pop", "video_style": "lifestyle teaser"},
        "business": {"music_style": "brand anthem", "video_style": "conversion-focused ad"},
    },
    "biography": {
        "personal": {"music_style": "cinematic piano", "video_style": "personal documentary"},
        "business": {"music_style": "corporate cinematic", "video_style": "founder/company story"},
    },
    "scripted_movie": {
        "personal": {"music_style": "hybrid score", "video_style": "short-film narrative"},
        "business": {"music_style": "epic trailer", "video_style": "brand narrative film"},
    },
    "lyric_music_video": {
        "personal": {"music_style": "expressive vocal", "video_style": "kinetic lyric visualizer"},
        "business": {"music_style": "campaign anthem", "video_style": "logo-aware lyric visualizer"},
    },
    "birthday_video": {
        "personal": {"music_style": "celebration pop", "video_style": "memory montage"},
        "business": {"music_style": "celebration branded", "video_style": "customer celebration story"},
    },
    "family_biography": {
        "personal": {"music_style": "warm acoustic", "video_style": "family documentary"},
        "business": {"music_style": "heritage cinematic", "video_style": "community legacy film"},
    },
    "personal_story_movie": {
        "personal": {"music_style": "emotional cinematic", "video_style": "personal narrative"},
        "business": {"music_style": "founder cinematic", "video_style": "mission narrative"},
    },
    "brand_launch_kit": {
        "personal": {"music_style": "creator launch", "video_style": "personal brand kickoff"},
        "business": {"music_style": "brand launch anthem", "video_style": "multi-channel launch reel"},
    },
    "promo_reel": {
        "personal": {"music_style": "hype trailer", "video_style": "creator promo montage"},
        "business": {"music_style": "conversion trailer", "video_style": "product promo reel"},
    },
    "business_biography": {
        "personal": {"music_style": "entrepreneurial documentary", "video_style": "origin story"},
        "business": {"music_style": "corporate documentary", "video_style": "company biography"},
    },
    "social_campaign_pack": {
        "personal": {"music_style": "viral social mix", "video_style": "vertical social burst"},
        "business": {"music_style": "campaign signature", "video_style": "cross-channel social campaign"},
    },
    "simulation_learning_video": {
        "personal": {"music_style": "focused ambient", "video_style": "interactive lesson walkthrough"},
        "business": {"music_style": "training cinematic", "video_style": "scenario-based learning module"},
    },
    "school_parent_update_video": {
        "personal": {"music_style": "uplifting acoustic", "video_style": "school-family update"},
        "business": {"music_style": "institutional warm", "video_style": "district communication brief"},
    },
    "video_game_trailer": {
        "personal": {"music_style": "epic synth", "video_style": "indie game trailer"},
        "business": {"music_style": "AAA trailer hybrid", "video_style": "launch gameplay trailer"},
    },
    "app_explainer_video": {
        "personal": {"music_style": "light tech", "video_style": "mobile app walkthrough"},
        "business": {"music_style": "productivity pulse", "video_style": "saas onboarding explainer"},
    },
    "website_launch_video": {
        "personal": {"music_style": "modern clean", "video_style": "portfolio launch teaser"},
        "business": {"music_style": "digital launch", "video_style": "website release campaign"},
    },
    "software_demo_video": {
        "personal": {"music_style": "clear ambient", "video_style": "feature-by-feature demo"},
        "business": {"music_style": "product demo", "video_style": "enterprise feature spotlight"},
    },
    "ai_business_solution_video": {
        "personal": {"music_style": "future minimal", "video_style": "ai service overview"},
        "business": {"music_style": "innovation orchestral", "video_style": "ai transformation showcase"},
    },
    "onboarding_video": {
        "personal": {"music_style": "friendly guide", "video_style": "new member onboarding"},
        "business": {"music_style": "training intro", "video_style": "employee onboarding sequence"},
    },
    "business_training_video": {
        "personal": {"music_style": "calm focus", "video_style": "skill training module"},
        "business": {"music_style": "corporate learning", "video_style": "compliance and skills training"},
    },
}


def _tier_for(enum_cls: type, tier: Tier):
    return enum_cls(tier.value)


class BuddyCreativeStudio:
    """Unified flagship creative surface for photo, video, and music production."""

    def __init__(self, tier: Tier = Tier.PRO) -> None:
        self.tier = tier
        self.media_bot = BuddyMediaTransformationBot(tier=tier)
        self.photo_bot = PhotoEditingBot(tier=_tier_for(PhotoTier, tier))
        self.video_bot = ProfessionalVideoEditingBot(tier=_tier_for(VideoTier, tier))
        self.music_bot = ProfessionalMusicEditingBot(tier=_tier_for(MusicTier, tier))

    def list_project_templates(self) -> dict[str, Any]:
        return _PROJECT_TEMPLATES

    def create_brand_kit(
        self,
        *,
        brand_name: str,
        audience: str,
        use_case: str = "business",
        tone: str = "trustworthy",
    ) -> dict[str, Any]:
        slug = brand_name.lower().replace(" ", "-")
        slogan = f"{brand_name}: {tone.title()} stories for {audience}"
        positioning = (
            f"{brand_name} is a {use_case}-ready creative brand designed for {audience}, "
            f"delivering consistent multimedia storytelling across music, video, and visuals."
        )
        style_profile = {
            "tone": tone,
            "audience": audience,
            "tone_profile": {
                "voice": "confident and human",
                "pacing": "medium-fast",
                "emotional_signature": "optimistic authority",
            },
            "primary_colors": ["#2E7DFF", "#FF6F3C", "#141B2D"],
            "typography": {"headline": "Montserrat Bold", "body": "Inter Regular"},
            "voice_guidelines": ["clear hooks", "emotion-first language", "high-trust CTA"],
        }
        typography_guidance = {
            "headlines": "Use Montserrat Bold with sentence case and short action verbs.",
            "body_text": "Use Inter Regular at readable sizes with high color contrast.",
            "captions": "Use Inter Medium and keep 1-2 line chunks per scene.",
        }
        color_system = {
            "primary": "#2E7DFF",
            "secondary": "#FF6F3C",
            "neutral_dark": "#141B2D",
            "neutral_light": "#F5F8FF",
            "accent_success": "#2BB673",
        }
        animation_style = {
            "transitions": ["smooth-zoom", "soft-fade", "kinetic-type"],
            "logo_reveal": "signal-wave pulse reveal",
            "motion_energy": "medium",
        }
        intro_outro_assets = {
            "intro_video_stub": f"https://cdn.dreamcobots.ai/brands/{slug}/intro.mp4",
            "outro_video_stub": f"https://cdn.dreamcobots.ai/brands/{slug}/outro.mp4",
            "audio_sting_stub": f"https://cdn.dreamcobots.ai/brands/{slug}/audio_sting.wav",
        }
        return {
            "brand_name": brand_name,
            "logo": {
                "concept": f"Dynamic emblem with signal-wave motif for {brand_name}",
                "delivery_stub": f"https://cdn.dreamcobots.ai/brands/{slug}/logo_primary.svg",
            },
            "slogan": slogan,
            "positioning_statement": positioning,
            "style_profile": style_profile,
            "tone_profile": style_profile["tone_profile"],
            "typography_guidance": typography_guidance,
            "color_system": color_system,
            "animation_style": animation_style,
            "intro_outro_assets": intro_outro_assets,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def _style_payload(brand_kit: dict[str, Any]) -> dict[str, Any]:
        return {
            "color_palette": brand_kit.get("color_system", {}),
            "typography": brand_kit.get("typography_guidance", {}),
            "animation_style": brand_kit.get("animation_style", {}),
            "brand_logo": brand_kit.get("logo", {}).get("delivery_stub"),
            "intro_outro_assets": brand_kit.get("intro_outro_assets", {}),
        }

    def launch_custom_project(
        self,
        *,
        user_intent: str,
        brief: str,
        use_case: str = "personal",
        brand_kit: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized = user_intent.lower().replace("-", " ").replace("_", " ")
        matching = [name for name in _PROJECT_TEMPLATES if all(token in normalized for token in name.split("_")[:2])]
        project_type = matching[0] if matching else "social_campaign_pack"
        result = self.launch_project(
            project_type=project_type,
            brief=brief,
            use_case=use_case,
            brand_kit=brand_kit,
        )
        result["user_intent"] = user_intent
        result["resolved_project_type"] = project_type
        return result

    def launch_project(
        self,
        *,
        project_type: str,
        brief: str,
        use_case: str = "personal",
        brand_kit: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if project_type not in _PROJECT_TEMPLATES:
            raise ValueError(f"Unsupported project_type '{project_type}'")
        if use_case not in {"personal", "business"}:
            raise ValueError("use_case must be 'personal' or 'business'")

        template = _PROJECT_TEMPLATES[project_type][use_case]
        resolved_brand_kit = brand_kit or self.create_brand_kit(
            brand_name="Buddy Creative",
            audience="families and creators" if use_case == "personal" else "brands and businesses",
            use_case=use_case,
            tone="playful" if project_type == "youtube_baby_song" else "cinematic",
        )

        style_payload = self._style_payload(resolved_brand_kit)
        style_application: dict[str, Any] = {
            "status": "not_applied",
            "reason": "tier_gated_or_unavailable",
        }
        try:
            style_application = self.media_bot.customize_visual_style(style_payload)
        except Exception:
            style_application = {
                "status": "not_applied",
                "reason": "tier_gated_or_unavailable",
                "style_payload": style_payload,
            }

        music = self.media_bot.text_to_music(
            f"{brief}\nBrand slogan: {resolved_brand_kit['slogan']}\nTone: {resolved_brand_kit['tone_profile']['voice']}",
            style=template["music_style"],
        )
        script = (
            f"{brief}\n\n"
            f"Production mode: {project_type}\n"
            f"Use case: {use_case}\n"
            f"Slogan: {resolved_brand_kit['slogan']}\n"
            f"Positioning: {resolved_brand_kit['positioning_statement']}\n"
            f"Typography guidance: {resolved_brand_kit['typography_guidance']['headlines']}\n"
            f"Color system primary: {resolved_brand_kit['color_system']['primary']}\n"
            f"Intro asset: {resolved_brand_kit['intro_outro_assets']['intro_video_stub']}"
        )
        video = self.media_bot.create_video(
            script=script,
            image_sample=resolved_brand_kit["logo"]["delivery_stub"],
        )
        visual = self.photo_bot.generate_cartoon_frame(
            description=f"{project_type} key art for {resolved_brand_kit['brand_name']} | {brief}",
            style="disney" if project_type == "youtube_baby_song" else "pixar",
        )

        assets = [music["asset"]["asset_id"], video["asset"]["asset_id"], visual["asset"]["asset_id"]]
        lineage = {
            "audio_asset_id": music["asset"]["asset_id"],
            "video_asset_id": video["asset"]["asset_id"],
            "visual_asset_id": visual["asset"]["asset_id"],
            "thumbnail_asset_id": video.get("thumbnail_asset", {}).get("asset_id"),
        }
        return {
            "project_type": project_type,
            "use_case": use_case,
            "template": template,
            "brand_kit": resolved_brand_kit,
            "brand_style_application": style_application,
            "music": music,
            "video": video,
            "visual": visual,
            "lineage": lineage,
            "status": "lifecycle_ready",
            "assets": assets,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
