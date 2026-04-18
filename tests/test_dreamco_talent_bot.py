"""Tests for bots/dreamco_talent_bot — DreamCo AI Music Producer & Talent Agency."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.dreamco_talent_bot.dreamco_talent_bot import (
    DreamCoTalentBot,
    DreamCoTalentBotError,
    DreamCoTalentBotTierError,
    MusicProductionEngine,
    VoiceCloneEngine,
    RightsEngine,
    TalentAgencyEngine,
    FinancialEngine,
    ContentCreatorEngine,
    MarketplaceEngine,
    SelfHealEngine,
    BeatTrack,
    VoiceProfile,
    RightsRecord,
    ArtistProfile,
    ShowBooking,
    GrantOpportunity,
    MarketplaceListing,
    SUPPORTED_GENRES,
    SUPPORTED_PLATFORMS,
    SUPPORTED_CONTENT_TYPES,
    SUPPORTED_RIGHT_TYPES,
    SUPPORTED_GRANT_CATEGORIES,
)
from bots.dreamco_talent_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# Tier definitions
# ===========================================================================

class TestTierDefinitions:
    def test_all_tiers_have_features(self):
        for tier in Tier:
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_pro(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.PRO.value])

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_has_white_label(self):
        enterprise_features = " ".join(BOT_FEATURES[Tier.ENTERPRISE.value])
        assert "white-label" in enterprise_features

    def test_enterprise_has_voice_cloning(self):
        enterprise_features = " ".join(BOT_FEATURES[Tier.ENTERPRISE.value])
        assert "voice cloning" in enterprise_features

    def test_enterprise_has_patent(self):
        enterprise_features = " ".join(BOT_FEATURES[Tier.ENTERPRISE.value])
        assert "patent" in enterprise_features

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert "features" in info

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] > get_bot_tier_info(Tier.PRO)["price_usd_monthly"]

    def test_tier_info_has_support_level(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info
            assert info["support_level"]

    def test_tier_info_has_requests_per_month(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "requests_per_month" in info


# ===========================================================================
# Bot instantiation
# ===========================================================================

class TestBotInstantiation:
    def test_free_tier_creation(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        assert bot.tier == Tier.FREE

    def test_pro_tier_creation(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier_creation(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_default_tier_is_free(self):
        bot = DreamCoTalentBot()
        assert bot.tier == Tier.FREE

    def test_has_all_eight_engines(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        assert hasattr(bot, '_music')
        assert hasattr(bot, '_voice')
        assert hasattr(bot, '_rights')
        assert hasattr(bot, '_agency')
        assert hasattr(bot, '_financial')
        assert hasattr(bot, '_content')
        assert hasattr(bot, '_marketplace')
        assert hasattr(bot, '_self_heal')

    def test_has_global_ai_sources_flow(self):
        bot = DreamCoTalentBot()
        assert hasattr(bot, 'flow')


# ===========================================================================
# Data models
# ===========================================================================

class TestDataModels:
    def test_beat_track_to_dict(self):
        beat = BeatTrack(
            genre="hip-hop", bpm=90, key="C", duration_seconds=30,
            title="Test Beat", audio_url="https://cdn.dreamco.ai/test.mp3"
        )
        d = beat.to_dict()
        assert d["genre"] == "hip-hop"
        assert d["bpm"] == 90
        assert d["key"] == "C"
        assert d["copyright_safe"] is True
        assert "track_id" in d
        assert "timestamp" in d

    def test_voice_profile_to_dict(self):
        vp = VoiceProfile(
            voice_name="MyVoice", language="en", tone="warm", source_sample="sample.wav"
        )
        d = vp.to_dict()
        assert d["voice_name"] == "MyVoice"
        assert d["language"] == "en"
        assert "voice_id" in d

    def test_rights_record_to_dict(self):
        rec = RightsRecord(
            title="My Song", rights_type="copyright", owner="Jane Doe",
            description="Musical work"
        )
        d = rec.to_dict()
        assert d["title"] == "My Song"
        assert d["rights_type"] == "copyright"
        assert d["owner"] == "Jane Doe"
        assert "registration_number" in d

    def test_artist_profile_to_dict(self):
        ap = ArtistProfile(name="DJ Nova", genre="house", bio="DJ from NY")
        d = ap.to_dict()
        assert d["name"] == "DJ Nova"
        assert d["genre"] == "house"
        assert "artist_id" in d

    def test_show_booking_to_dict(self):
        sb = ShowBooking(artist_name="MC Flow", venue="Club X", event_date="2025-10-01")
        d = sb.to_dict()
        assert d["artist_name"] == "MC Flow"
        assert d["venue"] == "Club X"
        assert "booking_id" in d

    def test_grant_opportunity_to_dict(self):
        g = GrantOpportunity(
            name="Music Grant", category="music_production", amount_usd=10000.0,
            deadline="2025-12-01", eligibility="All musicians",
            apply_url="https://example.com"
        )
        d = g.to_dict()
        assert d["name"] == "Music Grant"
        assert d["amount_usd"] == 10000.0
        assert "opportunity_id" in d

    def test_marketplace_listing_to_dict(self):
        ml = MarketplaceListing(
            title="Fire Beat", asset_type="beat", price_usd=29.99, track_id="abc123"
        )
        d = ml.to_dict()
        assert d["title"] == "Fire Beat"
        assert d["price_usd"] == 29.99
        assert "listing_id" in d

    def test_beat_track_unique_ids(self):
        beats = [
            BeatTrack(genre="pop", bpm=120, key="G", duration_seconds=30,
                      title=f"Beat {i}", audio_url="https://cdn.dreamco.ai/test.mp3")
            for i in range(5)
        ]
        ids = {b.track_id for b in beats}
        assert len(ids) == 5


# ===========================================================================
# Music Production Engine
# ===========================================================================

class TestMusicProductionEngine:
    def test_generate_beat_returns_beat_track(self):
        engine = MusicProductionEngine(daily_limit=10)
        beat = engine.generate_beat("hip-hop", bpm=95)
        assert isinstance(beat, BeatTrack)
        assert beat.genre == "hip-hop"
        assert beat.bpm == 95
        assert beat.copyright_safe is True

    def test_generate_beat_auto_bpm(self):
        engine = MusicProductionEngine(daily_limit=10)
        beat = engine.generate_beat("trap")
        assert beat.bpm > 0

    def test_generate_beat_unknown_genre_defaults(self):
        engine = MusicProductionEngine(daily_limit=10)
        beat = engine.generate_beat("unknown_genre_xyz")
        assert beat.genre == "hip-hop"

    def test_generate_beat_increments_daily_count(self):
        engine = MusicProductionEngine(daily_limit=10)
        engine.generate_beat("pop")
        assert engine._generated_today == 1

    def test_generate_beat_respects_daily_limit(self):
        engine = MusicProductionEngine(daily_limit=2)
        engine.generate_beat("pop")
        engine.generate_beat("pop")
        with pytest.raises(DreamCoTalentBotTierError):
            engine.generate_beat("pop")

    def test_generate_beat_no_limit_for_enterprise(self):
        engine = MusicProductionEngine(daily_limit=None)
        for _ in range(100):
            engine.generate_beat("jazz")
        assert engine._generated_today == 100

    def test_generate_song_returns_dict(self):
        engine = MusicProductionEngine(daily_limit=20)
        beat = engine.generate_beat("r&b")
        song = engine.generate_song("Love Story", "r&b", "Verse 1 lyrics here", beat)
        assert song["title"] == "Love Story"
        assert song["genre"] == "r&b"
        assert song["beat_id"] == beat.track_id
        assert song["copyright_safe"] is True

    def test_generate_content_reel(self):
        engine = MusicProductionEngine(daily_limit=20)
        content = engine.generate_content("reel", "summer vibes", 30)
        assert content["content_type"] == "reel"
        assert content["duration_seconds"] == 30
        assert "video_url" in content

    def test_generate_content_unknown_type_defaults(self):
        engine = MusicProductionEngine(daily_limit=20)
        content = engine.generate_content("unknown_type", "topic")
        assert content["content_type"] == "reel"

    def test_master_track_returns_dict(self):
        engine = MusicProductionEngine(daily_limit=10)
        result = engine.master_track("track123")
        assert result["track_id"] == "track123"
        assert result["mastered"] is True
        assert "mastered_url" in result


# ===========================================================================
# Bot — Music Production delegation
# ===========================================================================

class TestBotMusicProduction:
    def test_generate_beat_free(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        beat = bot.generate_beat("hip-hop", bpm=90)
        assert beat["genre"] == "hip-hop"
        assert beat["bpm"] == 90
        assert beat["copyright_safe"] is True

    def test_generate_beat_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        beat = bot.generate_beat("trap")
        assert beat["copyright_safe"] is True

    def test_generate_beat_enterprise_no_limit(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        for _ in range(60):
            bot.generate_beat("pop")

    def test_generate_beat_free_hits_limit(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        for _ in range(5):
            bot.generate_beat("hip-hop")
        with pytest.raises(DreamCoTalentBotTierError):
            bot.generate_beat("hip-hop")

    def test_generate_song(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        song = bot.generate_song("Midnight", "r&b", "The stars above")
        assert song["title"] == "Midnight"
        assert "audio_url" in song

    def test_generate_content_podcast(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        content = bot.generate_content("podcast", "music business tips", 1800)
        assert content["content_type"] == "podcast"

    def test_master_track(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        result = bot.master_track("trk001")
        assert result["mastered"] is True


# ===========================================================================
# Voice Clone Engine
# ===========================================================================

class TestVoiceCloneEngine:
    def test_clone_voice_pro_limit(self):
        engine = VoiceCloneEngine(clone_limit=3)
        v1 = engine.clone_voice("sample1.wav", "Voice1")
        v2 = engine.clone_voice("sample2.wav", "Voice2")
        v3 = engine.clone_voice("sample3.wav", "Voice3")
        assert len(engine._cloned_voices) == 3
        with pytest.raises(DreamCoTalentBotTierError):
            engine.clone_voice("sample4.wav", "Voice4")

    def test_clone_voice_no_limit(self):
        engine = VoiceCloneEngine(clone_limit=None)
        for i in range(10):
            engine.clone_voice(f"sample{i}.wav", f"Voice{i}")
        assert len(engine._cloned_voices) == 10

    def test_clone_voice_returns_profile(self):
        engine = VoiceCloneEngine(clone_limit=5)
        vp = engine.clone_voice("sample.wav", "TestVoice", "en")
        assert isinstance(vp, VoiceProfile)
        assert vp.voice_name == "TestVoice"
        assert vp.language == "en"

    def test_clone_voice_unknown_language_defaults(self):
        engine = VoiceCloneEngine(clone_limit=5)
        vp = engine.clone_voice("sample.wav", "TestVoice", "xx")
        assert vp.language == "en"

    def test_generate_voiceover(self):
        engine = VoiceCloneEngine(clone_limit=5)
        vo = engine.generate_voiceover("Hello world")
        assert "audio_url" in vo
        assert vo["text"] == "Hello world"

    def test_dub_audio(self):
        engine = VoiceCloneEngine(clone_limit=5)
        result = engine.dub_audio("https://cdn.dreamco.ai/test.mp3", "es")
        assert result["target_language"] == "es"
        assert "dubbed_url" in result

    def test_list_voices(self):
        engine = VoiceCloneEngine(clone_limit=5)
        engine.clone_voice("sample.wav", "Voice1")
        voices = engine.list_voices()
        assert len(voices) == 1
        assert voices[0]["voice_name"] == "Voice1"


# ===========================================================================
# Bot — Voice Clone delegation
# ===========================================================================

class TestBotVoiceClone:
    def test_clone_voice_free_raises(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            bot.clone_voice("sample.wav", "MyVoice")

    def test_clone_voice_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        vp = bot.clone_voice("sample.wav", "ProVoice")
        assert vp["voice_name"] == "ProVoice"

    def test_clone_voice_enterprise_unlimited(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        for i in range(10):
            bot.clone_voice(f"sample{i}.wav", f"Voice{i}")
        voices = bot.list_voices()
        assert len(voices) == 10

    def test_generate_voiceover_all_tiers(self):
        for tier in Tier:
            bot = DreamCoTalentBot(tier=tier)
            vo = bot.generate_voiceover("Welcome to the show.")
            assert "audio_url" in vo

    def test_dub_audio_enterprise(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        result = bot.dub_audio("https://cdn.dreamco.ai/test.mp3", "fr")
        assert result["target_language"] == "fr"

    def test_dub_audio_pro_raises(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        with pytest.raises(DreamCoTalentBotTierError):
            bot.dub_audio("https://cdn.dreamco.ai/test.mp3", "es")


# ===========================================================================
# Rights Engine
# ===========================================================================

class TestRightsEngine:
    def test_search_copyright_free(self):
        engine = RightsEngine(tier=Tier.FREE)
        results = engine.search_copyright("My Song")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_register_copyright_free_raises(self):
        engine = RightsEngine(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.register_copyright("My Song", "musical_work", "Jane Doe")

    def test_register_copyright_pro(self):
        engine = RightsEngine(tier=Tier.PRO)
        rec = engine.register_copyright("My Song", "musical_work", "Jane Doe")
        assert isinstance(rec, RightsRecord)
        assert rec.rights_type == "copyright"
        assert rec.status == "filed"

    def test_search_trademark_free_raises(self):
        engine = RightsEngine(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.search_trademark("DreamCo")

    def test_search_trademark_pro(self):
        engine = RightsEngine(tier=Tier.PRO)
        results = engine.search_trademark("DreamCo")
        assert isinstance(results, list)

    def test_register_trademark_pro(self):
        engine = RightsEngine(tier=Tier.PRO)
        rec = engine.register_trademark("DreamCo", "DreamCo Inc.", "Music platform")
        assert rec.rights_type == "trademark"
        assert rec.status == "filed"

    def test_search_patent_pro(self):
        engine = RightsEngine(tier=Tier.PRO)
        results = engine.search_patent("AI music generator")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_search_patent_free_raises(self):
        engine = RightsEngine(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.search_patent("AI music generator")

    def test_file_patent_enterprise(self):
        engine = RightsEngine(tier=Tier.ENTERPRISE)
        rec = engine.file_patent("AI Beat Machine", "DreamCo Inc.", "A machine for generating beats")
        assert rec.rights_type == "patent"
        assert rec.status == "filed"

    def test_file_patent_pro_raises(self):
        engine = RightsEngine(tier=Tier.PRO)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.file_patent("My Invention", "Jane", "Description")

    def test_list_registrations(self):
        engine = RightsEngine(tier=Tier.PRO)
        engine.register_copyright("Song A", "musical_work", "Jane")
        engine.register_trademark("Brand B", "Jane", "Music brand")
        recs = engine.list_registrations()
        assert len(recs) == 2


# ===========================================================================
# Bot — Rights Management delegation
# ===========================================================================

class TestBotRightsManagement:
    def test_search_copyright_all_tiers(self):
        for tier in Tier:
            bot = DreamCoTalentBot(tier=tier)
            results = bot.search_copyright("Test Song")
            assert isinstance(results, list)

    def test_register_copyright_free_raises(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            bot.register_copyright("Test", "musical_work", "Author")

    def test_register_copyright_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        rec = bot.register_copyright("My Track", "musical_work", "DJ Nova")
        assert rec["rights_type"] == "copyright"

    def test_search_trademark_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        results = bot.search_trademark("MyBrand")
        assert isinstance(results, list)

    def test_register_trademark_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        rec = bot.register_trademark("MyBrand", "DJ Nova", "Music label brand")
        assert rec["rights_type"] == "trademark"

    def test_search_patent_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        results = bot.search_patent("voice synthesizer")
        assert isinstance(results, list)

    def test_file_patent_enterprise(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        rec = bot.file_patent("Voice AI Device", "DreamCo", "Synthesizes voices using AI")
        assert rec["rights_type"] == "patent"

    def test_list_rights_registrations(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        bot.register_copyright("Track A", "musical_work", "Author")
        regs = bot.list_rights_registrations()
        assert len(regs) == 1


# ===========================================================================
# Talent Agency Engine
# ===========================================================================

class TestTalentAgencyEngine:
    def test_create_artist_profile(self):
        engine = TalentAgencyEngine(booking_limit=20)
        ap = engine.create_artist_profile("DJ Flow", "house", "Electronic DJ from Miami")
        assert isinstance(ap, ArtistProfile)
        assert ap.name == "DJ Flow"

    def test_book_show(self):
        engine = TalentAgencyEngine(booking_limit=20)
        booking = engine.book_show("DJ Flow", "Club X", "2025-10-15", payout_usd=500.0)
        assert isinstance(booking, ShowBooking)
        assert booking.status == "confirmed"
        assert booking.payout_usd == 500.0

    def test_book_show_respects_limit(self):
        engine = TalentAgencyEngine(booking_limit=2)
        engine.book_show("Artist A", "Venue 1", "2025-10-01")
        engine.book_show("Artist B", "Venue 2", "2025-10-02")
        with pytest.raises(DreamCoTalentBotTierError):
            engine.book_show("Artist C", "Venue 3", "2025-10-03")

    def test_book_show_no_limit(self):
        engine = TalentAgencyEngine(booking_limit=None)
        for i in range(50):
            engine.book_show(f"Artist {i}", f"Venue {i}", f"2025-10-{(i % 28) + 1:02d}")
        assert len(engine._bookings) == 50

    def test_create_show_outlet(self):
        engine = TalentAgencyEngine(booking_limit=5)
        outlet = engine.create_show_outlet("DreamCo Live", "youtube", "Live music channel")
        assert outlet["status"] == "live"
        assert "url" in outlet

    def test_list_artists(self):
        engine = TalentAgencyEngine(booking_limit=5)
        engine.create_artist_profile("Artist 1", "rap", "Bio 1")
        engine.create_artist_profile("Artist 2", "pop", "Bio 2")
        artists = engine.list_artists()
        assert len(artists) == 2

    def test_get_booking_stats(self):
        engine = TalentAgencyEngine(booking_limit=None)
        engine.create_artist_profile("MC Nova", "rap", "Bio")
        engine.book_show("MC Nova", "Arena A", "2025-11-01", payout_usd=1000.0)
        stats = engine.get_booking_stats()
        assert stats["total_bookings"] == 1
        assert stats["total_payout_usd"] == 1000.0
        assert stats["artists_managed"] == 1


# ===========================================================================
# Bot — Talent Agency delegation
# ===========================================================================

class TestBotTalentAgency:
    def test_create_artist_profile(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        ap = bot.create_artist_profile("MC Flow", "trap", "Rapper from Atlanta",
                                       social_handles={"instagram": "@mcflow"}, booking_rate_usd=250.0)
        assert ap["name"] == "MC Flow"
        assert ap["booking_rate_usd"] == 250.0

    def test_book_show_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        booking = bot.book_show("MC Flow", "The Venue", "2025-12-01", payout_usd=750.0)
        assert booking["status"] == "confirmed"

    def test_book_show_free_limit(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        bot.book_show("Artist A", "Venue A", "2025-10-01")
        with pytest.raises(DreamCoTalentBotTierError):
            bot.book_show("Artist B", "Venue B", "2025-10-02")

    def test_book_show_enterprise_unlimited(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        for i in range(30):
            bot.book_show(f"Artist {i}", f"Venue {i}", "2025-10-01")
        bookings = bot.list_bookings()
        assert len(bookings) == 30

    def test_create_show_outlet(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        outlet = bot.create_show_outlet("DreamCo Stars", "tiktok", "Go viral with DreamCo")
        assert outlet["status"] == "live"

    def test_get_booking_stats(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        bot.book_show("Artist A", "Club", "2025-10-01", payout_usd=300.0)
        stats = bot.get_booking_stats()
        assert stats["confirmed_bookings"] == 1
        assert stats["total_payout_usd"] == 300.0


# ===========================================================================
# Financial Engine
# ===========================================================================

class TestFinancialEngine:
    def test_find_grants_by_category(self):
        engine = FinancialEngine(tier=Tier.PRO)
        grants = engine.find_grants("music_production")
        assert len(grants) > 0
        assert all(isinstance(g, GrantOpportunity) for g in grants)

    def test_find_grants_unknown_category_returns_defaults(self):
        engine = FinancialEngine(tier=Tier.PRO)
        grants = engine.find_grants("zzz_unknown_zzz")
        assert len(grants) > 0

    def test_apply_for_grant_free_raises(self):
        engine = FinancialEngine(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.apply_for_grant("grant_001", "Jane", "Music project")

    def test_apply_for_grant_pro(self):
        engine = FinancialEngine(tier=Tier.PRO)
        result = engine.apply_for_grant("grant_001", "Jane Doe", "Hip-hop album")
        assert result["status"] == "submitted"
        assert result["applicant"] == "Jane Doe"

    def test_record_royalty_free_raises(self):
        engine = FinancialEngine(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.record_royalty("track_001", "spotify", 1000)

    def test_record_royalty_pro(self):
        engine = FinancialEngine(tier=Tier.PRO)
        rec = engine.record_royalty("track_001", "spotify", 10000, rate_per_stream=0.004)
        assert rec["earned_usd"] == 40.0
        assert rec["streams"] == 10000

    def test_royalty_summary(self):
        engine = FinancialEngine(tier=Tier.PRO)
        engine.record_royalty("t1", "spotify", 5000)
        engine.record_royalty("t2", "apple_music", 3000)
        summary = engine.royalty_summary()
        assert summary["total_royalty_records"] == 2
        assert summary["total_streams"] == 8000


# ===========================================================================
# Bot — Financial delegation
# ===========================================================================

class TestBotFinancial:
    def test_find_grants_free(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        grants = bot.find_grants("music_production")
        assert isinstance(grants, list)
        assert len(grants) > 0

    def test_find_grants_podcast(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        grants = bot.find_grants("podcast")
        assert all("opportunity_id" in g for g in grants)

    def test_apply_for_grant_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        result = bot.apply_for_grant("opp_001", "MC Flow", "Hip-hop production")
        assert result["status"] == "submitted"

    def test_apply_for_grant_free_raises(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            bot.apply_for_grant("opp_001", "MC Flow", "project")

    def test_record_royalty_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        rec = bot.record_royalty("track_001", "tiktok", 50000)
        assert rec["earned_usd"] > 0

    def test_royalty_summary(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        bot.record_royalty("t1", "spotify", 10000)
        summary = bot.royalty_summary()
        assert summary["total_streams"] == 10000


# ===========================================================================
# Content Creator Engine
# ===========================================================================

class TestContentCreatorEngine:
    def test_generate_hook(self):
        engine = ContentCreatorEngine(tier=Tier.FREE)
        hook = engine.generate_hook("MC Nova", "beat making")
        assert "MC Nova" in hook or "beat making" in hook

    def test_create_content_plan(self):
        engine = ContentCreatorEngine(tier=Tier.PRO)
        plan = engine.create_content_plan("DJ Flow", "electronic music", ["tiktok", "instagram"])
        assert plan["creator_name"] == "DJ Flow"
        assert "tiktok" in plan["weekly_posts"]
        assert len(plan["hooks"]) == 3

    def test_create_podcast_episode(self):
        engine = ContentCreatorEngine(tier=Tier.PRO)
        ep = engine.create_podcast_episode("The Beat Show", "Episode 1", "AI music", 45)
        assert ep["show_name"] == "The Beat Show"
        assert ep["duration_minutes"] == 45
        assert "intro_script" in ep

    def test_create_onlyfans_content_enterprise(self):
        engine = ContentCreatorEngine(tier=Tier.ENTERPRISE)
        result = engine.create_onlyfans_content("Creator X", "video", "Exclusive behind-the-scenes")
        assert "content_id" in result
        assert result["creator_name"] == "Creator X"

    def test_create_onlyfans_content_pro_raises(self):
        engine = ContentCreatorEngine(tier=Tier.PRO)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.create_onlyfans_content("Creator X", "video", "Content")

    def test_distribute_to_platforms_pro(self):
        engine = ContentCreatorEngine(tier=Tier.PRO)
        result = engine.distribute_to_platforms(
            "https://cdn.dreamco.ai/test.mp4",
            ["tiktok", "instagram"],
            "Check this out!"
        )
        assert "tiktok" in result["platforms"]
        assert "instagram" in result["platforms"]

    def test_distribute_to_platforms_free_raises(self):
        engine = ContentCreatorEngine(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.distribute_to_platforms("https://example.com/test.mp4", ["tiktok"])


# ===========================================================================
# Bot — Content Creator delegation
# ===========================================================================

class TestBotContentCreator:
    def test_generate_hook_all_tiers(self):
        for tier in Tier:
            bot = DreamCoTalentBot(tier=tier)
            hook = bot.generate_hook("DJ Nova", "rap beats")
            assert isinstance(hook, str)
            assert len(hook) > 0

    def test_create_content_plan(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        plan = bot.create_content_plan("MC Flow", "trap music", ["tiktok", "youtube"])
        assert "weekly_posts" in plan
        assert "hooks" in plan

    def test_create_podcast_episode(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        ep = bot.create_podcast_episode("DreamCo Podcast", "Ep 1", "How to make beats")
        assert ep["show_name"] == "DreamCo Podcast"

    def test_create_onlyfans_content_enterprise(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        result = bot.create_onlyfans_content("Creator", "photo", "Studio session")
        assert "content_id" in result

    def test_create_onlyfans_content_pro_raises(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        with pytest.raises(DreamCoTalentBotTierError):
            bot.create_onlyfans_content("Creator", "video", "Content")

    def test_distribute_to_platforms_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        result = bot.distribute_to_platforms(
            "https://cdn.dreamco.ai/test.mp4",
            ["spotify", "tiktok"]
        )
        assert "spotify" in result["platforms"]

    def test_distribute_to_platforms_free_raises(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        with pytest.raises(DreamCoTalentBotTierError):
            bot.distribute_to_platforms("https://cdn.dreamco.ai/test.mp4", ["tiktok"])


# ===========================================================================
# Marketplace Engine
# ===========================================================================

class TestMarketplaceEngine:
    def _make_beat(self) -> BeatTrack:
        return BeatTrack(
            genre="hip-hop", bpm=90, key="C",
            duration_seconds=30, title="Test Beat",
            audio_url="https://cdn.dreamco.ai/test.mp3"
        )

    def test_list_beat_for_sale(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        beat = self._make_beat()
        listing = engine.list_beat_for_sale(beat, price_usd=29.99)
        assert isinstance(listing, MarketplaceListing)
        assert listing.price_usd == 29.99
        assert listing.asset_type == "beat"

    def test_list_song_for_sale(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        song = {"title": "My Song", "song_id": "s001", "genre": "pop"}
        listing = engine.list_song_for_sale(song, price_usd=4.99)
        assert listing.asset_type == "song"
        assert listing.price_usd == 4.99

    def test_purchase_listing(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        beat = self._make_beat()
        listing = engine.list_beat_for_sale(beat, price_usd=19.99)
        purchase = engine.purchase_listing(listing.listing_id, "buyer@example.com")
        assert purchase["listing_id"] == listing.listing_id
        assert purchase["price_paid_usd"] == 19.99
        assert "download_url" in purchase

    def test_purchase_increments_sales(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        beat = self._make_beat()
        listing = engine.list_beat_for_sale(beat, price_usd=9.99)
        engine.purchase_listing(listing.listing_id, "a@example.com")
        engine.purchase_listing(listing.listing_id, "b@example.com")
        assert listing.sales == 2

    def test_purchase_nonexistent_listing_raises(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        with pytest.raises(DreamCoTalentBotError):
            engine.purchase_listing("nonexistent_id", "buyer@example.com")

    def test_create_white_label_store_enterprise(self):
        engine = MarketplaceEngine(tier=Tier.ENTERPRISE)
        store = engine.create_white_label_store("My Beats Store", "DJ Nova")
        assert store["store_name"] == "My Beats Store"
        assert store["status"] == "active"

    def test_create_white_label_store_pro_raises(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        with pytest.raises(DreamCoTalentBotTierError):
            engine.create_white_label_store("My Store", "DJ Nova")

    def test_marketplace_summary(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        beat = self._make_beat()
        listing = engine.list_beat_for_sale(beat, price_usd=10.0)
        engine.purchase_listing(listing.listing_id, "a@example.com")
        summary = engine.marketplace_summary()
        assert summary["total_listings"] == 1
        assert summary["total_sales"] == 1
        assert summary["total_revenue_usd"] == 10.0

    def test_list_marketplace_filter_by_type(self):
        engine = MarketplaceEngine(tier=Tier.PRO)
        beat = self._make_beat()
        engine.list_beat_for_sale(beat, price_usd=10.0)
        song = {"title": "My Song", "song_id": "s001"}
        engine.list_song_for_sale(song, price_usd=5.0)
        beats = engine.list_marketplace(asset_type="beat")
        assert all(l["asset_type"] == "beat" for l in beats)
        assert len(beats) == 1


# ===========================================================================
# Bot — Marketplace delegation
# ===========================================================================

class TestBotMarketplace:
    def test_list_beat_for_sale(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        beat = bot.generate_beat("hip-hop", bpm=90)
        listing = bot.list_beat_for_sale(beat, price_usd=24.99)
        assert listing["price_usd"] == 24.99
        assert listing["asset_type"] == "beat"

    def test_list_song_for_sale(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        song = bot.generate_song("Night Moves", "r&b", "Walking alone tonight")
        listing = bot.list_song_for_sale(song, price_usd=9.99)
        assert listing["asset_type"] == "song"

    def test_purchase_listing(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        beat = bot.generate_beat("trap")
        listing = bot.list_beat_for_sale(beat, price_usd=15.00)
        purchase = bot.purchase_listing(listing["listing_id"], "fan@example.com")
        assert "download_url" in purchase

    def test_marketplace_summary(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        beat = bot.generate_beat("pop")
        listing = bot.list_beat_for_sale(beat, price_usd=5.0)
        bot.purchase_listing(listing["listing_id"], "buyer@example.com")
        summary = bot.marketplace_summary()
        assert summary["total_revenue_usd"] == 5.0

    def test_create_white_label_store_enterprise(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        store = bot.create_white_label_store("DreamCo Beats", "DreamCo Inc.")
        assert store["status"] == "active"

    def test_create_white_label_store_pro_raises(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        with pytest.raises(DreamCoTalentBotTierError):
            bot.create_white_label_store("My Store", "DJ Nova")

    def test_list_marketplace(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        beat = bot.generate_beat("jazz")
        bot.list_beat_for_sale(beat, price_usd=8.0)
        listings = bot.list_marketplace()
        assert len(listings) >= 1


# ===========================================================================
# Self-Heal Engine
# ===========================================================================

class TestSelfHealEngine:
    def test_initial_health_is_healthy(self):
        engine = SelfHealEngine()
        health = engine.system_health()
        assert health["overall_status"] == "healthy"

    def test_monitor_ok_component(self):
        engine = SelfHealEngine()
        result = engine.monitor("music_production", "ok")
        assert result["status"] == "ok"

    def test_monitor_degraded_component_auto_recovers(self):
        engine = SelfHealEngine()
        result = engine.monitor("voice_clone", "error")
        assert result["resolved"] is True
        assert engine._component_status.get("voice_clone") == "ok"

    def test_incident_log_records_issues(self):
        engine = SelfHealEngine()
        engine.monitor("marketplace", "down")
        log = engine.incident_log()
        assert len(log) == 1
        assert log[0]["component"] == "marketplace"

    def test_system_health_all_components_present(self):
        engine = SelfHealEngine()
        health = engine.system_health()
        for component in SelfHealEngine.COMPONENTS:
            assert component in health["components"]


# ===========================================================================
# Bot — Self-Heal delegation
# ===========================================================================

class TestBotSelfHeal:
    def test_system_health_all_tiers(self):
        for tier in Tier:
            bot = DreamCoTalentBot(tier=tier)
            health = bot.system_health()
            assert health["overall_status"] in ("healthy", "degraded")

    def test_monitor_component_ok(self):
        bot = DreamCoTalentBot()
        result = bot.monitor_component("music_production", "ok")
        assert result["status"] == "ok"

    def test_monitor_component_degraded_auto_recovers(self):
        bot = DreamCoTalentBot()
        result = bot.monitor_component("rights_engine", "error")
        assert result["resolved"] is True

    def test_incident_log(self):
        bot = DreamCoTalentBot()
        bot.monitor_component("marketplace", "down")
        log = bot.incident_log()
        assert len(log) == 1


# ===========================================================================
# Orchestration: run_full_music_campaign
# ===========================================================================

class TestRunFullMusicCampaign:
    def test_free_tier_campaign(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        report = bot.run_full_music_campaign(
            "Artist X", "hip-hop", "My Track", "Verse 1 lyrics"
        )
        assert report["tier"] == "free"
        assert "beat" in report
        assert "song" in report
        assert "voiceover" in report
        assert "mastered" in report
        assert "beat_generation" in report["steps_completed"]
        # Marketplace listing not available on free
        assert "marketplace_listing" not in report

    def test_pro_tier_campaign(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        report = bot.run_full_music_campaign(
            "DJ Nova", "trap", "Dark Night", "Walking in the dark"
        )
        assert report["tier"] == "pro"
        assert "marketplace_listing" in report
        assert "marketplace_listing" in report["steps_completed"]

    def test_enterprise_tier_campaign(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        report = bot.run_full_music_campaign(
            "MC Big", "r&b", "Summer Love", "Summer love forever",
            platforms=["spotify", "apple_music", "tiktok"]
        )
        assert report["tier"] == "enterprise"
        assert "platform_distribution" in report["steps_completed"]


# ===========================================================================
# describe_tier
# ===========================================================================

class TestDescribeTier:
    def test_describe_free(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        output = bot.describe_tier()
        assert "free" in output.lower()
        assert "$" in output

    def test_describe_pro(self):
        bot = DreamCoTalentBot(tier=Tier.PRO)
        output = bot.describe_tier()
        assert "pro" in output.lower()

    def test_describe_enterprise(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        output = bot.describe_tier()
        assert "enterprise" in output.lower()

    def test_describe_free_suggests_upgrade(self):
        bot = DreamCoTalentBot(tier=Tier.FREE)
        output = bot.describe_tier()
        assert "Upgrade" in output

    def test_describe_enterprise_no_upgrade(self):
        bot = DreamCoTalentBot(tier=Tier.ENTERPRISE)
        output = bot.describe_tier()
        assert "Upgrade" not in output


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_supported_genres_not_empty(self):
        assert len(SUPPORTED_GENRES) > 0

    def test_supported_platforms_not_empty(self):
        assert len(SUPPORTED_PLATFORMS) > 0

    def test_supported_content_types_not_empty(self):
        assert len(SUPPORTED_CONTENT_TYPES) > 0

    def test_supported_right_types_not_empty(self):
        assert len(SUPPORTED_RIGHT_TYPES) > 0

    def test_supported_grant_categories_not_empty(self):
        assert len(SUPPORTED_GRANT_CATEGORIES) > 0

    def test_hip_hop_in_genres(self):
        assert "hip-hop" in SUPPORTED_GENRES

    def test_copyright_in_right_types(self):
        assert "copyright" in SUPPORTED_RIGHT_TYPES

    def test_music_production_in_grant_categories(self):
        assert "music_production" in SUPPORTED_GRANT_CATEGORIES


# ===========================================================================
# Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    @pytest.fixture
    def library(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        return lib

    def test_dreamco_talent_bot_is_registered(self, library):
        entry = library.get_bot("dreamco_talent_bot")
        assert entry.bot_id == "dreamco_talent_bot"

    def test_dreamco_talent_bot_display_name(self, library):
        entry = library.get_bot("dreamco_talent_bot")
        assert "Talent" in entry.display_name

    def test_dreamco_talent_bot_has_music_capability(self, library):
        entry = library.get_bot("dreamco_talent_bot")
        assert "beat_generation" in entry.capabilities

    def test_dreamco_talent_bot_has_rights_capability(self, library):
        entry = library.get_bot("dreamco_talent_bot")
        assert "copyright_registration" in entry.capabilities

    def test_dreamco_talent_bot_has_talent_capability(self, library):
        entry = library.get_bot("dreamco_talent_bot")
        assert "talent_management" in entry.capabilities

    def test_dreamco_talent_bot_entertainment_category(self, library):
        from bots.global_bot_network.bot_library import BotCategory
        entry = library.get_bot("dreamco_talent_bot")
        assert entry.category == BotCategory.ENTERTAINMENT
