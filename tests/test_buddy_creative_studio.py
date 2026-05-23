from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from bots.buddy_media_transformation_bot import BuddyCreativeStudio
from bots.buddy_media_transformation_bot.tiers import Tier


def test_brand_kit_contains_flagship_fields():
    studio = BuddyCreativeStudio(tier=Tier.ENTERPRISE)
    brand = studio.create_brand_kit(
        brand_name="Buddy Launch",
        audience="parents and creators",
        use_case="business",
    )
    assert brand["logo"]["delivery_stub"].startswith("https://")
    assert "slogan" in brand
    assert "positioning_statement" in brand
    assert "style_profile" in brand
    assert "typography_guidance" in brand
    assert "color_system" in brand
    assert "animation_style" in brand
    assert "intro_outro_assets" in brand


def test_launch_project_unifies_music_video_photo_lineage():
    studio = BuddyCreativeStudio(tier=Tier.ENTERPRISE)
    result = studio.launch_project(
        project_type="youtube_baby_song",
        brief="Create a catchy baby song about bedtime routines",
        use_case="business",
    )
    assert result["status"] == "lifecycle_ready"
    assert result["music"]["asset"]["status"] == "active"
    assert result["video"]["asset"]["status"] == "active"
    assert result["visual"]["asset"]["status"] == "active"
    assert result["lineage"]["audio_asset_id"] in result["assets"]
    assert "brand_style_application" in result


def test_templates_include_school_parent_and_business_training():
    studio = BuddyCreativeStudio(tier=Tier.ENTERPRISE)
    templates = studio.list_project_templates()
    assert "school_parent_update_video" in templates
    assert "business_training_video" in templates
    assert "video_game_trailer" in templates


def test_custom_intent_maps_to_launchable_project():
    studio = BuddyCreativeStudio(tier=Tier.ENTERPRISE)
    result = studio.launch_custom_project(
        user_intent="video game trailer for school robotics team",
        brief="Build an exciting trailer showing student robotics gameplay simulations",
        use_case="business",
    )
    assert result["resolved_project_type"] in studio.list_project_templates()
    assert result["status"] == "lifecycle_ready"
