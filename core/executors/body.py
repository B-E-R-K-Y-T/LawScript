from typing import TYPE_CHECKING

from core.executors.expression import ExpressionExecutor
from core.types.atomic import Void
from core.types.basetype import BaseAtomicType
from core.types.procedure import Print, Return, AssignField, Body
from core.executors.base import Executor
from core.types.variable import Variable, ScopeStack
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

            if isinstance(command, AssignField):
                executor = ExpressionExecutor(command.expression, self.tree_variables)
                var = Variable(command.name, executor.execute())

                self.tree_variables.set(var)

            if isinstance(command, Print):
                executor = ExpressionExecutor(command.expression, self.tree_variables)

                printer.raw_print(executor.execute())

        return Void()
