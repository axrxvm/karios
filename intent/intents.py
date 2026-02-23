import logging
from dataclasses import dataclass
from typing import Callable, Optional, Sequence

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Intent:
    name: str
    keywords: Sequence[str]
    executor: Callable[..., str]
    description: str = ""
    takes_argument: bool = False

    def __post_init__(self) -> None:
        logger.debug(
            "Intent created: %s (keywords=%s, takes_argument=%s)",
            self.name,
            self.keywords,
            self.takes_argument,
        )

    @property
    def is_local(self) -> bool:
        return True

    def execute(self, arg: Optional[str] = None) -> str:
        logger.debug("Executing intent '%s' with arg=%s", self.name, arg)
        try:
            if self.takes_argument:
                result = self.executor(arg)
            else:
                result = self.executor()
            logger.debug("Intent '%s' execution successful", self.name)
            return result
        except Exception:
            logger.error("Intent '%s' execution failed", self.name, exc_info=True)
            raise
