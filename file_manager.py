"""
file_manager.py
----------------
Handles all persistent file I/O for the assistant:
  * Appends every executed command to a structured JSON history file
    (this is the "File Handling" requirement of the assignment — a real,
    growing dataset of assistant usage that could later be analyzed).
  * Configures rotating log files under data/logs/.

Keeping this separate from command_executor.py means the *logic* of
running a command is decoupled from the *bookkeeping* of recording it.
"""

import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config


def setup_logging() -> None:
    """Configure root logger with console + rotating file handlers."""
    log_file = config.LOG_DIR / "assistant.log"
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.addHandler(console)


class FileManager:
    """Reads and writes the JSON command-history file."""

    def __init__(self, history_path: Path = config.HISTORY_FILE):
        self.history_path = history_path
        if not self.history_path.exists():
            self._write_all([])

    def _read_all(self) -> list[dict[str, Any]]:
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_all(self, records: list[dict[str, Any]]) -> None:
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    def log_command(
        self,
        raw_text: str,
        intent: str,
        parameters: dict[str, Any],
        success: bool,
        message: str,
    ) -> None:
        """Append one command record to the JSON history file."""
        records = self._read_all()
        records.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_text": raw_text,
            "intent": intent,
            "parameters": parameters,
            "success": success,
            "message": message,
        })
        self._write_all(records)

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return the most recent `limit` command records."""
        return self._read_all()[-limit:]
