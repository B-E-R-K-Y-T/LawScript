from typing import TYPE_CHECKING, Union, Generator

from core.exceptions import ErrorType, NameNotDefine, BaseError, EXCEPTIONS, create_law_script_exception_class_instance
from core.executors.expression import ExpressionExecutor
from core.tokens import Tokens
from core.types.atomic import Void, Number, Yield, String
from core.types.base_declarative_type import BaseDeclarativeType
from core.types.basetype import BaseAtomicType
from core.types.classes import ClassDefinition, ClassField
from core.types.procedure import (
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
    Context
)
from core.executors.base import Executor
from core.types.variable import Variable, ScopeStack, VariableContextCreator, traverse_scope
from util.console_worker import printer
from core.extend.function_wrap import PyExtendWrapper

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled


class Stop: ...


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
            if isinstance(command, Return):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)

                if self.async_mode:
                    executed = yield from executor.async_execute()
                else:
                    executed = executor.execute()

                return executed

            elif isinstance(command, AssignField):
                if command.name in self.tree_variables.scopes[-1].variables:
                    raise ErrorType(f"Переменная '{command.name}' уже определена!", info=command.meta_info)

                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)

                if self.async_mode:
                    executed = yield from executor.async_execute()
                else:
                    executed = executor.execute()

                var = Variable(command.name, executed)

                self.tree_variables.set(var)

            elif isinstance(command, Print):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)
                if self.async_mode:
                    executed = yield from executor.async_execute()
                else:
                    executed = executor.execute()

                printer.raw_print(executed)

            elif isinstance(command, When):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)
                if self.async_mode:
                    result = yield from executor.async_execute()
                else:
                    result = executor.execute()

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
                                result = yield from when_executor.async_execute()
                            else:
                                result = when_executor.execute()

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
                            result = yield from executor.async_execute()

                            if not result.value:
                                break

                        elif not executor.execute().value:
                            break

                        if self.async_mode:
                            yield Yield()

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
                    result_from = yield from executor_from.async_execute()
                else:
                    result_from = executor_from.execute()

                if self.async_mode:
                    result_to = yield from executor_to.async_execute()
                else:
                    result_to = executor_to.execute()

                if not isinstance(result_from, Number) or not isinstance(result_to, Number):
                    raise ErrorType(
                        f"В цикле в блоках '{Tokens.from_}' и '{Tokens.to}' должны быть числа!",
                        info=command.meta_info
                    )

                with VariableContextCreator(self.tree_variables):
                    body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)

                    for var in range(result_from.value, result_to.value + 1):
                        if self.async_mode:
                            yield Yield()

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

            elif isinstance(command, Expression):
                executor = ExpressionExecutor(command, self.tree_variables, self.compiled)

                if self.async_mode:
                    yield from executor.execute(self.async_mode)
                else:
                    executor.execute()

            elif isinstance(command, AssignOverrideVariable):
                target_expr_executor = ExpressionExecutor(command.target_expr, self.tree_variables, self.compiled)
                override_expr_executor = ExpressionExecutor(command.override_expr, self.tree_variables, self.compiled)

                if self.async_mode:
                    override_expr_result = yield from override_expr_executor.execute(self.async_mode)
                else:
                    override_expr_result = override_expr_executor.execute()

                if len(command.target_expr.operations) == 1:
                    target_name = command.target_expr.operations[0].name

                    try:
                        var = self.tree_variables.get(target_name)
                    except NameNotDefine as e:
                        raise NameNotDefine(str(e), info=command.meta_info)

                    override_expr_result.name = target_name
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

            elif isinstance(command, Continue):
                return command

            elif isinstance(command, Break):
                return command

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
                            if handler.exception_class_name != e.exc_name:
                                continue

                            ex_inst = create_law_script_exception_class_instance(handler.exception_class_name, e)

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

            else:
                raise ErrorType(f"Неизвестная команда '{command.name}'!", info=command.meta_info)

            if self.async_mode:
                yield Yield()

        return Stop()
