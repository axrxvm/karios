import subprocess


def open_app(app_name: str) -> str:
    try:
        subprocess.Popen([app_name])
        return f"Opening {app_name}"
    except Exception:
        return f"Failed to open {app_name}"
