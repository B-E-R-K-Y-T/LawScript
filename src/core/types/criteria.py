from typing import TYPE_CHECKING
from src.core.types.basetype import BaseType


if TYPE_CHECKING:
    from src.core.types.conditions import Modify


class Criteria(BaseType):
    def __init__(self, name: str, criteria: dict[str, "Modify"]):
        super().__init__(name)
        self.modify: dict[str, "Modify"] = criteria
