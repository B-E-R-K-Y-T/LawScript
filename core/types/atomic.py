from typing import Union

from core.types.basetype import BaseAtomicType


class String(BaseAtomicType):
    def __init__(self, name: str, value: str):
        super().__init__(name, value)


class Number(BaseAtomicType):
    def __init__(self, name: str, value: Union[float, int]):
        super().__init__(name, value)


class Void(BaseAtomicType):
    def __init__(self, name: str):
        super().__init__(name, None)

    def __str__(self):
        return "<void>"
