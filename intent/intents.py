from typing import Callable, List, Optional, Dict, Any


class Intent:
    def __init__(
        self,
        name: str,
        keywords: List[str],
        executor: Callable[..., str],
        description: str = "",
        takes_argument: bool = False,
    ):
        self.name = name
        self.keywords = keywords
        self.executor = executor
        self.description = description
        self.takes_argument = takes_argument

    @property
    def is_local(self) -> bool:
        return True

    def execute(self, arg: Optional[str] = None) -> str:
        if self.takes_argument:
            return self.executor(arg)
        return self.executor()
