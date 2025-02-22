from typing import Union, NamedTuple, Type

from core.exceptions import ErrorType, InvalidExpression, BaseError, NameNotDefine
from core.executors.base import Executor
from core.tokens import Tokens
from core.types.atomic import Void, Boolean
from core.types.basetype import BaseAtomicType
from core.types.procedure import Expression
from core.types.variable import ScopeStack, Variable, traverse_scope

ALLOW_OPERATORS = (
    Tokens.left_bracket,
    Tokens.right_bracket,
    Tokens.star,
    Tokens.div,
    Tokens.plus,
    Tokens.minus,
    Tokens.and_,
    Tokens.or_,
    Tokens.not_,
    Tokens.bool_equal,
    Tokens.greater,
    Tokens.less,

)


class Operands(NamedTuple):
    left: BaseAtomicType
    right: BaseAtomicType
    atomic_type: Type[BaseAtomicType]


class ExpressionExecutor(Executor):
    def __init__(self, expression: Expression, tree_variable: ScopeStack):
        self.expression = expression
        self.tree_variable = tree_variable

    def prepare_operations(self) -> list[Union[BaseAtomicType, str]]:
        new_expression_stack = []

        for operation in self.expression.operations:
            for variable in traverse_scope(self.tree_variable.scopes[-1]):
                if operation == variable.name:
                    new_expression_stack.append(variable.value)
                    break
            else:
                new_expression_stack.append(operation)

        for operation in new_expression_stack:
            if not isinstance(operation, BaseAtomicType):
                if operation not in Tokens:
                    raise NameNotDefine(
                        f"Имя переменной {operation} не определено."
                    )

        return new_expression_stack

    @staticmethod
    def get_operands(execute_stack: list[BaseAtomicType]) -> Operands:
        l, r = execute_stack.pop(-2), execute_stack.pop(-1)
        atomic_type = type(l)

        return Operands(
            left=l,
            right=r,
            atomic_type=atomic_type,
        )

    def evaluate(self) -> BaseAtomicType:
        prepared_operations: list[Union[BaseAtomicType, str]] = self.prepare_operations()
        evaluate_stack: list[Union[BaseAtomicType, str]] = []

        for operation in prepared_operations:
            if operation not in ALLOW_OPERATORS:
                evaluate_stack.append(operation)
                continue

            if operation == Tokens.minus:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.sub(operands.right)))

            elif operation == Tokens.plus:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.add(operands.right)))

            elif operation == Tokens.star:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.mul(operands.right)))

            elif operation == Tokens.div:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.div(operands.right)))

            elif operation == Tokens.and_:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.and_(operands.right)))

            elif operation == Tokens.or_:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.or_(operands.right)))

            elif operation == Tokens.not_:
                operand: BaseAtomicType = evaluate_stack.pop(-1)
                evaluate_stack.append(Boolean(operand.not_()))

            elif operation == Tokens.bool_equal:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.eq(operands.right)))

            elif operation == Tokens.greater:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.gt(operands.right)))

            elif operation == Tokens.less:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.lt(operands.right)))

            else:
                raise ErrorType(
                    f"Операция '{operation}' не поддерживается!",
                    info=self.expression.meta_info
                )

        if evaluate_stack:
            return evaluate_stack[0]

        return Void()

    def execute(self) -> BaseAtomicType:
        try:
            return self.evaluate()
        except BaseError as e:
            raise e
        except TypeError as _:
            raise ErrorType(
                f"Ошибка выполнения операции между операндами в выражении '{self.expression.meta_info.raw_line}'!",
                info=self.expression.meta_info
            )
        except Exception as _:
            raise InvalidExpression(
                f"Некорректное выражение: '{self.expression.meta_info.raw_line}'!",
                info=self.expression.meta_info
            )
