import os
from typing import Optional
from dotenv import load_dotenv
from core.config import LLM_MODEL, LLM_ENABLED

# Load .env into environment variables
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


_client: Optional["OpenAI"] = None


SYSTEM_PROMPT = (
    "You are Karios\n"
    "Respond for text to speech output\n"
    "Use commas, periods as required for natural speech\n"
    "Use simple natural sentences\n"
    "Avoid symbols emojis markdown and special characters\n"
    "Avoid lists and formatting\n"
    "Prefer short sentences\n"
    "Use minimal punctuation\n"
    "Do not use commas unless required for clarity\n"
    "Do not use semicolons colons or dashes\n"
    "Avoid abbreviations\n"
    "Speak clearly and conversationally\n"
    "Be concise\n"
    "No filler\n"
    "Answer directly\n"
)



def _get_client() -> Optional["OpenAI"]:
    global _client

    if not LLM_ENABLED or OpenAI is None:
        return None

    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")

    if not api_key:
        return None

    _client = OpenAI(
        api_key=api_key,
        base_url=api_base,
    )

    return _client


def query_llm(user_text: str) -> str:
    client = _get_client()

    if client is None:
        return "LLM is not available."

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
