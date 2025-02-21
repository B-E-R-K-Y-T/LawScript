from typing import Union

from core.types.basetype import BaseAtomicType


class String(BaseAtomicType):
    def __init__(self, value: str):
        super().__init__(str(), value)


class Number(BaseAtomicType):
    def __init__(self, value: Union[float, int]):
        super().__init__(str(), value)


class Void(BaseAtomicType):
    def __init__(self):
        super().__init__(str(), None)

    def __str__(self):
        return "<void>"
