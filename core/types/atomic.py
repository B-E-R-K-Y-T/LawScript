from typing import Union

from core.types.basetype import BaseAtomicType


class String(BaseAtomicType):
    def __init__(self, value: str):
        super().__init__(str(), value)


class Number(BaseAtomicType):
    def __init__(self, value: Union[float, int]):
        super().__init__(str(), value)

    def __str__(self) -> str:
        if isinstance(self.value, float):
            if self.value == float("inf"):
                return "Бесконечность."
            elif self.value == float("-inf"):
                return "Отрицательная бесконечность."

        return str(self.value)


class Void(BaseAtomicType):
    def __init__(self):
        super().__init__(str(), None)

    def __str__(self) -> str:
        return "<void>"
