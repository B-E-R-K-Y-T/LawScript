from copy import deepcopy
from typing import Optional, Type, Any

from typing_extensions import NamedTuple

from core.parse.base import MetaObject
from core.types.atomic import String
from core.types.basetype import BaseType, BaseAtomicType
from core.types.procedure import Body
from core.types.variable import ScopeStack, Variable


class Table(BaseType):
    def __init__(self, name: str, body: Body):
        super().__init__(name)

        self.body = body
        self.this: Optional[This] = None
        self.base_table: Optional[Table] = None
        self.tree_variables: Optional[ScopeStack] = None


class This(NamedTuple):
    name: str
    link: Table

class Field(BaseAtomicType):
    def __init__(self, link: BaseAtomicType, name: str = ""):
        self.link = link
        self.__value = link.value
        super().__init__(link.value, name)

    def add(self, other: "BaseAtomicType"):
        self.link.value = self.__value + other.value
        return self.link

    def sub(self, other: "BaseAtomicType"):
        self.link.value = self.__value - other.value
        return self.link

    def neg(self):
        self.link.value = -self.__value
        return self.link

    def pos(self):
        self.link.value = +self.__value
        return self.link

    def mul(self, other: "BaseAtomicType"):
        self.link.value = self.__value * other.value
        return self.link

    def div(self, other: "BaseAtomicType"):
        self.link.value = self.__value / other.value
        return self.link

    def mod(self, other: "BaseAtomicType"):
        self.link.value = self.__value % other.value
        return self.link

    def pow(self, other: "BaseAtomicType"):
        self.link.value = self.__value ** other.value
        return self.link

    def eq(self, other: "BaseAtomicType"):
        return self.__value == other.value

    def ne(self, other: "BaseAtomicType"):
        return self.__value != other.value

    def lt(self, other: "BaseAtomicType"):
        return self.__value < other.value

    def le(self, other: "BaseAtomicType"):
        return self.__value <= other.value

    def gt(self, other: "BaseAtomicType"):
        return self.__value > other.value

    def ge(self, other: "BaseAtomicType"):
        return self.__value >= other.value

    def and_(self, other: "BaseAtomicType"):
        self.link.value = self.__value and other.value
        return self.link

    def or_(self, other: "BaseAtomicType"):
        self.link.value = self.__value or other.value
        return self.link

    def not_(self):
        self.link.value = not self.__value
        return self.link

    def __repr__(self) -> str:
        return str(self.value)


class TableImage(NamedTuple):
    table: Type[Table]
    body: [Body, MetaObject]
    this: String
    base_table: Optional[Table] = None


class TableFactory(BaseType):
    def __init__(self, name: str, table_image: TableImage):
        super().__init__(name)
        self.table_image = table_image

    def create_table(self) -> Table:
        name = self.name
        this = self.table_image.this
        body = self.table_image.body
        base = self.table_image.base_table

        instance_table = self.table_image.table(
            name=name,
            body=body,
        )

        instance_table.this = This(self.table_image.this.value, instance_table)
        instance_table.tree_variables = ScopeStack()
        instance_table.tree_variables.set(Variable(this.value, instance_table.this))
        instance_table.base_table = base

        return instance_table
