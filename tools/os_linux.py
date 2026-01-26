import logging
import subprocess
import os
import signal

logger = logging.getLogger(__name__)


APP_ALIASES = {
    # Browsers
    "chrome": ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
    "firefox": ["firefox"],
    "brave": ["brave-browser", "brave"],
    "edge": ["microsoft-edge"],

    # Dev
    "vscode": ["code"],
    "code": ["code"],
    "terminal": ["gnome-terminal", "konsole", "xfce4-terminal"],
    "editor": ["nano", "vim"],

    # Media
    "spotify": ["spotify"],
    "vlc": ["vlc"],
    "music": ["spotify", "vlc"],

    # System
    "files": ["nautilus", "dolphin", "thunar"],
    "settings": ["gnome-control-center"],
}


def _find_binary(app: str):
    logger.debug(f"_find_binary() called for app: {app}")
    binaries = APP_ALIASES.get(app, [app])
    logger.debug(f"Trying binaries: {binaries}")
    for binary in binaries:
        try:
            logger.debug(f"Attempting to launch: {binary}")
            subprocess.Popen([binary])
            logger.info(f"Successfully launched: {binary}")
            return True
        except FileNotFoundError:
            logger.debug(f"Binary not found: {binary}")
            continue
    logger.warning(f"No binary found for app: {app}")
    return False


def open_app(app: str) -> str:
    logger.info(f"open_app() called with app: {app}")
    if not app:
        logger.warning("No application specified")
        return "No application specified"

    if _find_binary(app):
        result = f"Opening {app}"
        logger.info(result)
        return result

    result = f"Failed to open {app}"
    logger.error(result)
    return result


def close_app(app: str) -> str:
    logger.info(f"close_app() called with app: {app}")
    try:
        logger.debug(f"Running pkill -f {app}")
        result_proc = subprocess.run(["pkill", "-f", app], check=False)
        logger.debug(f"pkill return code: {result_proc.returncode}")
        result = f"Closed {app}"
        logger.info(result)
        return result
    except Exception as e:
        result = f"Failed to close {app}"
        logger.error(f"{result}: {e}", exc_info=True)
        return result


def lock_screen() -> str:
    logger.info("lock_screen() called")
    logger.debug("Executing loginctl lock-session")
    subprocess.Popen(["loginctl", "lock-session"])
    result = "Screen locked"
    logger.info(result)
    return result


def reboot() -> str:
    logger.info("reboot() called")
    logger.warning("SYSTEM REBOOT INITIATED")
    subprocess.Popen(["systemctl", "reboot"])
    return "Rebooting system"


def shutdown() -> str:
    logger.info("shutdown() called")
    logger.warning("SYSTEM SHUTDOWN INITIATED")
    subprocess.Popen(["systemctl", "poweroff"])
    return "Shutting down system"


def volume_up() -> str:
    logger.info("volume_up() called")
    logger.debug("Increasing volume by 5%")
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
    result = "Volume increased"
    logger.info(result)
    return result


def volume_down() -> str:
    logger.info("volume_down() called")
    logger.debug("Decreasing volume by 5%")
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
    result = "Volume decreased"
    logger.info(result)
    return result


def mute_volume() -> str:
    logger.info("mute_volume() called")
    logger.debug("Toggling mute")
    subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
    result = "Volume muted"
    logger.info(result)
    return result
