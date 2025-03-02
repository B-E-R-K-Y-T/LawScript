from copy import copy, deepcopy
from typing import Optional, Type

from typing_extensions import NamedTuple

from core.parse.base import MetaObject
from core.types.atomic import String
from core.types.basetype import BaseType
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
        this = deepcopy(self.table_image.this)
        body = deepcopy(self.table_image.body)
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
