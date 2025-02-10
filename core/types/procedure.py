from typing import Optional

from core.parse.base import build_rpn_stack
from core.types.basetype import BaseType
from core.types.variable import ScopeStack


class Body(BaseType):
    def __init__(self, name: str, commands: list[BaseType]):
        super().__init__(name)

        self.commands = commands

class CodeBlock(BaseType):
    def __init__(self, name: str, body: Body):
        super().__init__(name)

        self.body = body


class Procedure(BaseType):
    def __init__(self, name: str, body: Body, arguments_names: list[Optional[str]]):
        super().__init__(name)

        self.body = body
        self.arguments_names = arguments_names
        self.tree_variables: Optional[ScopeStack] = None


class Expression(BaseType):
    def __init__(self, name: str, operations):
        super().__init__(name)

        self.operations: list[str] = build_rpn_stack(operations)



class Print(BaseType):
    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class AssignField(BaseType):
    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class Else(CodeBlock):
    def __init__(self, name: str, body: Body):
        super().__init__(name, body)


class When(CodeBlock):
    def __init__(self, name: str, expression: Expression, body: Body, else_: Optional[Else] = None):
        super().__init__(name, body)

        self.expression = expression
        self.else_ = else_


class Return(BaseType):
    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class Loop(CodeBlock):
    def __init__(self, name: str, expression_from: Expression, expression_to: Expression, body: Body):
        super().__init__(name, body)

        self.expression_from = expression_from
        self.expression_to = expression_to
