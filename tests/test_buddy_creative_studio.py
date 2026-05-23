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
