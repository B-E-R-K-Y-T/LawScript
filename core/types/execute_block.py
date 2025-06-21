from core.types.basetype import BaseType
from core.types.procedure import Expression


class ExecuteBlock(BaseType):
    def __init__(self, name: str, expressions: list[Expression]):
        super().__init__(name)
        self.expressions = expressions

    def __repr__(self) -> str:
        return f"{ExecuteBlock.__name__}(expressions={self.expressions})"
