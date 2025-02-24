from typing import TYPE_CHECKING

from core.exceptions import ErrorType
from core.executors.expression import ExpressionExecutor
from core.tokens import Tokens
from core.types.atomic import Void, Boolean, Number
from core.types.basetype import BaseAtomicType
from core.types.procedure import Print, Return, AssignField, Body, When, Loop
from core.executors.base import Executor
from core.types.variable import Variable, ScopeStack, VariableContextCreator
from util.console_worker import printer

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled


class BodyExecutor(Executor):
    def __init__(self, body: Body, tree_variables: ScopeStack, compiled: "Compiled"):
        self.body = body
        self.tree_variables = tree_variables
        self.compiled = compiled

    def execute(self) -> BaseAtomicType:
        for command in self.body.commands:
            if isinstance(command, Return):
                executor = ExpressionExecutor(command.expression, self.tree_variables)

                return executor.execute()

            elif isinstance(command, AssignField):
                executor = ExpressionExecutor(command.expression, self.tree_variables)
                var = Variable(command.name, executor.execute())

                self.tree_variables.set(var)

            elif isinstance(command, Print):
                executor = ExpressionExecutor(command.expression, self.tree_variables)

                printer.raw_print(executor.execute())

            elif isinstance(command, When):
                executor = ExpressionExecutor(command.expression, self.tree_variables)
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
                executor_from = ExpressionExecutor(command.expression_from, self.tree_variables)
                executor_to = ExpressionExecutor(command.expression_to, self.tree_variables)

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

                        if not isinstance(executed, Void):
                            return executed

            else:
                raise ErrorType(f"Неизвестная команда '{command.name}'!", info=command.meta_info)

        return Void()
