import logging
import os
import sys
from enum import Enum

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class OS(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MAC = "mac"


def detect_os() -> OS:
    logger.debug(f"Detecting OS... os.name={os.name}, sys.platform={sys.platform}")
    if os.name == "nt":
        logger.info("OS detected: WINDOWS")
        return OS.WINDOWS
    elif os.name == "posix":
        if "darwin" in sys.platform:
            logger.info("OS detected: MAC")
            return OS.MAC
        logger.info("OS detected: LINUX")
        return OS.LINUX
    logger.error(f"Unsupported OS detected: os.name={os.name}")
    raise RuntimeError("Unsupported OS")


# ---- Global Config ----

OS_TYPE = detect_os()
logger.debug(f"OS_TYPE set to: {OS_TYPE}")

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


def _get_bool(name: str) -> bool:
    value = _require_env(name)
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"Invalid boolean for {name}: {value}")


def _get_int(name: str) -> int:
    value = _require_env(name)
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid integer for {name}: {value}") from exc


def _get_optional(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        return ""
    return value.strip()


WAKE_WORD = _require_env("KARIOS_WAKE_WORD")
logger.debug(f"WAKE_WORD set to: {WAKE_WORD}")

STT_SAMPLE_RATE = _get_int("KARIOS_STT_SAMPLE_RATE")
logger.debug(f"STT_SAMPLE_RATE set to: {STT_SAMPLE_RATE}")

VOSK_MODEL_PATH = _require_env("KARIOS_VOSK_MODEL_PATH")
PIPER_MODEL_PATH = _require_env("KARIOS_PIPER_MODEL_PATH")
logger.debug(f"VOSK_MODEL_PATH={VOSK_MODEL_PATH}, PIPER_MODEL_PATH={PIPER_MODEL_PATH}")

LLM_ENABLED = _get_bool("KARIOS_LLM_ENABLED")
LLM_MODEL = _require_env("KARIOS_LLM_MODEL")
logger.debug(f"LLM_ENABLED={LLM_ENABLED}, LLM_MODEL={LLM_MODEL}")

DEBUG = _get_bool("KARIOS_DEBUG")
logger.debug(f"DEBUG mode set to: {DEBUG}")

LOG_LEVEL = _require_env("KARIOS_LOG_LEVEL").upper()
logger.debug(f"LOG_LEVEL set to: {LOG_LEVEL}")

ALLOW_POWER_ACTIONS = _get_bool("KARIOS_ALLOW_POWER_ACTIONS")
POWER_CONFIRMATION_REQUIRED = _get_bool("KARIOS_REQUIRE_POWER_CONFIRMATION")
logger.debug(
    "ALLOW_POWER_ACTIONS=%s, POWER_CONFIRMATION_REQUIRED=%s",
    ALLOW_POWER_ACTIONS,
    POWER_CONFIRMATION_REQUIRED,
)

OPENAI_API_KEY = _get_optional("OPENAI_API_KEY")
OPENAI_API_BASE = _get_optional("OPENAI_API_BASE")
