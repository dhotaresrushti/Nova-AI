"""
speech_to_text.py
------------------
Handles microphone capture and conversion of spoken audio into text
using the `speech_recognition` library (Google Web Speech API by default).

This module is intentionally isolated from NLP/LLM logic so the
recognition backend (Google / Whisper / Vosk) can be swapped without
touching the rest of the pipeline.
"""

import logging
import speech_recognition as sr

import config

logger = logging.getLogger(__name__)


class SpeechToText:
    """Wraps microphone listening and speech-to-text transcription."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # Calibrate once for ambient noise so recognition is more reliable.
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen(self) -> str | None:
        """
        Listen on the microphone and return the transcribed text.

        Returns:
            str: the recognized text, lowercased and stripped.
            None: if no speech was detected or recognition failed.
        """
        with self.microphone as source:
            logger.info("Listening for a command...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=config.LISTEN_TIMEOUT,
                    phrase_time_limit=config.PHRASE_TIME_LIMIT,
                )
            except sr.WaitTimeoutError:
                logger.warning("Listening timed out; no speech detected.")
                return None

        try:
            text = self.recognizer.recognize_google(
                audio, language=config.SPEECH_LANGUAGE
            )
            logger.info("Transcribed: %s", text)
            return text.strip().lower()
        except sr.UnknownValueError:
            logger.warning("Could not understand audio.")
            return None
        except sr.RequestError as e:
            logger.error("Speech recognition service error: %s", e)
            return None
