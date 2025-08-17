from typing import Union

from core.types.atomic import String
from core.types.base_declarative_type import BaseDeclarativeType
from core.types.sanction_types import SanctionType
from core.types.severitys import Severity


class Sanction(BaseDeclarativeType):
    def __init__(self, name: str, type_: list[SanctionType], severity: Union[Severity, str], procedural_aspect: str):
        super().__init__(name)
        self.type = type_  # Виды санкций
        self.severity = severity  # Степень строгости
        self.procedural_aspect = procedural_aspect  # Процессуальные аспекты

        self.fields["__степень_строгости__"] = String(self.severity)
        self.fields["__процессуальный_аспект__"] = String(self.procedural_aspect)

    def __repr__(self) -> str:
        return (f"Sanction(types={self.type}, "
                f"severity={self.severity}, "
                f"procedural_aspects={self.procedural_aspect})")
