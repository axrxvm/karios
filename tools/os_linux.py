import subprocess
import os
import signal


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
    for binary in APP_ALIASES.get(app, [app]):
        try:
            subprocess.Popen([binary])
            return True
        except FileNotFoundError:
            continue
    return False


def open_app(app: str) -> str:
    if not app:
        return "No application specified"

    if _find_binary(app):
        return f"Opening {app}"

    return f"Failed to open {app}"


def close_app(app: str) -> str:
    try:
        subprocess.run(["pkill", "-f", app], check=False)
        return f"Closed {app}"
    except Exception:
        return f"Failed to close {app}"


def lock_screen() -> str:
    subprocess.Popen(["loginctl", "lock-session"])
    return "Screen locked"


def reboot() -> str:
    subprocess.Popen(["systemctl", "reboot"])
    return "Rebooting system"


def shutdown() -> str:
    subprocess.Popen(["systemctl", "poweroff"])
    return "Shutting down system"


def volume_up() -> str:
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
    return "Volume increased"


def volume_down() -> str:
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
    return "Volume decreased"


def mute_volume() -> str:
    subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
    return "Volume muted"
