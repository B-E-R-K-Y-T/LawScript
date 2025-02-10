from typing import TYPE_CHECKING

from core.types.basetype import BaseType
from core.types.conditions import ResultCondition
from core.types.documents import Document, FactSituation

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled


class CheckerSituation(BaseType):
    def __init__(self, name: str, document: Document, fact_situation: FactSituation):
        super().__init__(name)
        self.document = document
        self.fact_situation = fact_situation
        self.check_result_map = {
            True: "Выполнено",
            False: "Нарушено",
        }

    def check(self, compiled: "Compiled") -> dict[str, ResultCondition]:
        return self.document.hypothesis.condition.execute(
            fact_data=self.fact_situation.data,
            compiled=compiled
        )
