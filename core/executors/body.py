from typing import TYPE_CHECKING, Union

from core.exceptions import ErrorType, NameNotDefine
from core.executors.expression import ExpressionExecutor
from core.tokens import Tokens
from core.types.atomic import Void, Number
from core.types.basetype import BaseAtomicType
from core.types.procedure import Print, Return, AssignField, Body, When, Loop, Expression, Procedure, Continue, \
    CodeBlock, Break, AssignOverrideVariable
from core.executors.base import Executor
from core.types.variable import Variable, ScopeStack, VariableContextCreator, traverse_scope
from util.console_worker import printer
from core.extend.function_wrap import PyExtendWrapper

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled


class BodyExecutor(Executor):
    def __init__(self, body: Body, tree_variables: ScopeStack, compiled: "Compiled"):
        self.body = body
        self.tree_variables = tree_variables
        self.compiled = compiled
        self.catch_comprehensive_procedures()

    def catch_comprehensive_procedures(self):
        local_vars_names = {lv.name for lv in traverse_scope(self.tree_variables.scopes[-1])}

        for name, var in self.compiled.compiled_code.items():
            if name in local_vars_names:
                continue

            if isinstance(var, Procedure):
                self.tree_variables.set(Variable(var.name, var))
            elif isinstance(var, PyExtendWrapper):
                self.tree_variables.set(Variable(var.name, var))

    def execute(self) -> Union[BaseAtomicType, Continue, Break]:
        for command in self.body.commands:
            if isinstance(command, Return):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)

                return executor.execute()

            elif isinstance(command, AssignField):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)
                var = Variable(command.name, executor.execute())

                self.tree_variables.set(var)

            elif isinstance(command, Print):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)

                printer.raw_print(executor.execute())

            elif isinstance(command, When):
                executor = ExpressionExecutor(command.expression, self.tree_variables, self.compiled)
                result = executor.execute()

                with VariableContextCreator(self.tree_variables):
                    executed = Void()

                    if result.value:
                        body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)
                        executed = body_executor.execute()
                    elif command.else_ is not None:
                        body_executor = BodyExecutor(command.else_.body, self.tree_variables, self.compiled)
                        executed = body_executor.execute()

                    if not isinstance(executed, Void):
                        return executed

            elif isinstance(command, Loop):
                executor_from = ExpressionExecutor(command.expression_from, self.tree_variables, self.compiled)
                executor_to = ExpressionExecutor(command.expression_to, self.tree_variables, self.compiled)

                result_from = executor_from.execute()
                result_to = executor_to.execute()

                if not isinstance(result_from, Number) or not isinstance(result_to, Number):
                    raise ErrorType(
                        f"В цикле в блоках '{Tokens.from_}' и '{Tokens.to}' должны быть числа!",
                        info=command.meta_info
                    )

                with VariableContextCreator(self.tree_variables):
                    if not command.body.commands:
                        continue

                    body_executor = BodyExecutor(command.body, self.tree_variables, self.compiled)

                    for _ in range(result_from.value, result_to.value + 1):
                        executed = body_executor.execute()

                        if isinstance(executed, Continue):
                            continue

                        elif isinstance(executed, Break):
                            break

                        elif not isinstance(executed, Void):
                            return executed

            elif isinstance(command, Expression):
                executor = ExpressionExecutor(command, self.tree_variables, self.compiled)
                executor.execute()

            elif isinstance(command, AssignOverrideVariable):
                target_expr_executor = ExpressionExecutor(command.target_expr, self.tree_variables, self.compiled)
                override_expr_executor = ExpressionExecutor(command.override_expr, self.tree_variables, self.compiled)

                target_expr_execute = target_expr_executor.execute
                override_expr_result = override_expr_executor.execute()

                if len(command.target_expr.operations) == 1:
                    target_name = command.target_expr.operations[0].name

                    try:
                        var = self.tree_variables.get(target_name)
                    except NameNotDefine as e:
                        raise NameNotDefine(str(e), info=command.meta_info)

                    var.set_value(override_expr_result)

                    continue

                target = target_expr_execute()

                try:
                    var = self.tree_variables.get(target.name)
                except NameNotDefine as e:
                    raise NameNotDefine(str(e), info=command.meta_info)

                var.set_value(override_expr_result)

            elif isinstance(command, Continue):
                return command

            elif isinstance(command, Break):
                return command

            else:
                raise ErrorType(f"Неизвестная команда '{command.name}'!", info=command.meta_info)

        return Void()
