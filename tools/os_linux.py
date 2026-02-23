import logging
import re
import shutil
import subprocess

from core.config import ALLOW_POWER_ACTIONS, POWER_CONFIRMATION_REQUIRED

logger = logging.getLogger(__name__)

APP_ALIASES = {
    "chrome": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
    "firefox": ["firefox"],
    "brave": ["brave-browser", "brave"],
    "edge": ["microsoft-edge"],
    "vscode": ["code"],
    "code": ["code"],
    "terminal": ["gnome-terminal", "konsole", "xfce4-terminal"],
    "editor": ["nano", "vim"],
    "spotify": ["spotify"],
    "vlc": ["vlc"],
    "music": ["spotify", "vlc"],
    "files": ["nautilus", "dolphin", "thunar"],
    "settings": ["gnome-control-center"],
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
        logger.warning("Power action blocked by config: %s", action)
        return False

    if not POWER_CONFIRMATION_REQUIRED:
        return True

    try:
        answer = input(f"Confirm {action}. Type YES to continue: ").strip()
    except EOFError:
        logger.warning("Power action confirmation failed due to EOF")
        return False

    return answer == "YES"


def open_app(app: str) -> str:
    logger.info("open_app() called with app: %s", app)
    if not _validate_app_name(app):
        return "Invalid application name"

    binary = _first_installed_binary(app)
    if not binary:
        return f"Failed to open {app}"

    try:
        subprocess.Popen([binary])
        return f"Opening {app}"
    except Exception:
        logger.exception("Failed to open app: %s", app)
        return f"Failed to open {app}"


def close_app(app: str) -> str:
    logger.info("close_app() called with app: %s", app)
    if not _validate_app_name(app):
        return "Invalid application name"

    closed_any = False
    for binary in _resolve_binaries(app):
        result_proc = subprocess.run(["pkill", "-x", binary], check=False)
        if result_proc.returncode == 0:
            closed_any = True

    if closed_any:
        return f"Closed {app}"
    return f"No running process found for {app}"


def lock_screen() -> str:
    logger.info("lock_screen() called")
    subprocess.Popen(["loginctl", "lock-session"])
    return "Screen locked"


def reboot() -> str:
    logger.info("reboot() called")
    if not _confirm_power_action("system reboot"):
        if not ALLOW_POWER_ACTIONS:
            return "Power actions are disabled in config"
        return "Reboot cancelled"

    subprocess.Popen(["systemctl", "reboot"])
    return "Rebooting system"


def shutdown() -> str:
    logger.info("shutdown() called")
    if not _confirm_power_action("system shutdown"):
        if not ALLOW_POWER_ACTIONS:
            return "Power actions are disabled in config"
        return "Shutdown cancelled"

    subprocess.Popen(["systemctl", "poweroff"])
    return "Shutting down system"


def volume_up() -> str:
    logger.info("volume_up() called")
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"], check=False)
    return "Volume increased"


def volume_down() -> str:
    logger.info("volume_down() called")
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"], check=False)
    return "Volume decreased"


def mute_volume() -> str:
    logger.info("mute_volume() called")
    subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], check=False)
    return "Volume muted"
