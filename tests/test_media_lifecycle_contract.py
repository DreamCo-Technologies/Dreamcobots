from __future__ import annotations

from bots.buddy_media_transformation_bot.buddy_media_transformation_bot import BuddyMediaTransformationBot
from bots.buddy_media_transformation_bot.tiers import Tier as BuddyTier
from bots.media_runtime import MEDIA_LIFECYCLE_REQUIRED_FIELDS, validate_media_lifecycle_contract
from bots.photo_editing_bot.photo_editing_bot import PhotoEditingBot
from bots.photo_editing_bot.tiers import Tier as PhotoTier
from bots.professional_music_editing_bot.professional_music_editing_bot import ProfessionalMusicEditingBot
from bots.professional_music_editing_bot.tiers import Tier as MusicTier
from bots.professional_video_editing_bot.professional_video_editing_bot import ProfessionalVideoEditingBot
from bots.professional_video_editing_bot.tiers import Tier as VideoTier


def _assert_contract(payload: dict) -> None:
    for field in MEDIA_LIFECYCLE_REQUIRED_FIELDS:
        assert field in payload
    valid, errors = validate_media_lifecycle_contract(payload)
    assert valid is True, f"invalid lifecycle contract fields: {errors}"


def test_photo_bot_contract_for_edit_photo():
    bot = PhotoEditingBot(tier=PhotoTier.FREE)
    result = bot.edit_photo("photo.jpg")
    _assert_contract(result)


def test_buddy_bot_contract_for_text_to_music():
    bot = BuddyMediaTransformationBot(tier=BuddyTier.PRO)
    result = bot.text_to_music("launch anthem for new product", style="pop")
    _assert_contract(result)


def test_buddy_bot_contract_for_create_video():
    bot = BuddyMediaTransformationBot(tier=BuddyTier.PRO)
    result = bot.create_video("Short product launch script")
    _assert_contract(result)


def test_professional_music_export_contract():
    bot = ProfessionalMusicEditingBot(tier=MusicTier.PRO)
    project = bot.load_project()
    result = bot.export_project(project["project_id"], export_format="WAV")
    _assert_contract(result)


def test_professional_video_export_contract():
    bot = ProfessionalVideoEditingBot(tier=VideoTier.PRO)
    project = bot.load_project()
    result = bot.export_project(project["project_id"], export_format="MP4")
    _assert_contract(result)
