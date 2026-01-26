import logging
from typing import Callable, Optional, Tuple
from intent.parser import parse_intent
from llm.openai_client import query_llm
from core.config import DEBUG

logger = logging.getLogger(__name__)


class RouteResult:
    def __init__(
        self,
        text: str,
        handled_locally: bool,
        action: Optional[Callable] = None,
        arg: Optional[str] = None,
    ):
        logger.debug(f"RouteResult created: handled_locally={handled_locally}, text={text[:50]}..., arg={arg}")
        self.text = text
        self.handled_locally = handled_locally
        self.action = action
        self.arg = arg


def route(text: str) -> RouteResult:
    logger.info(f"route() called with text: {text}")
    if DEBUG:
        print(f"[ROUTER] Input: {text}")

    logger.debug("Parsing intent...")
    parsed = parse_intent(text)
    logger.debug(f"Intent parsing result: {parsed}")

    if parsed:
        intent, arg = parsed
        logger.debug(f"Intent parsed - name: {intent.name}, is_local: {intent.is_local}, arg: {arg}")

        if intent.is_local:
            if DEBUG:
                print(f"[ROUTER] Local intent: {intent.name} (arg={arg})")
            logger.info(f"Routing to local intent: {intent.name}")

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
    response = query_llm(text)
    logger.debug(f"LLM response received: {response[:100]}...")

    return RouteResult(
        text=response,
        handled_locally=False,
    )
