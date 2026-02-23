import logging
import re
import shutil
import subprocess

from core.config import ALLOW_POWER_ACTIONS, POWER_CONFIRMATION_REQUIRED

logger = logging.getLogger(__name__)

APP_ALIASES = {
    "chrome": ["chrome"],
    "firefox": ["firefox"],
    "edge": ["msedge"],
    "vscode": ["code"],
    "terminal": ["wt", "cmd", "powershell"],
}

_ALLOWED_APP_RE = re.compile(r"^[A-Za-z0-9._+-]+$")


def _validate_app_name(app: str) -> bool:
    return bool(app and _ALLOWED_APP_RE.fullmatch(app))


def _resolve_binaries(app: str):
    return APP_ALIASES.get(app, [app])


def _first_installed_binary(app: str):
    for binary in _resolve_binaries(app):
        if shutil.which(binary):
            return binary
    return None


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

    binary = _first_installed_binary(app_name)
    if not binary:
        return f"Failed to open {app_name}"

    try:
        subprocess.Popen([binary], shell=False)
        return f"Opening {app_name}"
    except Exception:
        logger.exception("Failed to open app: %s", app_name)
        return f"Failed to open {app_name}"


def close_app(app_name: str) -> str:
    if not _validate_app_name(app_name):
        return "Invalid application name"

    image_names = []
    for binary in _resolve_binaries(app_name):
        image_names.append(binary if binary.lower().endswith(".exe") else f"{binary}.exe")

    closed_any = False
    for image in image_names:
        result = subprocess.run(["taskkill", "/IM", image, "/F"], check=False)
        if result.returncode == 0:
            closed_any = True

    if closed_any:
        return f"Closed {app_name}"
    return f"No running process found for {app_name}"


def lock_screen() -> str:
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
    return "Screen locked"


def reboot() -> str:
    if not _confirm_power_action("system reboot"):
        if not ALLOW_POWER_ACTIONS:
            return "Power actions are disabled in config"
        return "Reboot cancelled"

    subprocess.Popen(["shutdown", "/r", "/t", "0"])
    return "Rebooting system"


def shutdown() -> str:
    if not _confirm_power_action("system shutdown"):
        if not ALLOW_POWER_ACTIONS:
            return "Power actions are disabled in config"
        return "Shutdown cancelled"

    subprocess.Popen(["shutdown", "/s", "/t", "0"])
    return "Shutting down system"


def volume_up() -> str:
    return "Volume control is not implemented for Windows yet"


def volume_down() -> str:
    return "Volume control is not implemented for Windows yet"


def mute_volume() -> str:
    return "Volume control is not implemented for Windows yet"
