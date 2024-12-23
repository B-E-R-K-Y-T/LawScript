from typing import TYPE_CHECKING

from asteval import Interpreter

from core.tokens import Tokens
from core.types.procedure import Procedure, Expression, Print, Return
from core.executors.base import Executor
from util.console_worker import printer

if TYPE_CHECKING:
    from util.compile import Compiled


class ProcedureExecute(Executor):
    def __init__(self, obj: Procedure, compiled: "Compiled"):
        self.obj = obj
        self.compiled = compiled
        self.aeval = Interpreter()

    def prepare_expression(self, expression: list[str]) -> str:
        for scope in self.obj.tree_variables.scopes:
            for name, variable in scope.variables.items():
                for offset, operation in enumerate(expression):
                    if name == operation:
                        expression[offset] = str(variable.value)

        return  " ".join(expression).replace(f"{Tokens.end_expr}", "")

    def execute_evaluate(self, expression: list[str]):
        expression = self.prepare_expression(expression)
        return self.aeval(expression)

    def execute(self):
        for command in self.obj.body.commands:
            if isinstance(command, Return):
                return self.execute_evaluate(command.expression.operations)

            if isinstance(command, Expression):
                return self.execute_evaluate(command.operations)

            if isinstance(command, Print):
                printer.raw_print(self.execute_evaluate(command.expression.operations))
