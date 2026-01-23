from typing import Optional, Tuple
from intent.rules import INTENTS


def parse_intent(text: str) -> Optional[Tuple[object, Optional[str]]]:
    text = text.lower().strip()
    tokens = text.split()

    for intent in INTENTS:
        if any(keyword in tokens for keyword in intent.keywords):
            arg = None

            if intent.takes_argument:
                # everything after the verb is the argument
                for i, token in enumerate(tokens):
                    if token in intent.keywords and i + 1 < len(tokens):
                        arg = tokens[i + 1]
                        break

            return intent, arg

    return None
