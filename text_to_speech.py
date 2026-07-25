"""
text_to_speech.py
------------------
Provides spoken feedback to the user using pyttsx3 (fully offline TTS,
no API key required — keeps the assistant responsive even without
internet, except for the LLM call itself).
"""

import logging
import pyttsx3

import config

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Wraps pyttsx3 to speak feedback back to the user."""

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", config.TTS_RATE)
        self.engine.setProperty("volume", config.TTS_VOLUME)

    def speak(self, text: str) -> None:
        """Speak the given text aloud and log it."""
        logger.info("Assistant says: %s", text)
        self.engine.say(text)
        self.engine.runAndWait()
