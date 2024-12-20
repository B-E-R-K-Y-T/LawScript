from typing import List

from core.types.basetype import BaseType
from core.types.obligations import Obligation
from core.types.laws import Law
from core.types.rules import Rule


class Disposition(BaseType):
    def __init__(self, name: str, law: Law, obligation: Obligation, rules: Rule):
        super().__init__(name)
        self.law = law  # Права
        self.obligation = obligation  # Обязанности
        self.rule = rules  # Прямые правила

    def __repr__(self) -> str:
        return (f"Disposition(rights={self.law}, "
                f"obligations={self.obligation}, "
                f"rules={self.rule})")

