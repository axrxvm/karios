import os
from enum import Enum


class OS(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MAC = "mac"


def detect_os() -> OS:
    if os.name == "nt":
        return OS.WINDOWS
    elif os.name == "posix":
        if "darwin" in os.sys.platform:
            return OS.MAC
        return OS.LINUX
    raise RuntimeError("Unsupported OS")


# ---- Global Config ----

OS_TYPE = detect_os()

WAKE_WORD = "karios"

STT_SAMPLE_RATE = 16000

LLM_ENABLED = True
LLM_MODEL = "google/gemini-2.5-flash"

DEBUG = True
