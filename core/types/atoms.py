from core.types.basetype import BaseAtomicType


class String(BaseAtomicType):
    def __init__(self, name: str, value: str):
        super().__init__(name, value)


class Number(BaseAtomicType):
    def __init__(self, name: str, value: float):
        super().__init__(name, value)
