from typing import Callable, Optional, Tuple
from intent.parser import parse_intent
from llm.openai_client import query_llm
from core.config import DEBUG


class RouteResult:
    def __init__(
        self,
        text: str,
        handled_locally: bool,
        action: Optional[Callable] = None,
        arg: Optional[str] = None,
    ):
        self.text = text
        self.handled_locally = handled_locally
        self.action = action
        self.arg = arg


def route(text: str) -> RouteResult:
    if DEBUG:
        print(f"[ROUTER] Input: {text}")

    parsed = parse_intent(text)

    if parsed:
        intent, arg = parsed

        if intent.is_local:
            if DEBUG:
                print(f"[ROUTER] Local intent: {intent.name} (arg={arg})")

            return RouteResult(
                text=text,
                handled_locally=True,
                action=intent.execute,
                arg=arg,
            )

    if DEBUG:
        print("[ROUTER] Escalating to LLM")

    response = query_llm(text)

    return RouteResult(
        text=response,
        handled_locally=False,
    )
