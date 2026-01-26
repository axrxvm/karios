import logging
from typing import Optional, Tuple
from intent.rules import INTENTS

logger = logging.getLogger(__name__)


def parse_intent(text: str) -> Optional[Tuple[object, Optional[str]]]:
    logger.debug(f"parse_intent() called with text: {text}")
    text = text.lower().strip()
    tokens = text.split()
    logger.debug(f"Tokens: {tokens}")

    for intent in INTENTS:
        logger.debug(f"Checking intent '{intent.name}' with keywords {intent.keywords}")
        if any(keyword in tokens for keyword in intent.keywords):
            logger.debug(f"Keyword match found for intent '{intent.name}'")
            arg = None

            if intent.takes_argument:
                logger.debug(f"Intent '{intent.name}' requires argument, extracting...")
                # everything after the verb is the argument
                for i, token in enumerate(tokens):
                    if token in intent.keywords and i + 1 < len(tokens):
                        arg = tokens[i + 1]
                        logger.debug(f"Argument extracted: {arg}")
                        break

            logger.info(f"Intent matched: {intent.name}, arg={arg}")
            return intent, arg

    logger.info("No intent matched")
    return None
