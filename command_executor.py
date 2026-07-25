"""
command_executor.py
--------------------
Takes a structured `Intent` (produced by nlp_processor) and performs the
corresponding action on the host operating system.

Design notes:
  * Application launching is restricted to a whitelist (config.APP_WHITELIST)
    rather than blindly executing whatever string the model/user produced —
    this avoids shell-injection-style risks from spoken/LLM-generated text.
  * File deletion moves files to a local "trash" folder instead of a hard
    delete, so a misheard command can't destroy user data irrecoverably.
  * Every action returns a (success: bool, message: str) tuple so the
    caller (main.py) can log it and speak feedback consistently.
"""
import webbrowser
import datetime
import time
import pyautogui
import psutil
import logging
import os
import platform
import shutil
import subprocess


from pathlib import Path

import config
from modules.nlp_processor import Intent

logger = logging.getLogger(__name__)

try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except Exception:  # pyautogui needs a display; unavailable on headless servers
    _PYAUTOGUI_AVAILABLE = False


class CommandExecutor:
    """Executes an Intent object and returns a result message."""

    def __init__(self):
        self.os_name = platform.system().lower()  # 'windows' / 'darwin' / 'linux'
        self.trash_dir = config.DEFAULT_WORKSPACE / ".trash"
        self.trash_dir.mkdir(exist_ok=True)

    def _get_location(self, location: str):
        """
        Returns the correct folder path based on the spoken location.
        """

        if not location:
            return config.DEFAULT_WORKSPACE

        return config.LOCATION_MAP.get(
            location.lower(),
            config.DEFAULT_WORKSPACE
        )



    # ------------------------------------------------------------------
    # Public dispatch
    # ------------------------------------------------------------------
    def execute(self, intent: Intent) -> tuple[bool, str]:
        handlers = {
            "open_application": self._open_application,
            "create_file": self._create_file,
            "create_folder": self._create_folder,
            "search_file": self._search_file,
            "open_folder": self._open_folder,
            "open_file": self._open_file,
            "type_text": self._type_text,
            "open_website": self._open_website,
            "delete_file": self._delete_file,
            "system_control": self._system_control,
            "unknown": self._unknown,
            "take_screenshot": self._take_screenshot,
            "get_datetime": self._get_datetime,
            "battery_status": self._battery_status,
            "open_camera": self._open_camera,
            "read_file": self._read_file,
            "search_google": self._search_google,
        }
        handler = handlers.get(intent.intent, self._unknown)
        try:
            return handler(intent.parameters)
        except Exception as e:
            logger.exception("Execution failed for intent %s", intent.intent)
            return False, f"Sorry, I ran into an error: {e}"

    # ------------------------------------------------------------------
    # Individual handlers
    # ------------------------------------------------------------------
    def _open_application(self, params: dict) -> tuple[bool, str]:

        app_name = params.get(
            "app_name",
            ""
        ).strip().lower()

        app_entry = config.APP_WHITELIST.get(app_name)

        if not app_entry:
            return (
                False,
                f"I don't know how to open '{app_name}'."
            )

        command = app_entry.get(self.os_name)

        if not command:
            return (
                False,
                f"{app_name} is not supported on {self.os_name}."
            )

        subprocess.Popen(
            command,
            shell=True
        )

        return (
            True,
            f"Opening {app_name}."
        )

    def _create_file(self, params: dict) -> tuple[bool, str]:

        file_name = params.get(
            "file_name",
            "new_file.txt"
        )

        # Add .txt if no extension is provided
        if "." not in file_name:
            file_name += ".txt"

        content = params.get(
            "content",
            ""
        )

        location = params.get(
            "location",
            "workspace"
        )

        base_path = self._get_location(location)

        file_path = base_path / file_name

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return (
            True,
            f"File '{file_name}' created in {base_path}."
        )

    def _create_folder(self, params: dict) -> tuple[bool, str]:

        folder_name = params.get("folder_name", "New Folder")

        location = params.get(
            "location",
            "workspace"
        )

        base_path = self._get_location(location)

        folder_path = base_path / folder_name

        folder_path.mkdir(
            parents=True,
            exist_ok=True
        )

        return (
            True,
            f"Folder '{folder_name}' created in {base_path}."
        )

    def _open_folder(self, params: dict) -> tuple[bool, str]:

        folder_name = params.get(
            "folder_name",
            ""
        ).strip().lower()

        if not folder_name:
            return (
                False,
                "Please tell me the folder name."
            )

        # Open standard folders directly
        if folder_name in config.LOCATION_MAP:
            folder = config.LOCATION_MAP[folder_name]

            os.startfile(folder)

            return (
                True,
                f"Opening {folder_name}."
            )

        # Search all configured locations
        search_locations = [
            config.DESKTOP,
            config.DOCUMENTS,
            config.DOWNLOADS,
            config.DEFAULT_WORKSPACE
        ]

        for location in search_locations:

            if location.exists():

                for item in location.iterdir():

                    if item.is_dir():

                        if item.name.lower() == folder_name:
                            os.startfile(item)

                            return (
                                True,
                                f"Opening {item.name}."
                            )

        return (
            False,
            f"Folder '{folder_name}' was not found."
        )

    def _open_file(self, params: dict) -> tuple[bool, str]:

        file_name = params.get(
            "file_name",
            ""
        ).strip().lower()

        if not file_name:
            return (
                False,
                "Please tell me the file name."
            )

        # Search configured locations
        for root in config.SEARCH_ROOTS:

            for directory, _, files in os.walk(root):

                for file in files:

                    if file.lower() == file_name:
                        file_path = Path(directory) / file

                        os.startfile(file_path)

                        return (
                            True,
                            f"Opening {file}."
                        )

        return (
            False,
            f"I could not find {file_name}."
        )

    def _search_file(self, params: dict) -> tuple[bool, str]:
        query = params.get("file_name", "").lower()
        if not query:
            return False, "I didn't catch a file name to search for."

        matches = []
        for root_dir in config.SEARCH_ROOTS:
            for dirpath, _, filenames in os.walk(root_dir):
                for fname in filenames:
                    if query in fname.lower():
                        matches.append(str(Path(dirpath) / fname))
                if len(matches) >= 10:
                    break
            if len(matches) >= 10:
                break

        if not matches:
            return False, f"No files found matching '{query}'."
        preview = "; ".join(matches[:5])
        return True, f"Found {len(matches)} match(es). Top results: {preview}"

    def _type_text(self, params: dict) -> tuple[bool, str]:
        text = params.get("text", "")
        if not text:
            return False, "There was no text to type."
        if not _PYAUTOGUI_AVAILABLE:
            return False, "Typing isn't available in this environment (no display)."
        pyautogui.typewrite(text, interval=0.02)
        return True, "Text typed."

    def _open_website(self, params: dict) -> tuple[bool, str]:

        url = params.get(
            "url",
            ""
        ).strip().lower()

        if not url:
            return (
                False,
                "No website was provided."
            )

        # Check predefined websites
        if url in config.WEBSITES:
            website = config.WEBSITES[url]

            webbrowser.open(website)

            return (
                True,
                f"Opening {url}."
            )

        # If user gave direct URL
        if not url.startswith(
                ("http://", "https://")
        ):
            url = "https://" + url

        webbrowser.open(url)

        return (
            True,
            f"Opening {url}."
        )

    def _delete_file(self, params: dict) -> tuple[bool, str]:
        """Soft-delete: moves the file to a local trash folder instead of
        permanently removing it, to protect against misrecognized speech."""
        file_name = params.get("file_name", "")
        target = config.DEFAULT_WORKSPACE / file_name
        if not target.exists():
            return False, f"'{file_name}' was not found in the workspace."
        shutil.move(str(target), str(self.trash_dir / target.name))
        return True, f"Moved '{file_name}' to trash. It can still be recovered."

    def _system_control(self, params: dict) -> tuple[bool, str]:

        action = params.get(
            "action",
            ""
        ).strip().lower()

        # ---------------- Shutdown ----------------
        if action == "shutdown":

            subprocess.Popen(
                "shutdown /s /t 30",
                shell=True
            )

            return (
                True,
                "Shutdown scheduled in 30 seconds."
            )

        # ---------------- Restart ----------------
        elif action == "restart":

            subprocess.Popen(
                "shutdown /r /t 30",
                shell=True
            )

            return (
                True,
                "Restart scheduled in 30 seconds."
            )

        # ---------------- Sleep ----------------
        elif action == "sleep":

            subprocess.Popen(
                "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                shell=True
            )

            return (
                True,
                "Putting the computer to sleep."
            )

        # ---------------- Lock ----------------
        elif action == "lock":

            subprocess.Popen(
                "rundll32.exe user32.dll,LockWorkStation",
                shell=True
            )

            return (
                True,
                "Locking your computer."
            )

        # ---------------- Volume ----------------
        elif action == "volume_up":

            return (
                True,
                "Volume up feature will be added."
            )

        elif action == "volume_down":

            return (
                True,
                "Volume down feature will be added."
            )

        elif action == "mute":

            return (
                True,
                "Mute feature will be added."
            )

        return (
            False,
            f"Unknown system action: {action}"
        )

    def _take_screenshot(self, params):

        folder = config.DEFAULT_WORKSPACE / "Screenshots"

        folder.mkdir(exist_ok=True)

        filename = (
                folder /
                f"screenshot_{int(time.time())}.png"
        )

        image = pyautogui.screenshot()

        image.save(filename)

        return (
            True,
            f"Screenshot saved at {filename}"
        )

    def _get_datetime(self, params):

        now = datetime.datetime.now()

        req = params.get(
            "type",
            "datetime"
        )

        if req == "date":

            return (
                True,
                f"Today's date is {now.strftime('%d %B %Y')}"
            )


        elif req == "time":

            return (
                True,
                f"Current time is {now.strftime('%I:%M %p')}"
            )

        return (
            True,
            f"Date and time is {now.strftime('%d %B %Y %I:%M %p')}"
        )

    def _battery_status(self, params):

        battery = psutil.sensors_battery()

        if battery:
            return (
                True,
                f"Battery percentage is {battery.percent}%"
            )

        return (
            False,
            "Battery information unavailable."
        )

    def _open_camera(self, params):

        subprocess.Popen(
            "start microsoft.windows.camera:",
            shell=True
        )

        return (
            True,
            "Opening camera."
        )

    def _read_file(self, params):

        file_name = params.get(
            "file_name",
            ""
        )

        path = config.DEFAULT_WORKSPACE / file_name

        if not path.exists():
            return (
                False,
                "File not found."
            )

        content = path.read_text(
            encoding="utf-8"
        )

        return (
            True,
            content[:500]
        )

    def _search_google(self, params):

        query = params.get(
            "query",
            ""
        )

        if not query:
            return (
                False,
                "No search query provided."
            )

        url = (
                "https://www.google.com/search?q="
                + query.replace(" ", "+")
        )

        webbrowser.open(url)

        return (
            True,
            f"Searching Google for {query}"
        )

    def _unknown(self, params: dict) -> tuple[bool, str]:
        return False, "Sorry, I didn't understand that command."
