from typing import List

from core.types.base_declarative_type import BaseDeclarativeType
from core.types.obligations import Obligation
from core.types.laws import Law
from core.types.rules import Rule


class Disposition(BaseDeclarativeType):
    def __init__(self, name: str, law: Law, obligation: Obligation, rules: Rule):
        super().__init__(name)
        self.law = law  # Права
        self.obligation = obligation  # Обязанности
        self.rule = rules  # Прямые правила

    def __repr__(self) -> str:
        return (f"Disposition(__право__={self.law}, "
                f"__обязанность__={self.obligation}, "
                f"__правило__={self.rule})")
