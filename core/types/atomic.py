from typing import Union

from core.tokens import Tokens
from core.types.basetype import BaseAtomicType


class String(BaseAtomicType):
    def __init__(self, value: str):
        super().__init__(value)


    def __hash__(self) -> int:
        return hash(self.value)


    def __eq__(self, other):
        if isinstance(other, String):
            return self.value == other.value

        return False


class Number(BaseAtomicType):
    def __init__(self, value: Union[float, int]):
        super().__init__(value)

    def is_int(self) -> bool:
        return isinstance(self.value, int)

    def __str__(self) -> str:
        if isinstance(self.value, float):
            if self.value == float("inf"):
                return "Бесконечность"
            elif self.value == float("-inf"):
                return "Отрицательная бесконечность"

        return str(self.value)


class Boolean(BaseAtomicType):
    def __init__(self, value: bool):
        super().__init__(value)

    def __str__(self):
        if self.value:
            return Tokens.true
        else:
            return Tokens.false


class Array(BaseAtomicType):
    def __init__(self, value: list[BaseAtomicType]):
        super().__init__(value)

    def append(self, obj: BaseAtomicType):
        self.value.append(obj)

    def remove(self, idx: Number):
        del self.value[idx.value]

    def index(self, idx: Number):
        return self.value[idx.value]

    def pop(self, idx: Number):
        return self.value.pop(idx.value)

    def len(self) -> Number:
        return Number(len(self.value))

    def __contains__(self, idx: Number):
        return idx in self.value

    def __len__(self):
        return len(self.value)

    def __str__(self):
        result = ""

        for value in self.value:
            result += ", "

            if isinstance(value, String):
                result += f"\"{value}\""
            else:
                result += str(value)

        return "[" + result[2:] + "]"

    def __setitem__(self, key, value):
        self.value[key] = value

    def __getitem__(self, item):
        return self.value[item]


class Table(BaseAtomicType):
    def __init__(self, value: dict[String, BaseAtomicType]):
        super().__init__(value)

    def get(self, key: String):
        return self.value[key]

    def set(self, key: String, value: BaseAtomicType):
        self.value[key] = value

    def del_(self, key: String):
        del self.value[key]

    def len(self) -> Number:
        return Number(len(self.value))

    def __contains__(self, key):
        return key in self.value

    def __getitem__(self, item: String):
        return self.value[item]

    def __setitem__(self, key: String, value: BaseAtomicType):
        self.value[key] = value

    def __len__(self):
        return len(self.value)

    def __str__(self) -> str:
        result = ""

        for key, value in self.value.items():
            result += ", "

            if isinstance(value, String):
                result += f"\"{key}\": \"{value}\""
            else:
                result += f"\"{key}\": {value}"

        return "{" + result[2:] + "}"


class Void(BaseAtomicType):
    def __init__(self):
        super().__init__(None)

    def __str__(self) -> str:
        return Tokens.void
