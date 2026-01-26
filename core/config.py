import os
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class OS(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MAC = "mac"


def detect_os() -> OS:
    logger.debug(f"Detecting OS... os.name={os.name}, sys.platform={os.sys.platform}")
    if os.name == "nt":
        logger.info("OS detected: WINDOWS")
        return OS.WINDOWS
    elif os.name == "posix":
        if "darwin" in os.sys.platform:
            logger.info("OS detected: MAC")
            return OS.MAC
        logger.info("OS detected: LINUX")
        return OS.LINUX
    logger.error(f"Unsupported OS detected: os.name={os.name}")
    raise RuntimeError("Unsupported OS")


# ---- Global Config ----

OS_TYPE = detect_os()
logger.debug(f"OS_TYPE set to: {OS_TYPE}")

WAKE_WORD = "karios"
logger.debug(f"WAKE_WORD set to: {WAKE_WORD}")

STT_SAMPLE_RATE = 16000
logger.debug(f"STT_SAMPLE_RATE set to: {STT_SAMPLE_RATE}")

LLM_ENABLED = True
LLM_MODEL = "google/gemini-2.5-flash"
logger.debug(f"LLM_ENABLED={LLM_ENABLED}, LLM_MODEL={LLM_MODEL}")

DEBUG = True
logger.debug(f"DEBUG mode set to: {DEBUG}")
