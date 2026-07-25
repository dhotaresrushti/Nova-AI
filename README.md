# Voice-Controlled Computer System

A Python-based assistant that lets you control your computer using natural
spoken commands. Built for a Data Science assignment to demonstrate speech
processing, NLP, LLM-based reasoning (via LangChain), and system-level
automation, with proper file handling and logging throughout.

## Features

| Voice command example                     | Action performed                          |
|---------------------------------------------|--------------------------------------------|
| "Open notepad"                               | Launches the whitelisted application       |
| "Create a folder called Projects"            | Makes a new folder in the workspace        |
| "Create a file called notes.txt"             | Creates a new text file                    |
| "Search for my resume file"                  | Searches the filesystem for matches        |
| "Type hello this is a test"                  | Types the text at the current cursor       |
| "Open website youtube.com"                   | Opens the URL in the default browser       |
| "Delete old.txt"                             | Soft-deletes (moves to a local trash dir)  |
| "Exit" / "Stop listening"                    | Ends the session                           |

## Architecture

```
Mic Audio → SpeechToText → NLPProcessor (LangChain + LLM) → CommandExecutor → OS Action
                                                    ↓
                                              FileManager (JSON history + logs)
                                                    ↓
                                              TextToSpeech (spoken feedback)
```

- **speech_to_text.py** — captures microphone audio and transcribes it
  (Google Web Speech API via `SpeechRecognition`).
- **nlp_processor.py** — the NLP/LLM core. Sends the transcript through a
  LangChain `ChatPromptTemplate` to an LLM (Claude by default, OpenAI
  optional), constrained to return a strict JSON `Intent` schema
  (`intent`, `parameters`, `confidence`). This is what lets the assistant
  understand free-form phrasing ("make a folder named X" vs "create folder
  X") and still map reliably onto a fixed set of executable actions.
- **command_executor.py** — maps each `Intent` to a real OS action. Uses an
  application whitelist and soft-delete (trash folder) as safety measures.
- **file_manager.py** — persists every command (timestamp, transcript,
  intent, parameters, success, result message) to
  `data/command_history.json`, and configures rotating log files under
  `data/logs/`.
- **text_to_speech.py** — speaks results back using offline TTS (`pyttsx3`).
- **main.py** — orchestrates the full listen → parse → execute → log →
  speak loop.

## Setup

1. **Clone/copy the project**, then create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > Note: `PyAudio` sometimes needs system-level build tools.
   > - Windows: `pip install pipwin && pipwin install pyaudio`
   > - macOS: `brew install portaudio` before `pip install pyaudio`
   > - Linux: `sudo apt-get install portaudio19-dev python3-pyaudio`

3. **Set your LLM API key** (Anthropic Claude by default):
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-...."
   ```
   To use OpenAI instead, set `LLM_PROVIDER=openai` and `OPENAI_API_KEY`.

4. **Run it:**
   ```bash
   python main.py
   ```
   Speak a command after you hear "Voice assistant ready."

## Extending the project

- **Add a new command type:** add it to the `intent` enum and examples in
  `nlp_processor.SYSTEM_PROMPT`, then add a handler method in
  `CommandExecutor` and register it in `CommandExecutor.execute()`'s
  `handlers` dict.
- **Add a new whitelisted app:** add an entry to `config.APP_WHITELIST`.
- **Swap the speech backend:** replace the body of
  `SpeechToText.listen()` (e.g., use OpenAI Whisper for offline/more
  accurate transcription).
- **Wire real system control:** `command_executor._system_control` is a
  clearly marked stub — connect it to `pycaw` (Windows volume),
  `osascript` (macOS), or `amixer`/`systemctl` (Linux).

## Design decisions worth mentioning in your report

1. **Structured LLM output over free-form execution.** The LLM never runs
   commands directly — it only classifies intent into a fixed JSON schema.
   This keeps the system's behavior auditable and prevents prompt-injection
   style risks from spoken input turning into arbitrary code execution.
2. **Whitelisted application launching** avoids passing raw, unsanitized
   strings to the shell.
3. **Soft-delete (trash folder)** protects against speech-recognition
   errors causing accidental data loss.
4. **Full JSON audit trail** (`data/command_history.json`) satisfies the
   "File Handling" requirement with real, structured, analyzable data —
   you could load this into pandas for a usage-analytics section of your
   report.
5. **Modular, single-responsibility files** make the codebase easy to
   test, extend, and explain in a viva/demo.

## Known limitations (good to state explicitly in your report)

- Requires an internet connection for both speech recognition (Google API)
  and the LLM call.
- `system_control` actions are stubbed pending OS-specific wiring.
- Voice recognition accuracy depends on microphone quality and ambient
  noise.
