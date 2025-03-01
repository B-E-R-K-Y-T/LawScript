from typing import Optional, Type

from typing_extensions import NamedTuple

from core.parse.base import MetaObject
from core.types.atomic import String
from core.types.basetype import BaseType
from core.types.procedure import Body
from core.types.variable import ScopeStack


class Table(BaseType):
    def __init__(self, name: str, body: Body):
        super().__init__(name)

        self.body = body
        self.this: Optional[Table] = None
        self.base_table: Optional[Table] = None
        self.tree_variables: Optional[ScopeStack] = None


class TableImage(NamedTuple):
    table: Type[Table]
    body: [Body, MetaObject]
    this: String
    base_table: Optional[Table] = None


class TableFactory(BaseType):
    def __init__(self, name: str, table_image: TableImage):
        super().__init__(name)
        self.table_image = table_image
