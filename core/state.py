import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class KariosState:
    awake: bool = False
    last_user_text: Optional[str] = None
    last_response: Optional[str] = None
    listening: bool = False
    
    def __setattr__(self, name, value):
        logger.debug(f"STATE.{name} = {value}")
        super().__setattr__(name, value)


logger.debug("Initializing KariosState...")
STATE = KariosState()
logger.info("KariosState initialized")
