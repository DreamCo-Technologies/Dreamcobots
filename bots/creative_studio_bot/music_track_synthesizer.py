# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Music Track Synthesizer — Creative Studio Bot

Generates dynamic instrumental audio tracks for commercials, music videos,
and cinematic content.

Features
--------
  • Genre-aware composition (pop, hip-hop, jazz, classical, electronic, etc.)
  • Tempo, key, and mood controls
  • Multi-layer instrument arrangement (drums, bass, melody, pads)
  • Beat-sync metadata for visual alignment
  • Export references compatible with the CineCore video pipeline

Usage
-----
    from bots.creative_studio_bot.music_track_synthesizer import MusicTrackSynthesizer

    synth = MusicTrackSynthesizer()
    track = synth.generate(genre="hip-hop", tempo=90, mood="energetic")
    print(track)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_GENRES = [
    "pop", "hip-hop", "jazz", "classical", "electronic",
    "r&b", "reggae", "country", "rock", "cinematic", "ambient",
]

SUPPORTED_MOODS = [
    "energetic", "calm", "uplifting", "dramatic", "mysterious",
    "romantic", "tense", "playful", "nostalgic", "triumphant",
]

SUPPORTED_KEYS = [
    "C major", "G major", "D major", "A major",
    "E minor", "A minor", "D minor", "B minor",
]

# Instrument layers per genre (simulated arrangement)
_GENRE_INSTRUMENTS: Dict[str, List[str]] = {
    "pop":        ["drums", "bass", "synth_pad", "lead_melody", "strings"],
    "hip-hop":    ["drums", "bass", "808_bass", "sample_loop", "hi_hat"],
    "jazz":       ["upright_bass", "piano", "drums", "trumpet", "saxophone"],
    "classical":  ["strings", "piano", "oboe", "french_horn", "timpani"],
    "electronic": ["drums", "synth_bass", "arp", "lead_synth", "fx_pads"],
    "r&b":        ["drums", "bass", "keys", "guitar", "vocals_chop"],
    "reggae":     ["drums", "bass", "rhythm_guitar", "organ", "horns"],
    "country":    ["acoustic_guitar", "drums", "fiddle", "pedal_steel", "bass"],
    "rock":       ["drums", "electric_bass", "rhythm_guitar", "lead_guitar", "keys"],
    "cinematic":  ["strings", "brass", "choir", "piano", "percussion"],
    "ambient":    ["pads", "guitar", "piano", "ambient_fx", "sub_bass"],
}

_DEFAULT_INSTRUMENTS = ["drums", "bass", "melody"]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class MusicTrack:
    """
    A generated instrumental music track.

    ``track_ref`` is an opaque reference to the synthesised audio asset
    (e.g. an S3 key or encrypted blob ID) — analogous to ``audio_ref`` in
    the voice pipeline.
    """

    track_id: str
    genre: str
    mood: str
    tempo_bpm: int
    key: str
    duration_seconds: float
    instruments: List[str]
    beat_markers: List[float]   # Timestamps (s) of each beat for visual sync
    track_ref: str              # Opaque asset reference
    status: str = "completed"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "genre": self.genre,
            "mood": self.mood,
            "tempo_bpm": self.tempo_bpm,
            "key": self.key,
            "duration_seconds": self.duration_seconds,
            "instruments": self.instruments,
            "beat_markers": self.beat_markers,
            "track_ref": self.track_ref,
            "status": self.status,
            "tags": self.tags,
        }


# ---------------------------------------------------------------------------
# MusicTrackSynthesizer
# ---------------------------------------------------------------------------


class MusicTrackSynthesizer:
    """
    Generates dynamic instrumental audio tracks for the Creative Hub.

    Parameters
    ----------
    default_duration : float
        Default track length in seconds (overridable per call).
    """

    def __init__(self, default_duration: float = 30.0) -> None:
        self._default_duration = default_duration
        self._library: List[MusicTrack] = []

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def generate(
        self,
        genre: str = "pop",
        tempo: int = 120,
        mood: str = "uplifting",
        key: Optional[str] = None,
        duration: Optional[float] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a new instrumental music track.

        Parameters
        ----------
        genre : str
            Musical genre (see ``SUPPORTED_GENRES``).
        tempo : int
            Beats per minute (40–200).
        mood : str
            Emotional mood (see ``SUPPORTED_MOODS``).
        key : str | None
            Musical key (see ``SUPPORTED_KEYS``).  Chosen automatically if omitted.
        duration : float | None
            Track length in seconds.  Uses ``default_duration`` if omitted.
        tags : list of str | None
            Optional tags for cataloguing.

        Returns
        -------
        dict
            Serialised :class:`MusicTrack` instance.

        Raises
        ------
        ValueError
            If *genre*, *mood*, or *tempo* is invalid.
        """
        self._validate(genre, mood, tempo)

        chosen_key = key if key in SUPPORTED_KEYS else SUPPORTED_KEYS[0]
        track_duration = duration if (duration and duration > 0) else self._default_duration
        instruments = _GENRE_INSTRUMENTS.get(genre, _DEFAULT_INSTRUMENTS)

        # Generate beat markers at the given tempo
        beat_interval = 60.0 / max(tempo, 1)
        beat_markers = [
            round(i * beat_interval, 3)
            for i in range(int(track_duration / beat_interval))
        ]

        track = MusicTrack(
            track_id=str(uuid.uuid4())[:8],
            genre=genre,
            mood=mood,
            tempo_bpm=tempo,
            key=chosen_key,
            duration_seconds=track_duration,
            instruments=instruments,
            beat_markers=beat_markers,
            track_ref=f"music:{genre}:{str(uuid.uuid4())[:8]}",
            tags=tags or [],
        )
        self._library.append(track)
        return track.to_dict()

    def list_tracks(
        self,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return all generated tracks, optionally filtered by genre or mood.
        """
        tracks = self._library
        if genre:
            tracks = [t for t in tracks if t.genre == genre]
        if mood:
            tracks = [t for t in tracks if t.mood == mood]
        return [t.to_dict() for t in tracks]

    def get_track(self, track_id: str) -> Dict[str, Any]:
        """Retrieve a specific track by ID."""
        for track in self._library:
            if track.track_id == track_id:
                return track.to_dict()
        raise KeyError(f"Track '{track_id}' not found.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate(self, genre: str, mood: str, tempo: int) -> None:
        if genre not in SUPPORTED_GENRES:
            raise ValueError(
                f"Genre '{genre}' not supported. "
                f"Choose from: {SUPPORTED_GENRES}"
            )
        if mood not in SUPPORTED_MOODS:
            raise ValueError(
                f"Mood '{mood}' not supported. "
                f"Choose from: {SUPPORTED_MOODS}"
            )
        if not (40 <= tempo <= 200):
            raise ValueError(f"Tempo must be between 40 and 200 BPM. Got: {tempo}")
