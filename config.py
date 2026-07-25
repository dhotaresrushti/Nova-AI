
"""
config.py
---------
Central configuration for Voice Controlled Computer System.
"""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# Base Directories
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
HISTORY_FILE = DATA_DIR / "command_history.json"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Create empty history file if it doesn't exist
if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text("[]", encoding="utf-8")


# ==========================================================
# LLM Configuration
# ==========================================================

LLM_PROVIDER = "ollama"
LLM_MODEL = "llama3.2"


# ==========================================================
# Speech Recognition
# ==========================================================

SPEECH_LANGUAGE = "en-IN"
LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 8


# ==========================================================
# Text To Speech
# ==========================================================

TTS_RATE = 175
TTS_VOLUME = 1.0


# ==========================================================
# Important Windows Locations
# ==========================================================

HOME = Path.home()

DESKTOP = HOME / "Desktop"
DOCUMENTS = HOME / "Documents"
DOWNLOADS = HOME / "Downloads"
PICTURES = HOME / "Pictures"

DEFAULT_WORKSPACE = HOME / "VoiceAssistantWorkspace"
DEFAULT_WORKSPACE.mkdir(exist_ok=True)

LOCATION_MAP = {
    "desktop": DESKTOP,
    "documents": DOCUMENTS,
    "document": DOCUMENTS,
    "downloads": DOWNLOADS,
    "download": DOWNLOADS,
    "pictures": PICTURES,
    "picture": PICTURES,
    "workspace": DEFAULT_WORKSPACE,
}


# ==========================================================
# File Search Locations
# ==========================================================

SEARCH_ROOTS = [
    str(DESKTOP),
    str(DOCUMENTS),
    str(DOWNLOADS),
    str(DEFAULT_WORKSPACE),
]


# ==========================================================
# Supported Applications
# ==========================================================

APP_WHITELIST = {

    "notepad": {
        "windows": "notepad.exe"
    },

    "calculator": {
        "windows": "calc.exe"
    },

    "paint": {
        "windows": "mspaint.exe"
    },

    "cmd": {
        "windows": "cmd.exe"
    },

    "command prompt": {
        "windows": "cmd.exe"
    },

    "powershell": {
        "windows": "powershell.exe"
    },

    "file explorer": {
        "windows": "explorer.exe"
    },

    "explorer": {
        "windows": "explorer.exe"
    },

    "settings": {
        "windows": "start ms-settings:"
    },

    "control panel": {
        "windows": "control"
    },

    "task manager": {
        "windows": "taskmgr.exe"
    },

    "chrome": {
        "windows": "start chrome"
    },

    "google chrome": {
        "windows": "start chrome"
    },

    "browser": {
        "windows": "start chrome"
    },

    "edge": {
        "windows": "start msedge"
    },

    "vscode": {
        "windows": "code"
    },

    "visual studio code": {
        "windows": "code"
    },

    "pycharm": {
        "windows": "pycharm64.exe"
    },

    "word": {
        "windows": "start winword"
    },

    "excel": {
        "windows": "start excel"
    },

    "powerpoint": {
        "windows": "start powerpnt"
    },

    "power bi": {
        "windows": "start PBIDesktop"
    }
}


# ==========================================================
# Frequently Used Websites
# ==========================================================

WEBSITES = {

    "youtube": "https://www.youtube.com",

    "gmail": "https://mail.google.com",

    "google": "https://www.google.com",

    "chatgpt": "https://chat.openai.com",

    "github": "https://github.com",

    "linkedin": "https://www.linkedin.com",

    "instagram": "https://www.instagram.com",

    "facebook": "https://www.facebook.com",

    "whatsapp": "https://web.whatsapp.com",

    "stackoverflow": "https://stackoverflow.com",

    "geeksforgeeks": "https://www.geeksforgeeks.org"
}

