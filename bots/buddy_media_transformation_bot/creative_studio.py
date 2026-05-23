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
            "primary_colors": ["#2E7DFF", "#FF6F3C", "#141B2D"],
            "typography": {"headline": "Montserrat Bold", "body": "Inter Regular"},
            "voice_guidelines": ["clear hooks", "emotion-first language", "high-trust CTA"],
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
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

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

        music = self.media_bot.text_to_music(brief, style=template["music_style"])
        script = (
            f"{brief}\n\n"
            f"Production mode: {project_type}\n"
            f"Use case: {use_case}\n"
            f"Slogan: {resolved_brand_kit['slogan']}\n"
            f"Positioning: {resolved_brand_kit['positioning_statement']}"
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
            "music": music,
            "video": video,
            "visual": visual,
            "lineage": lineage,
            "status": "lifecycle_ready",
            "assets": assets,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
