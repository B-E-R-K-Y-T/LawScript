from typing import List

from core.types.basetype import BaseType
from core.types.sanction_types import SanctionType
from core.types.severitys import Severity


class Sanction(BaseType):
    def __init__(self, name: str, type_: SanctionType, severity: Severity, procedural_aspect: str):
        super().__init__(name)
        self.type = type_  # Виды санкций
        self.severity = severity  # Степень строгости
        self.procedural_aspect = procedural_aspect  # Процессуальные аспекты

    def __repr__(self) -> str:
        return (f"Sanction(types={self.type}, "
                f"severity={self.severity}, "
                f"procedural_aspects={self.procedural_aspect})")


class AdministrativeSanction(Sanction):
    def __init__(self, type_: List[SanctionType], severity: Severity, procedural_aspect: List[str],
                 violation_code: str):
        super().__init__(type_, severity, procedural_aspect)
        self.violation_code = violation_code  # Код нарушения

    def __repr__(self) -> str:
        return (f"AdministrativeSanction(types={self.type}, "
                f"severity={self.severity}, "
                f"procedural_aspects={self.procedural_aspect}, "
                f"violation_code='{self.violation_code}')")


class CriminalSanction(Sanction):
    def __init__(self, type_: List[SanctionType], severity: Severity, procedural_aspect: List[str],
                 article_number: str):
        super().__init__(type_, severity, procedural_aspect)
        self.article_number = article_number  # Номер статьи Уголовного кодекса

    def __repr__(self) -> str:
        return (f"CriminalSanction(types={self.type}, "
                f"severity={self.severity}, "
                f"procedural_aspects={self.procedural_aspect}, "
                f"article_number='{self.article_number}')")


class CivilSanction(Sanction):
    def __init__(self, type_: List[SanctionType], severity: Severity, procedural_aspect: List[str],
                 compensation_amount: float):
        super().__init__(type_, severity, procedural_aspect)
        self.compensation_amount = compensation_amount  # Сумма компенсации убытков

    def __repr__(self) -> str:
        return (f"CivilSanction(types={self.type}, "
                f"severity={self.severity}, "
                f"procedural_aspects={self.procedural_aspect}, "
                f"compensation_amount={self.compensation_amount})")
