"""
main.py
-------
Entry point for the Voice-Controlled Computer System.

Pipeline per loop iteration:
    1. Listen to the microphone and transcribe speech -> text   (speech_to_text)
    2. Send text to the LLM via LangChain -> structured Intent   (nlp_processor)
    3. Execute the Intent as a real OS action                    (command_executor)
    4. Log the command + result to JSON history                  (file_manager)
    5. Speak the result back to the user                         (text_to_speech)

Run with:
    python main.py
Say "stop listening" / "exit" / "quit" to end the session.
"""

import logging

from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.nlp_processor import NLPProcessor
from modules.command_executor import CommandExecutor
from modules.file_manager import FileManager, setup_logging

EXIT_PHRASES = {"exit", "quit", "stop listening", "goodbye", "shut down assistant"}


def run_once(stt, tts, nlp, executor, file_manager, logger) -> bool:
    """
    Run a single listen -> parse -> execute -> log -> speak cycle.
    Returns False if the user asked to exit, True otherwise.
    """
    text = stt.listen()
    if not text:
        return True  # nothing heard; just loop again

    logger.info("Heard: %s", text)
    if text in EXIT_PHRASES:
        tts.speak("Goodbye!")
        return False

    intent = nlp.parse(text)
    logger.info("Parsed intent: %s | params=%s | confidence=%.2f",
                intent.intent, intent.parameters, intent.confidence)

    success, message = executor.execute(intent)
    file_manager.log_command(
        raw_text=text,
        intent=intent.intent,
        parameters=intent.parameters,
        success=success,
        message=message,
    )
    tts.speak(message)
    return True


def main():
    setup_logging()
    logger = logging.getLogger("main")
    logger.info("Starting Voice-Controlled Computer System...")

    stt = SpeechToText()
    tts = TextToSpeech()
    nlp = NLPProcessor()
    executor = CommandExecutor()
    file_manager = FileManager()

    tts.speak("Voice assistant ready. How can I help you?")

    running = True
    while running:
        try:
            running = run_once(stt, tts, nlp, executor, file_manager, logger)
        except KeyboardInterrupt:
            logger.info("Interrupted by user (Ctrl+C). Shutting down.")
            break
        except Exception:
            logger.exception("Unexpected error in main loop; continuing.")

    logger.info("Session ended.")


if __name__ == "__main__":
    main()
