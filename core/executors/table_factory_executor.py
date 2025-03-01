from typing import TYPE_CHECKING

from core.executors.base import Executor
from core.types.procedure import Procedure, AssignField
from core.types.table import TableFactory, Table
from core.types.variable import Variable

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled
    from core.executors.expression import ExpressionExecutor


def _get_expression_executor( *args, **kwargs) -> "ExpressionExecutor":
    from core.executors.expression import ExpressionExecutor
    return ExpressionExecutor(*args, **kwargs)


class TableFactoryExecutor(Executor):
    def __init__(self, factory: TableFactory, instance_table: Table, compiled: "Compiled"):
        self.factory = factory
        self.instance_table = instance_table
        self.compiled = compiled

    def execute(self):
        for cmd in self.factory.table_image.body.commands:
            if isinstance(cmd, Procedure):
                self.instance_table.tree_variables.set(Variable(cmd.name, cmd))
            elif isinstance(cmd, AssignField):
                executor = _get_expression_executor(cmd.expression, self.instance_table.tree_variables, self.compiled)
                self.instance_table.tree_variables.set(Variable(cmd.name, executor.execute()))
