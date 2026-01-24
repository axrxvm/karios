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
