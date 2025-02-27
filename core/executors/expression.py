from typing import Union, NamedTuple, Type, Optional, TYPE_CHECKING, Callable

from core.call_func_stack import call_func_stack_builder
from core.exceptions import (
    ErrorType,
    InvalidExpression,
    BaseError,
    NameNotDefine,
    MaxRecursionError,
    DivisionByZeroError
)
from core.executors.base import Executor
from core.tokens import Tokens, ServiceTokens, ALL_TOKENS
from core.types.atomic import Void, Boolean
from core.types.basetype import BaseAtomicType, BaseType
from core.types.operation import Operator
from core.types.procedure import Expression, Procedure
from core.types.variable import ScopeStack, traverse_scope, Variable
from core.extend.function_wrap import PyExtendWrapper

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
            if (
                    not isinstance(operation, BaseAtomicType)
                    and
                    not isinstance(operation, Procedure)
                    and
                    not isinstance(operation, PyExtendWrapper)
            ):
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

    def call_procedure_evaluate(self, procedure: Procedure, evaluate_stack: list[Union[BaseAtomicType, Procedure]]):
        if not evaluate_stack:
            evaluate_stack.append(procedure)
            return

        call_func_stack_builder.push(func_name=procedure.name, meta_info=self.expression.meta_info)
        operand: Union[BaseAtomicType, Operator] = evaluate_stack.pop(-1)

        procedure.tree_variables = ScopeStack()

        if not isinstance(operand, Operator):
            if not procedure.arguments_names:
                raise InvalidExpression(
                    f"Функция {procedure.name} не принимает аргументов.",
                    info=self.expression.meta_info
                )

            procedure.tree_variables.set(Variable(procedure.arguments_names[0], operand))

        if procedure.arguments_names and isinstance(operand, Operator):
            raise InvalidExpression(
                f"Функция {procedure.name} принимает '{len(procedure.arguments_names)}' аргумента(ов)",
                info=self.expression.meta_info
            )

        executor = self.procedure_executor(procedure, self.compiled)

        try:
            evaluate_stack.append(executor.execute())
        except RecursionError:
            raise MaxRecursionError(
                f"Вызов функции {procedure.name} завершился с ошибкой.",
                info=self.expression.meta_info
            )

        call_func_stack_builder.pop()

    def call_py_extend_procedure_evaluate(
            self, py_extend_procedure: PyExtendWrapper, evaluate_stack: list[Union[BaseAtomicType, PyExtendWrapper]]
    ):
        if not evaluate_stack:
            evaluate_stack.append(py_extend_procedure)
            return

        call_func_stack_builder.push(func_name=py_extend_procedure.name, meta_info=self.expression.meta_info)
        operand = evaluate_stack.pop(-1)

        if isinstance(operand, Operator) and operand.operator == ServiceTokens.void_arg:
            args = None
        else:
            args = [operand]

        try:
            py_extend_procedure.check_args(args)
            result = py_extend_procedure.call(args)
        except BaseError as e:
            raise InvalidExpression(str(e), info=self.expression.meta_info)

        if not isinstance(result, BaseAtomicType):
            raise ErrorType(
                f"Вызов функции {py_extend_procedure.name} завершился с ошибкой. Не верный возвращаемый тип.",
                info=self.expression.meta_info
            )

        evaluate_stack.append(result)
        call_func_stack_builder.pop()

    def evaluate(self) -> BaseAtomicType:
        try:
            prepared_operations: list[Union[BaseAtomicType, Operator]] = self.prepare_operations()
        except BaseError as e:
            raise InvalidExpression(str(e), info=self.expression.meta_info)

        evaluate_stack: list[Union[BaseAtomicType, BaseType]] = []

        for operation in prepared_operations:
            if isinstance(operation, Procedure):
                self.call_procedure_evaluate(operation, evaluate_stack)
                continue

            elif isinstance(operation, PyExtendWrapper):
                self.call_py_extend_procedure_evaluate(operation, evaluate_stack)
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
        except TypeError:
            raise ErrorType(
                f"Ошибка выполнения операции между операндами в выражении '{self.expression.meta_info.raw_line}'!",
                info=self.expression.meta_info
            )
        except ZeroDivisionError:
            raise DivisionByZeroError(
                f"Деление на ноль в выражении '{self.expression.meta_info.raw_line}'!",
                info=self.expression.meta_info
            )
        except Exception:
            raise InvalidExpression(
                f"Некорректное выражение: '{self.expression.meta_info.raw_line}'!",
                info=self.expression.meta_info
            )
