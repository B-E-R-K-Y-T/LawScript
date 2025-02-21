from typing import TYPE_CHECKING

from core.exceptions import EmptyReturn
from core.executors.expression import ExpressionExecutor
from core.types.procedure import Procedure, Print, Return, AssignField
from core.executors.base import Executor
from core.types.variable import Variable
from util.console_worker import printer

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled


class ProcedureExecutor(Executor):
    def __init__(self, procedure: Procedure, compiled: "Compiled"):
        self.procedure = procedure
        self.compiled = compiled

    def execute(self):
        for command in self.procedure.body.commands:
            if isinstance(command, Return):
                if not command.expression.operations:
                    raise EmptyReturn

                executor = ExpressionExecutor(command.expression, self.procedure.tree_variables)

                return executor.execute()

            if isinstance(command, AssignField):
                executor = ExpressionExecutor(command.expression, self.procedure.tree_variables)
                var = Variable(command.name, executor.execute())

                self.procedure.tree_variables.set(var)

            if isinstance(command, Print):
                executor = ExpressionExecutor(command.expression, self.procedure.tree_variables)
                printer.raw_print(executor.execute())
