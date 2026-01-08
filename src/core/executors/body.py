from typing import TYPE_CHECKING, Union, Generator, Final

from src.core.exceptions import (
    ErrorType,
    NameNotDefine,
    BaseError,
    create_law_script_exception_class_instance,
    InvalidExceptionType,
    is_def_err,
)
from src.core.executors.expression import ExpressionExecutor
from src.core.tokens import Tokens
from src.core.types.atomic import Number, YIELD
from src.core.types.base_declarative_type import BaseDeclarativeType
from src.core.types.basetype import BaseAtomicType
from src.core.types.classes import ClassDefinition, ClassField, ClassExceptionDefinition, ClassInstance
from src.core.types.procedure import (
    Print,
    Return,
    AssignField,
    Body,
    When,
    Loop,
    Expression,
    Procedure,
    Continue,
    Break,
    AssignOverrideVariable,
    While,
    Context,
    BlockSync,
    ErrorThrow
)
from src.core.executors.base import Executor
from src.core.types.variable import Variable, ScopeStack, VariableContextCreator, traverse_scope
from src.util.console_worker import printer
from src.core.extend.function_wrap import PyExtendWrapper

if TYPE_CHECKING:
    from src.util.build_tools.compile import Compiled


class Stop: ...


STOP: Final[Stop] = Stop()


class BodyExecutor(Executor):
    def __init__(self, body: Body, tree_variables: ScopeStack, compiled: "Compiled"):
        self.body = body
        self.tree_variables = tree_variables
        self.compiled = compiled
        self.catch_comprehensive_procedures()
        self.async_mode = False

    def catch_comprehensive_procedures(self):
        local_vars_names = {lv.name for lv in traverse_scope(self.tree_variables.scopes[-1])}

        for name, var in self.compiled.compiled_code.items():
            if name in local_vars_names:
                continue

            if isinstance(var, Procedure):
                self.tree_variables.set(Variable(var.name, var))
            elif isinstance(var, PyExtendWrapper):
                self.tree_variables.set(Variable(var.name, var))
            elif isinstance(var, ClassDefinition):
                self.tree_variables.set(Variable(var.name, var))
            elif isinstance(var, BaseDeclarativeType):
                self.tree_variables.set(Variable(var.name, var))

    def execute(self) -> Union[Generator, Union[BaseAtomicType, Continue, Break]]:
        gen = self._execute()

        try:
            while True:
                next(gen)
        except StopIteration as exc:
            return exc.value

    def async_execute(self):
        self.async_mode = True

        return self._execute()

    def _execute(self) -> Union[Generator, Union[BaseAtomicType, Continue, Break]]:
        for command in self.body.commands:
            if isinstance(command, Expression):
                executor = ExpressionExecutor(command, self.tree_variables, self.compiled)

                if self.async_mode:
                    yield from executor.execute(self.async_mode)
                else:
                    executor.execute_with_atomic_type()

            elif isinstance(command, AssignOverrideVariable):
                target_expr_executor = ExpressionExecutor(command.target_expr, self.tree_variables, self.compiled)
                override_expr_executor = ExpressionExecutor(command.override_expr, self.tree_variables, self.compiled)

                if self.async_mode:
                    override_expr_result = yield from override_expr_executor.execute(self.async_mode)
                else:
                    override_expr_result = override_expr_executor.execute_with_atomic_type()

                if len(command.target_expr.operations) == 1:
                    target_name = command.target_expr.operations[0].name

                    try:
                        var = self.tree_variables.get(target_name)
                    except NameNotDefine as e:
                        raise NameNotDefine(str(e), info=command.meta_info)

                    # Странный код, не помню, зачем он тут. Если его закомментировать, тесты не падают, но пока оставлю
                    # override_expr_result.name = target_name
                    var.set_value(override_expr_result)

                    continue

                if self.async_mode:
                    target = yield from target_expr_executor.execute(self.async_mode)
                else:
                    target = target_expr_executor.execute()

                if isinstance(target, ClassField):
                    target.value = override_expr_result
                    continue

                try:
                    var = self.tree_variables.get(target.name)
                except NameNotDefine as e:
                    raise NameNotDefine(str(e), info=command.meta_info)

                var.set_value(override_expr_result)

            elif isinstance(command, AssignField):
                if command.name in self.tree_variables.scopes[-1].variables:
                    raise ErrorType(f"Переменная '{command.name}' уже определена!", info=command.meta_info)

                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)

                if self.async_mode:
                    executed = yield from executor.async_execute(as_atomic=True)
                else:
                    executed = executor.execute_with_atomic_type()

                var = Variable(command.name, executed)

                self.tree_variables.set(var)

            elif isinstance(command, Print):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)
                if self.async_mode:
                    executed = yield from executor.async_execute(as_atomic=True)
                else:
                    executed = executor.execute_with_atomic_type()

                printer.raw_print(executed)

            elif isinstance(command, When):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)
                if self.async_mode:
                    result = yield from executor.async_execute(as_atomic=True)
                else:
                    result = executor.execute_with_atomic_type()

                with VariableContextCreator(self.tree_variables):
                    if result.value:
                        body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)
                        if self.async_mode:
                            executed = yield from body_executor.async_execute()
                        else:
                            executed = body_executor.execute()

                        if not isinstance(executed, Stop):
                            return executed
                    else:
                        for else_when in command.else_whens:
                            when_executor = ExpressionExecutor(else_when.expression, self.tree_variables, self.compiled)
                            if self.async_mode:
                                result = yield from when_executor.async_execute(as_atomic=True)
                            else:
                                result = when_executor.execute_with_atomic_type()

                            if result.value:
                                body_executor = BodyExecutor(else_when.body, self.tree_variables, self.compiled)

                                if self.async_mode:
                                    executed = yield from body_executor.async_execute()
                                else:
                                    executed = body_executor.execute()

                                if not isinstance(executed, Stop):
                                    return executed

                                break

                        else:
                            if command.else_ is not None:
                                body_executor = BodyExecutor(command.else_.body, self.tree_variables, self.compiled)
                                if self.async_mode:
                                    executed = yield from body_executor.async_execute()
                                else:
                                    executed = body_executor.execute()

                                if not isinstance(executed, Stop):
                                    return executed

            elif isinstance(command, While):
                body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)

                with VariableContextCreator(self.tree_variables):
                    while True:
                        if self.async_mode:
                            result = yield from executor.async_execute(as_atomic=True)
                        else:
                            result = executor.execute_with_atomic_type()

                        if self.async_mode:
                            yield YIELD

                        if not result.value:
                            break

                        if self.async_mode:
                            executed = yield from body_executor.async_execute()
                        else:
                            executed = body_executor.execute()

                        if isinstance(executed, Continue):
                            continue

                        elif isinstance(executed, Break):
                            break

                        elif not isinstance(executed, Stop):
                            return executed

            elif isinstance(command, Loop):
                executor_from = ExpressionExecutor(command.expression_from, self.tree_variables, self.compiled)
                executor_to = ExpressionExecutor(command.expression_to, self.tree_variables, self.compiled)

                if self.async_mode:
                    result_from = yield from executor_from.async_execute(as_atomic=True)
                else:
                    result_from = executor_from.execute_with_atomic_type()

                if self.async_mode:
                    result_to = yield from executor_to.async_execute(as_atomic=True)
                else:
                    result_to = executor_to.execute_with_atomic_type()

                if not isinstance(result_from, Number) or not isinstance(result_to, Number):
                    raise ErrorType(
                        f"В цикле в блоках '{Tokens.from_}' и '{Tokens.to}' должны быть числа!",
                        info=command.meta_info
                    )

                with VariableContextCreator(self.tree_variables):
                    body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)

                    for var in range(result_from.value, result_to.value + 1):
                        if self.async_mode:
                            yield YIELD

                        if command.name_loop_var is not None:
                            self.tree_variables.set(Variable(command.name_loop_var, Number(var)))

                        if self.async_mode:
                            executed = yield from body_executor.async_execute()
                        else:
                            executed = body_executor.execute()

                        if isinstance(executed, Continue):
                            continue

                        elif isinstance(executed, Break):
                            break

                        elif not isinstance(executed, Stop):
                            return executed

            elif isinstance(command, Continue):
                if self.async_mode:
                    yield YIELD

                return command

            elif isinstance(command, Break):
                if self.async_mode:
                    yield YIELD

                return command

            elif isinstance(command, ErrorThrow):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)
                if self.async_mode:
                    executed = yield from executor.async_execute(as_atomic=True)
                else:
                    executed = executor.execute_with_atomic_type()

                if isinstance(executed, ClassExceptionDefinition):
                    raise executed.base_ex(info=executor.expression.meta_info)
                elif isinstance(executed, ClassInstance):
                    if not is_def_err(executed.metadata.parent):
                        raise InvalidExceptionType(type_ex=executed)

                    info = executed.fields.get(executed.metadata.info_attr_name)

                    raise executed.metadata.base_ex(
                        info,
                        info=executor.expression.meta_info,
                    )
                else:
                    raise InvalidExceptionType(type_ex=executed, info=executor.expression.meta_info)

            elif isinstance(command, Context):
                with VariableContextCreator(self.tree_variables):
                    body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)
                    try:
                        if self.async_mode:
                            executed = yield from body_executor.async_execute()
                        else:
                            executed = body_executor.execute()

                        if not isinstance(executed, Stop):
                            return executed
                    except BaseError as e:
                        for handler in command.handlers:
                            exception = self.compiled.compiled_code.get(handler.exception_class_name)

                            if exception is None:
                                continue

                            if not isinstance(exception, ClassExceptionDefinition):
                                continue

                            if not isinstance(e, exception.base_ex):
                                continue

                            if handler.exception_class_name == e.exc_name:
                                ex_inst = create_law_script_exception_class_instance(handler.exception_class_name, e)
                            else:
                                ex_inst = exception.create_instance(e)

                            self.tree_variables.set(Variable(handler.exception_inst_name, ex_inst))

                            body_executor = BodyExecutor(handler.body, self.tree_variables, self.compiled)
                            if self.async_mode:
                                executed = yield from body_executor.async_execute()

                                if not isinstance(executed, Stop):
                                    return executed
                            else:
                                executed = body_executor.execute()

                                if not isinstance(executed, Stop):
                                    return executed

                            break
                        else:
                            raise

            elif isinstance(command, Return):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)

                if self.async_mode:
                    executed = yield from executor.async_execute(as_atomic=True)
                else:
                    executed = executor.execute_with_atomic_type()

                return executed

            elif isinstance(command, BlockSync):
                body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)

                while command.is_blocked:
                    if self.async_mode:
                        yield YIELD

                with command.lock:
                    command.is_blocked = True

                try:
                    if self.async_mode:
                        executed = yield from body_executor.async_execute()
                    else:
                        executed = body_executor.execute()
                finally:
                    with command.lock:
                        command.is_blocked = False

                if not isinstance(executed, Stop):
                    return executed

            else:
                raise ErrorType(f"Неизвестная команда '{command.name}'!", info=command.meta_info)

            if self.async_mode:
                yield YIELD

        return STOP
