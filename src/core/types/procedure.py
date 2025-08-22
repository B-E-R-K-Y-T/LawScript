from typing import Optional, Union

from src.core.extend.function_wrap import PyExtendWrapper
from src.core.types.basetype import BaseType, BaseAtomicType
from src.core.types.code_block import CodeBlock, Body
from src.core.types.line import Info
from src.core.types.operation import Operator
from src.core.types.variable import ScopeStack


class Procedure(CodeBlock):
    __slots__ = ('arguments_names', 'default_arguments', 'tree_variables')

    def __init__(
            self, name: str, body: Body,
            arguments_names: list[Optional[str]], default_arguments: Optional[dict[str, 'Expression']] = None
    ):
        super().__init__(name, body)

        self.arguments_names = arguments_names
        self.default_arguments = default_arguments
        self.tree_variables: Optional[ScopeStack] = None

    def __str__(self):
        return f"Процедура('{self.name}') кол-во аргументов: {len(self.arguments_names)}"

    def __repr__(self):
        return self.name


class LinkedProcedure(BaseType):
    __slots__ = ('func',)

    def __init__(self, name: str, func: Union[Procedure, PyExtendWrapper]):
        super().__init__(name)
        self.func = func

    def __str__(self):
        return str(self.func)

    def __repr__(self):
        return repr(self.func)


class ProcedureContextName(BaseType):
    def __init__(self, operator: Operator):
        super().__init__(operator.name)
        self.operator = operator
        self.func: Optional[Procedure] = None


class Expression(BaseType):
    __slots__ = ('meta_info', 'operations', 'raw_operations')

    def __init__(self, name: str, operations, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line
        self.operations: Optional[list[Union[Operator, BaseAtomicType]]] = None
        self.raw_operations = operations


class AssignOverrideVariable(BaseType):
    __slots__ = ('meta_info', 'operations', 'raw_operations')

    def __init__(self, name: str, target_expr: Expression, override_expr: Expression, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line
        self.target_expr = target_expr
        self.override_expr = override_expr


class Continue(BaseType):
    __slots__ = ('meta_info',)

    def __init__(self, name: str, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line


class Break(BaseType):
    __slots__ = ('meta_info',)

    def __init__(self, name: str, info_line: Info):
        super().__init__(name)
        self.meta_info = info_line


class Print(BaseType):
    __slots__ = ('expression',)

    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class AssignField(BaseType):
    __slots__ = ('meta_info', 'expression')

    def __init__(self, name: str, expression: Expression, info_line: Info):
        super().__init__(name)

        self.meta_info = info_line
        self.expression = expression


class Else(CodeBlock):
    __slots__ = ()

    def __init__(self, name: str, body: Body):
        super().__init__(name, body)


class ElseWhen(CodeBlock):
    __slots__ = ('expression',)

    def __init__(self, name: str, expression: Expression, body: Body):
        super().__init__(name, body)

        self.expression = expression


class When(CodeBlock):
    __slots__ = ('expression', 'else_whens', 'else_')

    def __init__(
            self, name: str, expression: Expression, body: Body,
            else_: Optional[Else] = None, else_whens: Optional[list[ElseWhen]] = None
    ):
        super().__init__(name, body)

        self.expression = expression
        self.else_whens = else_whens
        self.else_ = else_


class Return(BaseType):
    __slots__ = ('expression',)

    def __init__(self, name: str, expression: Expression):
        super().__init__(name)

        self.expression = expression


class Loop(CodeBlock):
    __slots__ = ('expression_from', 'expression_to', 'name_loop_var')

    def __init__(self, name: str, expression_from: Expression, expression_to: Expression, body: Body):
        super().__init__(name, body)

        self.expression_from = expression_from
        self.expression_to = expression_to
        self.name_loop_var = None


class While(CodeBlock):
    __slots__ = ('expression',)

    def __init__(self, name: str, expression: Expression, body: Body):
        super().__init__(name, body)
        self.expression = expression


class Context(CodeBlock):
    def __init__(self, name: str, body: Body):
        super().__init__(name, body)
        self.handlers: list[ExceptionHandler] = []


class ExceptionHandler(CodeBlock):
    def __init__(self, name: str, body: Body):
        super().__init__(name, body)
        self.exception_inst_name: str = ""
        self.exception_class_name: str = ""
