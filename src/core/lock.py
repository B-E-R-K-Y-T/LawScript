from threading import Lock
from typing import Final

GLOBAL_LOCK: Final[Lock] = Lock()
