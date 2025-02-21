from typing import Union, NamedTuple, Type

from core.exceptions import ErrorType
from core.executors.base import Executor
from core.tokens import Tokens
from core.types.atomic import Void
from core.types.basetype import BaseAtomicType
from core.types.procedure import Expression
from core.types.variable import ScopeStack, Variable


class Operands(NamedTuple):
    left: Union[BaseAtomicType, str]
    right: Union[BaseAtomicType, str]
    atomic_type: Type[BaseAtomicType]


class ExpressionExecutor(Executor):
    def __init__(self, expression: Expression, tree_variable: ScopeStack):
        self.expression = expression
        self.tree_variable = tree_variable

    def prepare_operations(self) -> list[Union[BaseAtomicType, str]]:
        new_expression_stack = []

        for operation in self.expression.operations:
            if operation in self.tree_variable.scopes[-1].variables:
                variable: Variable[BaseAtomicType] = self.tree_variable.scopes[-1].variables[operation]
                new_expression_stack.append(variable.value)

                continue

            new_expression_stack.append(operation)

        return new_expression_stack

    @staticmethod
    def get_operands(execute_stack: list) -> Operands:
        l, r = execute_stack.pop(-2), execute_stack.pop(-1)

        type_l = type(l)
        type_r = type(r)
        atomic_type = type_l

        if type_l != type_r:
            raise ErrorType(
                f"Операнды '{l}'({type_l.type_name()}) и '{r}'({type_r.type_name()}) должны быть одного типа!"
            )

        return Operands(
            left=l,
            right=r,
            atomic_type=atomic_type,
        )

    def execute(self) -> BaseAtomicType:
        prepared_operations: list[Union[BaseAtomicType, str]] = self.prepare_operations()
        execute_stack: list[Union[BaseAtomicType, str]] = []
        allow_operators = (
            Tokens.star,
            Tokens.div,
            Tokens.plus,
            Tokens.minus,
        )

        for operation in prepared_operations:
            if operation not in allow_operators:
                execute_stack.append(operation)
                continue

            if operation == Tokens.minus:
                operands = self.get_operands(execute_stack)
                execute_stack.append(operands.atomic_type(operands.left.sub(operands.right)))

            if operation == Tokens.plus:
                operands = self.get_operands(execute_stack)
                execute_stack.append(operands.atomic_type(operands.left.add(operands.right)))

            if operation == Tokens.star:
                operands = self.get_operands(execute_stack)
                execute_stack.append(operands.atomic_type(operands.left.mul(operands.right)))

            if operation == Tokens.div:
                operands = self.get_operands(execute_stack)
                execute_stack.append(operands.atomic_type(operands.left.div(operands.right)))

        if execute_stack:
            return execute_stack[0]

        return Void()
