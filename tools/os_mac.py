import logging
import re
import subprocess

from core.config import ALLOW_POWER_ACTIONS, POWER_CONFIRMATION_REQUIRED

logger = logging.getLogger(__name__)

APP_ALIASES = {
    "chrome": ["Google Chrome"],
    "firefox": ["Firefox"],
    "edge": ["Microsoft Edge"],
    "vscode": ["Visual Studio Code"],
    "terminal": ["Terminal"],
}

_ALLOWED_APP_RE = re.compile(r"^[A-Za-z0-9 ._+-]+$")


def _validate_app_name(app: str) -> bool:
    return bool(app and _ALLOWED_APP_RE.fullmatch(app))


def _resolve_apps(app: str):
    return APP_ALIASES.get(app, [app])


def _confirm_power_action(action: str) -> bool:
    if not ALLOW_POWER_ACTIONS:
        return False
    if not POWER_CONFIRMATION_REQUIRED:
        return True

    try:
        answer = input(f"Confirm {action}. Type YES to continue: ").strip()
    except EOFError:
        return False

    return answer == "YES"


def open_app(app_name: str) -> str:
    if not _validate_app_name(app_name):
        return "Invalid application name"

    for app in _resolve_apps(app_name):
        result = subprocess.run(["open", "-a", app], check=False)
        if result.returncode == 0:
            return f"Opening {app_name}"

    return f"Failed to open {app_name}"


def close_app(app_name: str) -> str:
    if not _validate_app_name(app_name):
        return "Invalid application name"

    closed_any = False
    for app in _resolve_apps(app_name):
        result = subprocess.run(["osascript", "-e", f'tell application "{app}" to quit'], check=False)
        if result.returncode == 0:
            closed_any = True

    if closed_any:
        return f"Closed {app_name}"
    return f"No running process found for {app_name}"


def lock_screen() -> str:
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "System Events" to keystroke "q" using {control down, command down}',
        ],
        check=False,
    )
    return "Screen locked"


def reboot() -> str:
    if not _confirm_power_action("system reboot"):
        if not ALLOW_POWER_ACTIONS:
            return "Power actions are disabled in config"
        return "Reboot cancelled"

    subprocess.Popen(["osascript", "-e", 'tell application "System Events" to restart'])
    return "Rebooting system"


def shutdown() -> str:
    if not _confirm_power_action("system shutdown"):
        if not ALLOW_POWER_ACTIONS:
            return "Power actions are disabled in config"
        return "Shutdown cancelled"

    subprocess.Popen(["osascript", "-e", 'tell application "System Events" to shut down'])
    return "Shutting down system"


def volume_up() -> str:
    subprocess.run(
        [
            "osascript",
            "-e",
            "set volume output volume ((output volume of (get volume settings)) + 5)",
        ],
        check=False,
    )
    return "Volume increased"


def volume_down() -> str:
    subprocess.run(
        [
            "osascript",
            "-e",
            "set volume output volume ((output volume of (get volume settings)) - 5)",
        ],
        check=False,
    )
    return "Volume decreased"


def mute_volume() -> str:
    subprocess.run(["osascript", "-e", "set volume with output muted"], check=False)
    return "Volume muted"
