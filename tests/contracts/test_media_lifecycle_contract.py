from __future__ import annotations

from typing import Callable

from bots.buddy_media_transformation_bot.buddy_media_transformation_bot import BuddyMediaTransformationBot
from bots.buddy_media_transformation_bot.tiers import Tier as BuddyTier
from bots.media_runtime import (
    MEDIA_LIFECYCLE_REQUIRED_FIELDS,
    MEDIA_LIFECYCLE_STATES,
    validate_media_lifecycle_contract,
)
from bots.photo_editing_bot.photo_editing_bot import PhotoEditingBot
from bots.photo_editing_bot.tiers import Tier as PhotoTier
from bots.professional_music_editing_bot.professional_music_editing_bot import ProfessionalMusicEditingBot
from bots.professional_music_editing_bot.tiers import Tier as MusicTier
from bots.professional_video_editing_bot.professional_video_editing_bot import ProfessionalVideoEditingBot
from bots.professional_video_editing_bot.tiers import Tier as VideoTier


def _payloads() -> list[tuple[str, Callable[[], dict]]]:
    return [
        ("photo.edit_photo", lambda: PhotoEditingBot(tier=PhotoTier.FREE).edit_photo("photo.jpg")),
        (
            "buddy.text_to_music",
            lambda: BuddyMediaTransformationBot(tier=BuddyTier.PRO).text_to_music("launch anthem", style="pop"),
        ),
        ("buddy.create_video", lambda: BuddyMediaTransformationBot(tier=BuddyTier.PRO).create_video("launch video script")),
        (
            "professional_music.export_project",
            lambda: (
                lambda bot: bot.export_project(bot.load_project()["project_id"], export_format="WAV")
            )(ProfessionalMusicEditingBot(tier=MusicTier.PRO)),
        ),
        (
            "professional_video.export_project",
            lambda: (
                lambda bot: bot.export_project(bot.load_project()["project_id"], export_format="MP4")
            )(ProfessionalVideoEditingBot(tier=VideoTier.PRO)),
        ),
    ]


def _assert_schema(payload: dict) -> None:
    missing = [field for field in MEDIA_LIFECYCLE_REQUIRED_FIELDS if field not in payload]
    assert not missing, f"missing lifecycle fields: {missing}"
    valid, errors = validate_media_lifecycle_contract(payload)
    assert valid is True, f"invalid lifecycle contract: {errors}"


def _assert_lifecycle_state(payload: dict) -> None:
    assert payload["status"] in MEDIA_LIFECYCLE_STATES


def _assert_lineage(payload: dict) -> None:
    assert isinstance(payload["lineage"], dict)
    assert len(payload["lineage"]) > 0


def _assert_asset_persistence(payload: dict) -> None:
    assert payload["asset_ids"], "asset_ids must not be empty"
    assert all(str(asset_id).startswith("asset_") for asset_id in payload["asset_ids"])


def _assert_signed_urls(payload: dict) -> None:
    assert payload["signed_urls"], "signed_urls must not be empty"
    for url in payload["signed_urls"]:
        assert str(url).startswith("https://")
        assert ("exp=" in str(url)) or ("expires=" in str(url))
        assert ("sig=" in str(url)) or ("signature=" in str(url))


def test_media_lifecycle_contract_suite():
    for name, payload_builder in _payloads():
        payload = payload_builder()
        _assert_schema(payload)
        _assert_lifecycle_state(payload)
        _assert_lineage(payload)
        _assert_asset_persistence(payload)
        _assert_signed_urls(payload)
