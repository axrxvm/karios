import logging
from typing import Callable, List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class Intent:
    def __init__(
        self,
        name: str,
        keywords: List[str],
        executor: Callable[..., str],
        description: str = "",
        takes_argument: bool = False,
    ):
        logger.debug(f"Intent created: {name} (keywords={keywords}, takes_argument={takes_argument})")
        self.name = name
        self.keywords = keywords
        self.executor = executor
        self.description = description
        self.takes_argument = takes_argument

    @property
    def is_local(self) -> bool:
        return True

    def execute(self, arg: Optional[str] = None) -> str:
        logger.debug(f"Executing intent '{self.name}' with arg={arg}")
        try:
            if self.takes_argument:
                result = self.executor(arg)
            else:
                result = self.executor()
            logger.debug(f"Intent '{self.name}' execution successful: {result}")
            return result
        except Exception as e:
            logger.error(f"Intent '{self.name}' execution failed: {e}", exc_info=True)
            raise
