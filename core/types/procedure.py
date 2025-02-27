from typing import Optional, Union

from core.extend.function_wrap import PyExtendWrapper
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
        return f"Процедура('{self.name}') кол-во аргументов: {len(self.arguments_names)}"


class LinkedProcedure(BaseType):
    def __init__(self, name: str, func: Union[Procedure, PyExtendWrapper]):
        super().__init__(name)
        self.func = func


class Expression(BaseType):
    def __init__(self, name: str, operations, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line
        self.operations: Optional[list[Union[Operator, BaseAtomicType]]] = None
        self.raw_operations = operations



class AssignOverrideVariable(BaseType):
    def __init__(self, name: str, target_expr: Expression, override_expr: Expression, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line
        self.target_expr = target_expr
        self.override_expr = override_expr


class Continue(BaseType):
    def __init__(self, name: str, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line


class Break(BaseType):
    def __init__(self, name: str, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line


class Print(BaseType):
    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class AssignField(BaseType):
    def __init__(self, name: str, expression: Expression, info_line: Info):
        super().__init__(name)

        self.meta_info = info_line
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


class While(CodeBlock):
    def __init__(self, name: str, expression: Expression, body: Body):
        super().__init__(name, body)
        self.expression = expression
