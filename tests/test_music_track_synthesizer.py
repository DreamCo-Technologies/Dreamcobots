"""
Tests for MusicTrackSynthesizer.
"""

import sys
import os
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "bots", "ai-models-integration"))

from bots.creative_studio_bot.music_track_synthesizer import (
    MusicTrackSynthesizer,
    SUPPORTED_GENRES,
    SUPPORTED_MOODS,
    MusicTrack,
)


class TestMusicTrackSynthesizer:
    def test_generate_default(self):
        synth = MusicTrackSynthesizer()
        track = synth.generate()
        assert track["genre"] == "pop"
        assert track["status"] == "completed"

    def test_generate_returns_dict(self):
        synth = MusicTrackSynthesizer()
        track = synth.generate(genre="jazz", tempo=90, mood="calm")
        assert isinstance(track, dict)
        assert "track_id" in track
        assert "beat_markers" in track
        assert "track_ref" in track

    def test_beat_markers_count(self):
        synth = MusicTrackSynthesizer()
        track = synth.generate(genre="hip-hop", tempo=120, duration=10.0)
        # At 120 BPM, 1 beat every 0.5 s → 20 beats in 10 s
        assert len(track["beat_markers"]) == 20

    def test_all_supported_genres(self):
        synth = MusicTrackSynthesizer()
        for genre in SUPPORTED_GENRES:
            track = synth.generate(genre=genre, tempo=100, mood="uplifting")
            assert track["genre"] == genre

    def test_all_supported_moods(self):
        synth = MusicTrackSynthesizer()
        for mood in SUPPORTED_MOODS:
            track = synth.generate(mood=mood)
            assert track["mood"] == mood

    def test_invalid_genre_raises(self):
        synth = MusicTrackSynthesizer()
        with pytest.raises(ValueError, match="not supported"):
            synth.generate(genre="grunge_folk_fusion")

    def test_invalid_mood_raises(self):
        synth = MusicTrackSynthesizer()
        with pytest.raises(ValueError, match="not supported"):
            synth.generate(mood="bored")

    def test_tempo_too_low_raises(self):
        synth = MusicTrackSynthesizer()
        with pytest.raises(ValueError):
            synth.generate(tempo=30)

    def test_tempo_too_high_raises(self):
        synth = MusicTrackSynthesizer()
        with pytest.raises(ValueError):
            synth.generate(tempo=250)

    def test_list_tracks(self):
        synth = MusicTrackSynthesizer()
        synth.generate(genre="pop")
        synth.generate(genre="jazz")
        all_tracks = synth.list_tracks()
        assert len(all_tracks) == 2

    def test_list_tracks_filter_genre(self):
        synth = MusicTrackSynthesizer()
        synth.generate(genre="pop")
        synth.generate(genre="jazz")
        pop_tracks = synth.list_tracks(genre="pop")
        assert len(pop_tracks) == 1
        assert pop_tracks[0]["genre"] == "pop"

    def test_list_tracks_filter_mood(self):
        synth = MusicTrackSynthesizer()
        synth.generate(mood="calm")
        synth.generate(mood="energetic")
        calm = synth.list_tracks(mood="calm")
        assert len(calm) == 1

    def test_get_track(self):
        synth = MusicTrackSynthesizer()
        track = synth.generate(genre="rock", tempo=140)
        fetched = synth.get_track(track["track_id"])
        assert fetched["track_id"] == track["track_id"]

    def test_get_track_missing_raises(self):
        synth = MusicTrackSynthesizer()
        with pytest.raises(KeyError):
            synth.get_track("nonexistent_id")

    def test_track_ref_format(self):
        synth = MusicTrackSynthesizer()
        track = synth.generate(genre="electronic")
        assert track["track_ref"].startswith("music:electronic:")

    def test_instruments_not_empty(self):
        synth = MusicTrackSynthesizer()
        for genre in SUPPORTED_GENRES:
            track = synth.generate(genre=genre)
            assert len(track["instruments"]) > 0

    def test_default_duration(self):
        synth = MusicTrackSynthesizer(default_duration=15.0)
        track = synth.generate()
        assert track["duration_seconds"] == 15.0

    def test_custom_duration(self):
        synth = MusicTrackSynthesizer()
        track = synth.generate(duration=60.0)
        assert track["duration_seconds"] == 60.0

    def test_tags_stored(self):
        synth = MusicTrackSynthesizer()
        track = synth.generate(tags=["ad", "upbeat"])
        assert "ad" in track["tags"]
