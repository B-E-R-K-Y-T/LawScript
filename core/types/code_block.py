from typing import Optional

from core.types.basetype import BaseType
from core.types.docs import Docs


class Body(BaseType):
    __slots__ = ("commands", "docs")

    def __init__(self, name: str, commands: list[BaseType], docs: Optional[Docs] = None):
        super().__init__(name)

        self.commands = commands
        self.docs = docs


class CodeBlock(BaseType):
    __slots__ = ('body',)

    def __init__(self, name: str, body: Body):
        super().__init__(name)

        self.body = body
