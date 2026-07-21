"""
Media Recognition Tool for Dreamcobots platform (Dreamcobots' Shazam).

Recognises, processes, and facilitates downloading of music and media
to preferred applications.
"""

import hashlib
import mimetypes
import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MediaTrack:
    """Represents a recognised media track."""
    title: str
    artist: str
    album: str
    genre: str
    duration_seconds: float
    fingerprint: str
    track_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    download_url: Optional[str] = None


@dataclass
class RecognitionResult:
    """Result returned from a media recognition attempt."""
    success: bool
    confidence: float          # 0.0 – 1.0
    track: Optional[MediaTrack] = None
    message: str = ""


class MediaRecognition:
    """
    Dreamcobots' Shazam – media recognition, processing, and download tool.

    Uses acoustic fingerprinting to identify audio/video, then surfaces
    metadata and download options for preferred applications.

    A real deployment would integrate with an acoustic-fingerprinting service
    (e.g. AcoustID / Chromaprint).  This implementation provides the full
    interface and a catalogue-backed recognition flow that works without
    external network calls so the platform can be tested offline.
    """

    # Confidence threshold above which recognition is considered successful
    CONFIDENCE_THRESHOLD = 0.75

    def __init__(self) -> None:
        self._catalogue: Dict[str, MediaTrack] = {}

    # ------------------------------------------------------------------
    # Catalogue management
    # ------------------------------------------------------------------

    def register_track(self, track: MediaTrack) -> None:
        """Add a track to the local recognition catalogue."""
        self._catalogue[track.fingerprint] = track

    def get_catalogue(self) -> List[MediaTrack]:
        """Return all tracks in the catalogue."""
        return list(self._catalogue.values())

    # ------------------------------------------------------------------
    # Fingerprinting
    # ------------------------------------------------------------------

    @staticmethod
    def compute_fingerprint(audio_bytes: bytes) -> str:
        """
        Compute an acoustic fingerprint from raw audio bytes.

        In production this would call Chromaprint / AcoustID.  Here we use a
        SHA-1 hash of the first 4 KB as a stable stand-in.

        Args:
            audio_bytes: Raw audio data.

        Returns:
            Hex fingerprint string.
        """
        sample = audio_bytes[:4096]
        return hashlib.sha1(sample).hexdigest()

    # ------------------------------------------------------------------
    # Recognition
    # ------------------------------------------------------------------

    def recognize(self, audio_bytes: bytes) -> RecognitionResult:
        """
        Attempt to recognise a media clip from its audio bytes.

        Matches the computed fingerprint against the registered catalogue.

        Args:
            audio_bytes: Raw audio data (PCM / MP3 / etc.).

        Returns:
            RecognitionResult with track metadata when a match is found.
        """
        if not audio_bytes:
            return RecognitionResult(success=False, confidence=0.0, message="Empty audio input")

        fingerprint = self.compute_fingerprint(audio_bytes)
        track = self._catalogue.get(fingerprint)
        if track:
            return RecognitionResult(success=True, confidence=1.0, track=track, message="Exact match found")

        # Simulate partial matching via prefix similarity
        for fp, candidate in self._catalogue.items():
            shared = sum(a == b for a, b in zip(fingerprint, fp))
            confidence = shared / len(fingerprint)
            if confidence >= self.CONFIDENCE_THRESHOLD:
                return RecognitionResult(
                    success=True,
                    confidence=round(confidence, 3),
                    track=candidate,
                    message=f"Partial match (confidence={confidence:.1%})",
                )

        return RecognitionResult(
            success=False,
            confidence=0.0,
            message="No matching track found in catalogue",
        )

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def get_download_options(self, track: MediaTrack) -> List[Dict[str, str]]:
        """
        Return available download options for a recognised track.

        Each option includes a target app and the download URL.

        Args:
            track: A recognised MediaTrack.

        Returns:
            List of dicts with keys ``app`` and ``url``.
        """
        if not track.download_url:
            return []
        return [
            {"app": "Spotify", "url": f"spotify://track/{track.track_id}"},
            {"app": "Apple Music", "url": f"music://track/{track.track_id}"},
            {"app": "YouTube Music", "url": f"https://music.youtube.com/watch?v={track.track_id}"},
            {"app": "Direct Download", "url": track.download_url},
        ]

    # ------------------------------------------------------------------
    # File-based helpers
    # ------------------------------------------------------------------

    @staticmethod
    def detect_media_type(file_path: str) -> str:
        """
        Return the MIME type of a media file based on its extension.

        Args:
            file_path: Path to the file.

        Returns:
            MIME type string (e.g. 'audio/mpeg') or 'application/octet-stream'.
        """
        mime, _ = mimetypes.guess_type(file_path)
        return mime or "application/octet-stream"

    def recognize_file(self, file_path: str) -> RecognitionResult:
        """
        Recognise a media track from a file on disk.

        Args:
            file_path: Path to the audio/video file.

        Returns:
            RecognitionResult.
        """
        with open(file_path, "rb") as fh:
            data = fh.read()
        return self.recognize(data)
