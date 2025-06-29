from typing import Union, NamedTuple, Type, Optional, TYPE_CHECKING, Callable

from core.background_task.schedule import get_task_scheduler
from core.background_task.task import ProcedureBackgroundTask, AbstractBackgroundTask
from core.call_func_stack import call_func_stack_builder
from core.exceptions import (
    ErrorType,
    InvalidExpression,
    BaseError,
    NameNotDefine,
    MaxRecursionError,
    DivisionByZeroError,
    ErrorOverflow
)
from core.executors.base import Executor
from core.tokens import Tokens, ServiceTokens, ALL_TOKENS
from core.types.atomic import Void, Boolean, Yield
from core.types.basetype import BaseAtomicType, BaseType
from core.types.classes import ClassDefinition, ClassInstance, Method, ClassField
from core.types.operation import Operator
from core.types.procedure import Expression, Procedure, LinkedProcedure
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
    Tokens.wait,
    Tokens.attr_access,
    ServiceTokens.unary_minus,
    ServiceTokens.unary_plus,
    ServiceTokens.in_background
}

VALID_TYPES = (
    BaseAtomicType,
    Procedure,
    PyExtendWrapper,
    LinkedProcedure,
    AbstractBackgroundTask,
    ClassDefinition,
    ClassInstance,
    ClassField,
)


class Operands(NamedTuple):
    left: BaseAtomicType
    right: Optional[BaseAtomicType]
    atomic_type: Type[BaseAtomicType]


class ProcedureWrapper(NamedTuple):
    procedure: Optional[Union[Procedure, PyExtendWrapper]] = None
    args: Optional[list[BaseAtomicType]] = None


class ExpressionExecutor(Executor):
    def __init__(self, expression: Expression, tree_variable: ScopeStack, compiled: "Compiled"):
        self.expression = expression
        self.tree_variable = tree_variable
        self.compiled = compiled
        self.procedure_executor = _get_procedure_executor()
        self.task_scheduler = get_task_scheduler()

    def prepare_operations(self) -> list[Union[BaseAtomicType, Operator]]:
        scope_vars = {var.name: var.value for var in traverse_scope(self.tree_variable.scopes[-1])}
        new_expression_stack = []

        for offset, operation in enumerate(self.expression.operations):
            if operation.name in scope_vars:
                if isinstance(operation, LinkedProcedure):
                    new_expression_stack.append(operation)
                elif isinstance(scope_vars[operation.name], AbstractBackgroundTask):
                    scope_vars[operation.name].name = operation.name
                    new_expression_stack.append(scope_vars[operation.name])
                else:
                    new_expression_stack.append(scope_vars[operation.name])
            else:
                new_expression_stack.append(operation)

        for offset, operation in enumerate(new_expression_stack):
            if not isinstance(operation, VALID_TYPES) and operation.name not in ALL_TOKENS:
                # for step in range(1, 3):
                next_operation = new_expression_stack[offset + 1] if offset + 1 < len(new_expression_stack) else None

                if next_operation is not None and isinstance(next_operation, Operator):
                    if next_operation.operator == Tokens.attr_access:
                        field = ClassField()
                        field.name = operation.name
                        new_expression_stack[offset] = field
                        break
                # else:
                raise NameNotDefine(name=operation.name, scopes=self.tree_variable.scopes)


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

    def init_procedure_context(self, procedure: Procedure, evaluate_stack: list[Union[BaseAtomicType, Procedure]]):
        if not evaluate_stack:
            evaluate_stack.append(procedure)
            return ProcedureWrapper()

        procedure.tree_variables = ScopeStack()

        rev_arguments_names = list(reversed(procedure.arguments_names))
        arg_position = 0
        count_args = 0

        while True:
            if not evaluate_stack:
                break

            operand: Union[BaseAtomicType, Operator] = evaluate_stack.pop(-1)

            if isinstance(operand, Operator):
                if operand.operator == ServiceTokens.arg_separator:
                    break

                if operand.operator == ServiceTokens.void_arg:
                    break

            if evaluate_stack:
                if isinstance(evaluate_stack[-1], Operator):
                    if evaluate_stack[-1].operator == Tokens.comma:
                        evaluate_stack.pop(-1)

            count_args += 1

            if not isinstance(operand, Operator):
                if rev_arguments_names and arg_position < len(rev_arguments_names):
                    argument = rev_arguments_names[arg_position]
                    operand.name = argument
                    procedure.tree_variables.set(Variable(argument, operand))
                    arg_position += 1

                if not procedure.arguments_names:
                    raise InvalidExpression(
                        f"Функция {procedure.name} не принимает аргументов.",
                        info=self.expression.meta_info
                    )

        if procedure.default_arguments is not None:
            procedure_variables = procedure.tree_variables.scopes[0].variables

            new_procedure_variables = {}

            for arg_name, (default_name, default_arg) in zip(procedure.arguments_names, reversed(procedure_variables.items())):
                default_arg.name = arg_name
                new_procedure_variables[arg_name] = default_arg

            procedure.tree_variables.scopes[0].variables.update(new_procedure_variables)

            fact_default_args_count = 0

            for arg_num, (name, expr) in enumerate(reversed(procedure.default_arguments.items())):
                if arg_num + 1 > len(procedure.arguments_names) - count_args:
                    break

                fact_default_args_count += 1

                value = ExpressionExecutor(expr, self.tree_variable, self.compiled).execute()

                procedure.tree_variables.set(Variable(name, value))

            count_args += fact_default_args_count

        if count_args != len(procedure.arguments_names):
            raise InvalidExpression(
                f"Функция {procedure.name} принимает '{len(procedure.arguments_names)}' "
                f"аргумента(ов), но передано: '{count_args}'",
                info=self.expression.meta_info
            )

        return ProcedureWrapper(
            procedure=procedure,
        )

    def call_procedure(self, procedure: Procedure, evaluate_stack: list[Union[BaseAtomicType, Procedure]]):
        executor = self.procedure_executor(procedure, self.compiled)
        evaluate_stack.append(executor.execute())

    def call_method(self, method: Procedure, evaluate_stack: list[Union[BaseAtomicType, Procedure]], this: Variable):
        method.tree_variables.set(this)
        self.call_procedure(method, evaluate_stack)

    def call_constructor(
            self, method: Procedure, evaluate_stack: list[Union[BaseAtomicType, Procedure]],
            this: Variable, instance: ClassInstance
    ):
        self.call_method(method, evaluate_stack, this)
        evaluate_stack.pop(-1)
        instance.this = instance

        evaluate_stack.append(instance)

    @staticmethod
    def init_py_extend_procedure_context(
            py_extend_procedure: PyExtendWrapper, evaluate_stack: list[Union[BaseAtomicType, PyExtendWrapper]]
    ) -> ProcedureWrapper:
        if not evaluate_stack:
            evaluate_stack.append(py_extend_procedure)
            return ProcedureWrapper()

        args = None

        while True:
            if not evaluate_stack:
                break

            operand = evaluate_stack.pop(-1)

            if isinstance(operand, Operator):
                if operand.operator == ServiceTokens.arg_separator:
                    break

            if evaluate_stack:
                if isinstance(evaluate_stack[-1], Operator):
                    if evaluate_stack[-1].operator == Tokens.comma:
                        evaluate_stack.pop(-1)

            if isinstance(operand, Operator) and operand.operator == ServiceTokens.void_arg:
                args = None
                break
            else:
                if args is None:
                    args = []

                args.append(operand)

        if args is not None:
            args = list(reversed(args))

        return ProcedureWrapper(
            procedure=py_extend_procedure,
            args=args
        )

    def call_py_extend_procedure(self, py_extend_procedure, args, evaluate_stack: list[Union[BaseAtomicType, PyExtendWrapper]]):
        try:
            py_extend_procedure.check_args(args)
            result = py_extend_procedure.call(args)
        except BaseError as e:
            raise InvalidExpression(str(e), info=self.expression.meta_info)

        if not isinstance(result, BaseAtomicType):
            raise ErrorType(
                f"Вызов процедуры '{py_extend_procedure.name}' завершился с ошибкой. Не верный возвращаемый тип.",
                info=self.expression.meta_info
            )

        evaluate_stack.append(result)

    def evaluate(self) -> BaseAtomicType:
        try:
            prepared_operations: list[Union[BaseAtomicType, Operator]] = self.prepare_operations()
        except BaseError as e:
            raise InvalidExpression(str(e), info=self.expression.meta_info)

        evaluate_stack: list[Union[AbstractBackgroundTask, BaseAtomicType, BaseType]] = []

        for offset, operation in enumerate(prepared_operations):
            if isinstance(operation, Operator) and operation.operator == Tokens.attr_access:
                operands = self.get_operands(evaluate_stack)
                res = operands.left.get_attribute(operands.right.name)

                if isinstance(res, Method):
                    operation = res
                else:
                    evaluate_stack.append(res)
                    continue

            if isinstance(operation, LinkedProcedure):
                operation.func.name = operation.name
                evaluate_stack.append(operation.func)
                continue

            if isinstance(operation, Procedure):
                if offset + 1 < len(prepared_operations):
                    next_op = prepared_operations[offset + 1]

                    if isinstance(next_op, Operator):
                        if prepared_operations[offset + 1].operator == ServiceTokens.in_background:
                            evaluate_stack.append(operation)
                            continue

                try:
                    call_metadata = self.init_procedure_context(operation, evaluate_stack)

                    if call_metadata.procedure is not None:
                        call_func_stack_builder.push(func_name=operation.name, meta_info=self.expression.meta_info)
                        self.call_procedure(call_metadata.procedure, evaluate_stack)
                        call_func_stack_builder.pop()
                except RecursionError:
                    raise MaxRecursionError(
                        f"Вызов процедуры '{operation.name}' завершился с ошибкой. Циклический вызов.",
                        info=self.expression.meta_info
                    )

                continue

            elif isinstance(operation, PyExtendWrapper):
                if offset + 1 < len(prepared_operations):
                    next_op = prepared_operations[offset + 1]

                    if isinstance(next_op, Operator):
                        if prepared_operations[offset + 1].operator == ServiceTokens.in_background:
                            evaluate_stack.append(operation)
                            continue

                call_metadata = self.init_py_extend_procedure_context(operation, evaluate_stack)

                if call_metadata.procedure is not None:
                    call_func_stack_builder.push(func_name=operation.name, meta_info=self.expression.meta_info)
                    self.call_py_extend_procedure(call_metadata.procedure, call_metadata.args, evaluate_stack)
                    call_func_stack_builder.pop()

                continue

            elif isinstance(operation, ClassDefinition):
                try:
                    call_metadata = self.init_procedure_context(operation.constructor, evaluate_stack)

                    if call_metadata.procedure is not None:
                        call_func_stack_builder.push(func_name=operation.name, meta_info=self.expression.meta_info)
                        instance = operation.create_instance()
                        self.call_constructor(
                            call_metadata.procedure,
                            evaluate_stack,
                            Variable(operation.constructor.this, instance),
                            instance
                        )
                        call_func_stack_builder.pop()
                except RecursionError:
                    raise MaxRecursionError(
                        f"Вызов процедуры '{operation.name}' завершился с ошибкой. Циклический вызов.",
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

            elif operation.operator == Tokens.wait:
                task = evaluate_stack.pop(-1)

                if not isinstance(task, AbstractBackgroundTask):
                    raise ErrorType(
                        f"Операция '{Tokens.wait}' "
                        f"поддерживается только для задач!",
                        info=self.expression.meta_info
                    )

                while not task.done:
                    yield Yield()

                evaluate_stack.append(task.result)

            elif operation.operator == ServiceTokens.in_background:
                func = evaluate_stack.pop(-1)

                if isinstance(func, PyExtendWrapper):
                    call_metadata = self.init_py_extend_procedure_context(func, evaluate_stack)

                    if call_metadata.procedure is not None:
                        call_func_stack_builder.push(func_name=operation.name, meta_info=self.expression.meta_info)
                        self.call_py_extend_procedure(call_metadata.procedure, call_metadata.args, evaluate_stack)
                        call_func_stack_builder.pop()

                        background_task = evaluate_stack.pop(-1)

                        if not isinstance(background_task, AbstractBackgroundTask):
                            raise ErrorType(
                                f"Возвращаемое значение процедуры '{func.name}' должно быть задачей!",
                            )

                        self.task_scheduler.schedule_task(background_task)
                        evaluate_stack.append(background_task)

                    continue

                if not isinstance(func, Procedure):
                    if isinstance(func, Operator):
                        err_msg = (
                            f"Операция '{Tokens.in_} {Tokens.background}' "
                            f"не поддерживается для '{func.operator}'!"
                        )
                    else:
                        err_msg = (
                            f"Операция '{Tokens.in_} {Tokens.background}' "
                            f"не поддерживается для '{func}'!"
                        )

                    raise ErrorType(
                        err_msg,
                        info=self.expression.meta_info
                    )

                try:
                    call_metadata = self.init_procedure_context(func, evaluate_stack)

                    if call_metadata.procedure is not None:
                        executor = self.procedure_executor(call_metadata.procedure, self.compiled)
                        background_task = ProcedureBackgroundTask(call_metadata.procedure.name, executor)

                        self.task_scheduler.schedule_task(background_task)
                        evaluate_stack.append(background_task)

                except RecursionError:
                    raise MaxRecursionError(
                        f"Вызов процедуры '{operation.name}' завершился с ошибкой. Циклический вызов.",
                        info=self.expression.meta_info
                    )

                continue

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

    def execute(self, async_execute=False) -> BaseAtomicType:
        if async_execute:
            return self.async_execute()

        return self.sync_execute()

    def async_execute(self):
        gen = self.evaluate()

        while True:
            try:
                res = yield from gen

                if not isinstance(res, Yield):
                    return res
            except StopIteration as exc:
                return exc
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
            except OverflowError:
                raise ErrorOverflow(
                    f"Выражение вышло за пределы типа данных в выражении: '{self.expression.meta_info.raw_line}'!",
                    info=self.expression.meta_info
                )
            except Exception:
                raise InvalidExpression(
                    f"Некорректное выражение: '{self.expression.meta_info.raw_line}'!",
                    info=self.expression.meta_info
                )

    def sync_execute(self) -> BaseAtomicType:
        try:
            gen = self.evaluate()

            try:
                while True:
                    next(gen)
            except StopIteration as exc:
                return exc.value
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
        except OverflowError:
            raise ErrorOverflow(
                f"Выражение вышло за пределы типа данных в выражении: '{self.expression.meta_info.raw_line}'!",
                info=self.expression.meta_info
            )
        except Exception:
            raise InvalidExpression(
                f"Некорректное выражение: '{self.expression.meta_info.raw_line}'!",
                info=self.expression.meta_info
            )
