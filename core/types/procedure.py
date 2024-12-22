from typing import Optional, Union

from core.types.basetype import BaseType
from core.types.variable import Variable


class Body(BaseType):
    def __init__(self, name: str, commands: list[BaseType]):
        super().__init__(name)

        self.commands = commands


class Procedure(BaseType):
    def __init__(self, name: str, body: Body, arguments_names: list[Optional[str]]):
        super().__init__(name)

        self.body = body
        self.arguments_names = arguments_names
        self.tree_variables: dict[str, Variable] = {}


class Expression(BaseType):
    def __init__(self, name: str, operations):
        super().__init__(name)

        self.operations: list[str] = operations

    def evaluate_expression(self) -> Union[int, str, float, list]:
        ...


class Print(BaseType):
    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression_from = expression


class AssignField(BaseType):
    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class Else(BaseType):
    def __init__(self, name: str, body: Body):
        super().__init__(name)

        self.body = body


class When(BaseType):
    def __init__(self, name: str, expression: Expression, body: Body, else_: Optional[Else] = None):
        super().__init__(name)

        self.expression = expression
        self.body = body
        self.else_ = else_


class Return(BaseType):
    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class Loop(BaseType):
    def __init__(self, name: str, expression_from: Expression, expression_to: Expression, body: Body):
        super().__init__(name)

        self.expression_from = expression_from
        self.expression_to = expression_to
        self.body = body
