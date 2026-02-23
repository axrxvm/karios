import logging
from typing import Dict, List, Optional
from core.config import LLM_MODEL, LLM_ENABLED, OPENAI_API_KEY, OPENAI_API_BASE

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    logger.info("OpenAI module imported successfully")
except ImportError:
    logger.warning("OpenAI module not available")
    OpenAI = None


_client: Optional["OpenAI"] = None
_session_histories: Dict[str, List[Dict[str, str]]] = {}
_MAX_CONTEXT_MESSAGES = 12


SYSTEM_PROMPT = (
    "You are Karios, a calm and natural speaking assistant.\n"
    "Your responses are spoken using text to speech.\n"
    "Write exactly how a human would speak.\n"
    "Use short, clear sentences.\n"
    "Use periods and commas to control pacing.\n"
    "Use commas for brief pauses.\n"
    "Use periods to end thoughts.\n"
    "Do not use semicolons, colons, dashes, or slashes.\n"
    "Do not use emojis, symbols, markdown, or special characters.\n"
    "Do not use lists or formatting.\n"
    "Avoid abbreviations. Always write full words.\n"
    "Avoid filler words and unnecessary phrases.\n"
    "Speak directly and conversationally.\n"
    "Be concise, but natural.\n"
    "Respond with plain text only.\n"
)




def _get_client() -> Optional["OpenAI"]:
    global _client
    logger.debug("_get_client() called")

    if not LLM_ENABLED:
        logger.warning("LLM is disabled")
        return None
    
    if OpenAI is None:
        logger.warning("OpenAI module not available")
        return None

    if _client is not None:
        logger.debug("Returning existing OpenAI client")
        return _client

    logger.debug("Creating new OpenAI client...")
    api_key = OPENAI_API_KEY
    api_base = OPENAI_API_BASE or None
    logger.debug(f"API base URL: {api_base}")

    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        return None

    _client = OpenAI(
        api_key=api_key,
        base_url=api_base,
    )
    logger.info("OpenAI client created successfully")

    return _client


def _trim_history(session_id: str) -> None:
    history = _session_histories.get(session_id, [])
    if len(history) > _MAX_CONTEXT_MESSAGES:
        _session_histories[session_id] = history[-_MAX_CONTEXT_MESSAGES:]


def reset_session_context(session_id: str) -> None:
    _session_histories.pop(session_id, None)


def query_llm(user_text: str, session_id: str = "default") -> str:
    logger.info("query_llm() called")
    client = _get_client()

    if client is None:
        logger.error("OpenAI client is not available")
        return "LLM is not available."

    logger.debug("Sending request to LLM model: %s", LLM_MODEL)
    logger.debug("Message length: %d characters", len(user_text))
    history = _session_histories.setdefault(session_id, [])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": user_text}]
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.2,
        )
        logger.debug("LLM response received successfully")
        result = response.choices[0].message.content.strip()
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": result})
        _trim_history(session_id)
        logger.debug("LLM response extracted")
        return result
    except Exception as exc:
        logger.error("Error querying LLM", exc_info=True)
        return f"Error communicating with LLM: {str(exc)}"
