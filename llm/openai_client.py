import os
import logging
from typing import Optional
from dotenv import load_dotenv
from core.config import LLM_MODEL, LLM_ENABLED

logger = logging.getLogger(__name__)

# Load .env into environment variables
logger.debug("Loading environment variables from .env...")
load_dotenv()
logger.debug(".env file loaded")

try:
    from openai import OpenAI
    logger.info("OpenAI module imported successfully")
except ImportError:
    logger.warning("OpenAI module not available")
    OpenAI = None


_client: Optional["OpenAI"] = None


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
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
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


def query_llm(user_text: str) -> str:
    logger.info(f"query_llm() called with user_text: {user_text}")
    client = _get_client()

    if client is None:
        logger.error("OpenAI client is not available")
        return "LLM is not available."

    logger.debug(f"Sending request to LLM model: {LLM_MODEL}")
    logger.debug(f"Message length: {len(user_text)} characters")
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.2,
        )
        logger.debug(f"LLM response received successfully")
        result = response.choices[0].message.content.strip()
        logger.debug(f"LLM response: {result[:100]}...")
        return result
    except Exception as e:
        logger.error(f"Error querying LLM: {e}", exc_info=True)
        return f"Error communicating with LLM: {str(e)}"
