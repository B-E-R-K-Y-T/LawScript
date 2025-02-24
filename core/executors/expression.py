from typing import Union, NamedTuple, Type, Optional, TYPE_CHECKING, Callable

from core.exceptions import ErrorType, InvalidExpression, BaseError, NameNotDefine, MaxRecursionError
from core.executors.base import Executor
from core.tokens import Tokens, ServiceTokens, ALL_TOKENS
from core.types.atomic import Void, Boolean
from core.types.basetype import BaseAtomicType
from core.types.operation import Operator
from core.types.procedure import Expression, Procedure
from core.types.variable import ScopeStack, traverse_scope, Variable

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled
    from core.executors.procedure import ProcedureExecutor


def _get_procedure_executor() -> Callable[..., "ProcedureExecutor"]:
    from core.executors.procedure import ProcedureExecutor
    return lambda *args, **kwargs: ProcedureExecutor(*args, **kwargs)


ALLOW_OPERATORS = {
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
    Tokens.bool_not_equal,
    Tokens.greater,
    Tokens.less,
    Tokens.exponentiation,
    ServiceTokens.unary_minus,
    ServiceTokens.unary_plus,
}


class Operands(NamedTuple):
    left: BaseAtomicType
    right: Optional[BaseAtomicType]
    atomic_type: Type[BaseAtomicType]


class ExpressionExecutor(Executor):
    def __init__(self, expression: Expression, tree_variable: ScopeStack, compiled: "Compiled"):
        self.expression = expression
        self.tree_variable = tree_variable
        self.compiled = compiled
        self.procedure_executor = _get_procedure_executor()

    def prepare_operations(self) -> list[Union[BaseAtomicType, Operator]]:
        new_expression_stack = []

        for operation in self.expression.operations:
            for variable in traverse_scope(self.tree_variable.scopes[-1]):
                if operation.name == variable.name:
                    new_expression_stack.append(variable.value)
                    break
            else:
                new_expression_stack.append(operation)

        for operation in new_expression_stack:
            if not isinstance(operation, BaseAtomicType) and not isinstance(operation, Procedure):
                if operation.name not in ALL_TOKENS:
                    raise NameNotDefine(
                        f"Имя переменной {operation.name} не определено."
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
        try:
            prepared_operations: list[Union[BaseAtomicType, Operator]] = self.prepare_operations()
        except BaseError as e:
            raise InvalidExpression(str(e), info=self.expression.meta_info)

        evaluate_stack: list[Union[BaseAtomicType, str]] = []

        for operation in prepared_operations:
            if isinstance(operation, Procedure):
                procedure = operation
                operand = evaluate_stack.pop(-1)

                procedure.tree_variables = ScopeStack()
                procedure.tree_variables.set(Variable(procedure.arguments_names[0], operand))

                executor = self.procedure_executor(procedure, self.compiled)

                try:
                    evaluate_stack.append(executor.execute())
                except RecursionError:
                    raise MaxRecursionError(
                        f"Вызов функции {procedure.name} завершился с ошибкой.",
                        info=self.expression.meta_info
                    )

                continue

            if operation.name not in ALLOW_OPERATORS:
                evaluate_stack.append(operation)
                continue

            if operation.operator == Tokens.minus:
                if len(evaluate_stack) == 1:
                    operand = evaluate_stack.pop(-1)
                    atomic_type = type(operand)

                    evaluate_stack.append(atomic_type(operand.neg()))
                    continue

                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.sub(operands.right)))

            elif operation.operator == Tokens.plus:
                if len(evaluate_stack) == 1:
                    operand = evaluate_stack.pop(-1)
                    atomic_type = type(operand)

                    evaluate_stack.append(atomic_type(operand.pos()))
                    continue

                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.add(operands.right)))

            elif operation.operator == ServiceTokens.unary_minus:
                operand = evaluate_stack.pop(-1)
                atomic_type = type(operand)

                evaluate_stack.append(atomic_type(operand.neg()))

            elif operation.operator == ServiceTokens.unary_plus:
                operand = evaluate_stack.pop(-1)
                atomic_type = type(operand)

                evaluate_stack.append(atomic_type(operand.pos()))

            elif operation.operator == Tokens.star:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.mul(operands.right)))

            elif operation.operator == Tokens.div:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.div(operands.right)))

            elif operation.operator == Tokens.exponentiation:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(operands.atomic_type(operands.left.pow(operands.right)))

            elif operation.operator == Tokens.and_:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.and_(operands.right)))

            elif operation.operator == Tokens.or_:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.or_(operands.right)))

            elif operation.operator == Tokens.not_:
                operand: BaseAtomicType = evaluate_stack.pop(-1)
                evaluate_stack.append(Boolean(operand.not_()))

            elif operation.operator == Tokens.bool_equal:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.eq(operands.right)))

            elif operation.operator == Tokens.bool_not_equal:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.ne(operands.right)))

            elif operation.operator == Tokens.greater:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.gt(operands.right)))

            elif operation.operator == Tokens.less:
                operands = self.get_operands(evaluate_stack)
                evaluate_stack.append(Boolean(operands.left.lt(operands.right)))

            else:
                raise ErrorType(
                    f"Операция '{operation}' не поддерживается!",
                    info=self.expression.meta_info
                )

        if len(evaluate_stack) > 1:
            raise ErrorType(
                f"Некорректное выражение: '{self.expression.meta_info.raw_line}'!",
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
