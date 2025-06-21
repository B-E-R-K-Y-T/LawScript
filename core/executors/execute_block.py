from typing import TYPE_CHECKING

from core.executors.base import Executor
from core.executors.expression import ExpressionExecutor
from core.types.atomic import Void
from core.types.basetype import BaseAtomicType
from core.types.variable import ScopeStack, Variable

if TYPE_CHECKING:
    from core.types.execute_block import ExecuteBlock
    from util.build_tools.compile import Compiled


class ExecuteBlockExecutor(Executor):
    def __init__(self, execute_block: 'ExecuteBlock', compiled: 'Compiled'):
        self.execute_block = execute_block
        self.compiled = compiled

    def execute(self) -> BaseAtomicType:
        for expression in self.execute_block.expressions:
            scope_stack = ScopeStack()

            for object_name, value in self.compiled.compiled_code.items():
                scope_stack.set(Variable(object_name, value))

            expression_executor = ExpressionExecutor(expression, scope_stack, self.compiled)
            expression_executor.execute()

        return Void()
