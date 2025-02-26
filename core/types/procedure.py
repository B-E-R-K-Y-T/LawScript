from typing import Optional, Union

from core.parse.util.rpn import build_rpn_stack
from core.types.basetype import BaseType, BaseAtomicType
from core.types.line import Info
from core.types.operation import Operator
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

    def __repr__(self):
        return f'Процедура({self.name}, {self.body}, {self.arguments_names})'


class Expression(BaseType):
    def __init__(self, name: str, operations, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line
        self.operations: list[Union[Operator, BaseAtomicType]] = build_rpn_stack(operations, self.meta_info)


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
