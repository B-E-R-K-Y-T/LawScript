from enum import StrEnum

from core.types.basetype import BaseType


class Levels(StrEnum):
    LOW = "НИЗКАЯ"
    MEDIUM = "СРЕДНЯЯ"
    HIGH = "ВЫСОКАЯ"
    VERY_HIGH = "ОЧЕНЬ_ВЫСОКАЯ"


class Severity(BaseType):
    def __init__(self, name: str,  level: Levels):
        super().__init__(name)
        self.level = level  # Уровень строгости

    def __repr__(self) -> str:
        return f"Severity(level='{self.level}')"


SEVERITY_LOW = Severity(str(), Levels.LOW)
SEVERITY_MEDIUM = Severity(str(), Levels.MEDIUM)
SEVERITY_HIGH = Severity(str(), Levels.HIGH)
SEVERITY_VERY_HIGH = Severity(str(), Levels.VERY_HIGH)
