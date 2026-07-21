"""
SpeechHandler - Speech-to-task voice recognition for Buddy.

Converts spoken audio into text using the SpeechRecognition library,
then delegates parsing to the TextHandler.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SpeechRecognitionError(RuntimeError):
    """Raised when speech cannot be recognized."""


class SpeechHandler:
    """Capture microphone audio and convert it to text.

    Uses the ``speech_recognition`` package (PyPI: ``SpeechRecognition``)
    with Google Web Speech as the default backend.  Falls back gracefully
    when audio hardware or the package is unavailable.

    Example::

        handler = SpeechHandler()
        text = handler.listen()      # blocks until audio captured
        print(text)
    """

    def __init__(self, language: str = "en-US", timeout: int = 5) -> None:
        """
        Args:
            language: BCP-47 language tag for recognition (default ``"en-US"``).
            timeout: Seconds to wait for speech before giving up (default 5).
        """
        self.language = language
        self.timeout = timeout
        self._recognizer = None
        self._sr = None
        self._init_recognizer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def listen(self) -> str:
        """Record a single utterance from the default microphone and return
        the recognized text.

        Returns:
            Transcribed text string (may be empty on failure).

        Raises:
            SpeechRecognitionError: When the speech package is unavailable
                or audio capture / recognition fails unrecoverably.
        """
        if self._sr is None or self._recognizer is None:
            raise SpeechRecognitionError(
                "SpeechRecognition package is not available. "
                "Install it with: pip install SpeechRecognition pyaudio"
            )

        try:
            with self._sr.Microphone() as source:
                logger.info("Listening for speech (timeout=%ds)…", self.timeout)
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(source, timeout=self.timeout)
            return self._transcribe(audio)
        except self._sr.WaitTimeoutError:
            logger.warning("No speech detected within %d seconds.", self.timeout)
            return ""
        except OSError as exc:
            raise SpeechRecognitionError(
                f"Microphone access failed: {exc}"
            ) from exc

    def transcribe_audio_file(self, path: str) -> str:
        """Transcribe an audio file at *path* and return the text.

        Args:
            path: Filesystem path to a WAV/FLAC/AIFF file.

        Returns:
            Transcribed text string.
        """
        if self._sr is None or self._recognizer is None:
            raise SpeechRecognitionError(
                "SpeechRecognition package is not available."
            )

        with self._sr.AudioFile(path) as source:
            audio = self._recognizer.record(source)
        return self._transcribe(audio)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_recognizer(self) -> None:
        """Try to import SpeechRecognition and create a Recognizer."""
        try:
            import speech_recognition as sr  # type: ignore[import]

            self._sr = sr
            self._recognizer = sr.Recognizer()
            logger.debug("SpeechRecognition initialized.")
        except ImportError:
            logger.warning(
                "SpeechRecognition package not found.  Voice input will be "
                "unavailable until you run: pip install SpeechRecognition pyaudio"
            )

    def _transcribe(self, audio: object) -> str:
        """Use Google Web Speech API to convert *audio* to text.

        Falls back to ``recognize_sphinx`` when the network is unavailable.
        """
        try:
            text: str = self._recognizer.recognize_google(  # type: ignore[union-attr]
                audio, language=self.language
            )
            logger.info("Recognized (Google): %r", text)
            return text
        except self._sr.UnknownValueError:  # type: ignore[union-attr]
            logger.warning("Google could not understand the audio.")
            return ""
        except self._sr.RequestError as exc:  # type: ignore[union-attr]
            logger.warning(
                "Google Speech API request failed: %s. Trying offline…", exc
            )
            return self._transcribe_offline(audio)

    def _transcribe_offline(self, audio: object) -> str:
        """Attempt offline transcription via CMU Sphinx (if installed)."""
        try:
            text: str = self._recognizer.recognize_sphinx(audio)  # type: ignore[union-attr]
            logger.info("Recognized (Sphinx offline): %r", text)
            return text
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Offline transcription failed: %s", exc)
            return ""
