from typing import Any, Optional, TYPE_CHECKING, Union

from core.types.line import Info

if TYPE_CHECKING:
    from core.types.classes import ClassField


class BaseType:
    def __init__(self, name: str):
        self.meta_info: Optional[Info] = None
        self.name = name

    def set_info(self, meta_info: Info):
        self.meta_info = meta_info

    def __repr__(self):
        return f"Служебное имя: <{self.name if self.name else 'ОТСУТСТВУЕТ'}>"


class BaseAtomicType(BaseType):
    def __init__(self, value: Any):
        super().__init__(str())
        self.value = value
        self.fields: dict[str, Union["ClassField[BaseAtomicType]", "BaseAtomicType"]] = {}

    def add(self, other: "BaseAtomicType"):
        return self.value + other.value

    def sub(self, other: "BaseAtomicType"):
        return self.value - other.value

    def neg(self):
        return -self.value

    def pos(self):
        return +self.value

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

    def get_attribute(self, name: str) -> "ClassField":
        from core.types.classes import ClassField

        if isinstance(self, ClassField):
            return self.value.get_attribute(name)

        return self.fields.setdefault(name, ClassField())

    @classmethod
    def type_name(cls):
        return f"{cls.__name__}"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.type_name()}({self.value})"
