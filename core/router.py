import logging
from dataclasses import dataclass
from typing import Callable, Optional
from intent.parser import parse_intent
from llm.openai_client import query_llm
from core.config import DEBUG

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RouteResult:
    text: str
    handled_locally: bool
    action: Optional[Callable] = None
    arg: Optional[str] = None


def route(text: str, session_id: str = "default") -> RouteResult:
    logger.info("route() called")
    if DEBUG:
        print(f"[ROUTER] Input: {text}")

    logger.debug("Parsing intent...")
    parsed = parse_intent(text)
    logger.debug("Intent parsing complete")

    if parsed:
        intent, arg = parsed
        logger.debug("Intent parsed - name: %s, is_local: %s", intent.name, intent.is_local)

        if intent.is_local:
            if DEBUG:
                print(f"[ROUTER] Local intent: {intent.name} (arg={arg})")
            logger.info("Routing to local intent: %s", intent.name)

            return RouteResult(
                text=text,
                handled_locally=True,
                action=intent.execute,
                arg=arg,
            )

    if DEBUG:
        print("[ROUTER] Escalating to LLM")
    logger.info("No local intent matched, escalating to LLM")

    logger.debug("Querying LLM...")
    response = query_llm(text, session_id=session_id)
    logger.debug("LLM response received")

    return RouteResult(
        text=response,
        handled_locally=False,
    )
