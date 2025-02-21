from typing import Any


class BaseType:
    def __init__(self, name: str):
        self.name = name


class BaseAtomicType(BaseType):
    def __init__(self, name: str, value: Any):
        super().__init__(name)
        self.value = value

    def add(self, other: "BaseAtomicType"):
        return self.value + other.value

    def sub(self, other: "BaseAtomicType"):
        return self.value - other.value

    def mul(self, other: "BaseAtomicType"):
        return self.value * other.value

    def div(self, other: "BaseAtomicType"):
        return self.value / other.value

    def mod(self, other: "BaseAtomicType"):
        return self.value % other.value

    def pow(self, other: "BaseAtomicType"):
        return self.value ** other.value

    def eq(self, other: "BaseAtomicType"):
        return self.value == other.value

    def ne(self, other: "BaseAtomicType"):
        return self.value != other.value

    def lt(self, other: "BaseAtomicType"):
        return self.value < other.value

    def le(self, other: "BaseAtomicType"):
        return self.value <= other.value

    def gt(self, other: "BaseAtomicType"):
        return self.value > other.value

    def ge(self, other: "BaseAtomicType"):
        return self.value >= other.value

    def and_(self, other: "BaseAtomicType"):
        return self.value and other.value

    def or_(self, other: "BaseAtomicType"):
        return self.value or other.value

    def not_(self):
        return not self.value

    @classmethod
    def type_name(cls):
        return f"{cls.__name__}"

    def __str__(self):
        return str(self.value)

