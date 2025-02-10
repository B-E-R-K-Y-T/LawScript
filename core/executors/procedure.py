from typing import TYPE_CHECKING, Optional, Union

from core.exceptions import EmptyReturn
from core.tokens import Tokens
from core.types.procedure import Procedure, Expression, Print, Return
from core.executors.base import Executor
from util.console_worker import printer

if TYPE_CHECKING:
    from util.compile import Compiled


class Operation:
    def __init__(
            self, operand1: Optional[Union[str, float]] = None,
            operand2: Optional["Operation"] = None,
            operation: Optional[str] = None
    ):
        self.operand1 = operand1
        self.operand2 = operand2
        self.operation = operation


class ExpressionExecutor(Executor):
    def __init__(self, expression: list[str]):
        self.expression = expression
        self.jump = 0
        self.result_operation = Operation()

    def parse_expr(self) -> Operation:
        for offset, operation in enumerate(self.expression):
            if offset < self.jump:
                continue


            if operation == Tokens.star:
                self.jump += 1

                self.result_operation.operand1 = self.expression[offset - 1]
                self.result_operation.operand2 = Operation(
                    self.expression[offset + 1],
                    Operation(),
                    None
                )
                self.result_operation.operation = operation

    def execute(self, expr: Operation):
        print(expr)




class ProcedureExecutor(Executor):
    def __init__(self, procedure: Procedure, compiled: "Compiled"):
        self.procedure = procedure
        self.compiled = compiled

    def prepare_expression(self, expression: list[str]) -> list[str]:
        for scope in self.procedure.tree_variables.scopes:
            for name, variable in scope.variables.items():
                for offset, operation in enumerate(expression):
                    if name == operation:
                        expression[offset] = str(variable.value)

        return  expression

        # print(expression)
        #
        # return self.aeval(expression)

    def execute(self):
        for command in self.procedure.body.commands:
            if isinstance(command, Return):
                if not command.expression.operations:
                    raise EmptyReturn

                return self.prepare_expression(command.expression.operations)

            if isinstance(command, Expression):
                return self.execute_evaluate(command.operations)

            if isinstance(command, Print):
                expr_executor = ExpressionExecutor(self.prepare_expression(command.expression.operations))
                printer.raw_print(expr_executor.execute(expr_executor.parse_expr()))
