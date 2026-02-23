import logging
from typing import Optional, Tuple
from intent.intents import Intent
from intent.rules import INTENTS

logger = logging.getLogger(__name__)


_INTENT_KEYWORD_SETS = tuple(
    (intent, frozenset(intent.keywords))
    for intent in INTENTS
)


def parse_intent(text: str) -> Optional[Tuple[Intent, Optional[str]]]:
    logger.debug("parse_intent() called")
    tokens = text.lower().strip().split()
    if not tokens:
        logger.info("No intent matched")
        return None

    token_set = set(tokens)
    logger.debug("Token count: %d", len(tokens))

    for intent, keyword_set in _INTENT_KEYWORD_SETS:
        logger.debug("Checking intent '%s'", intent.name)
        if token_set.intersection(keyword_set):
            logger.debug("Keyword match found for intent '%s'", intent.name)
            arg = None

            if intent.takes_argument:
                logger.debug("Intent '%s' requires argument, extracting", intent.name)
                # Keep existing behavior, argument is first token after first matched keyword.
                for i, token in enumerate(tokens):
                    if token in keyword_set and i + 1 < len(tokens):
                        arg = tokens[i + 1]
                        logger.debug("Argument extracted")
                        break

            logger.info("Intent matched: %s", intent.name)
            return intent, arg

    logger.info("No intent matched")
    return None
