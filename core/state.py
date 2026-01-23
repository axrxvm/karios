from dataclasses import dataclass
from typing import Optional


@dataclass
class KariosState:
    awake: bool = False
    last_user_text: Optional[str] = None
    last_response: Optional[str] = None
    listening: bool = False


STATE = KariosState()
