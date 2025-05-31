from typing import TYPE_CHECKING

from core.executors.body import BodyExecutor
from core.types.basetype import BaseAtomicType
from core.types.procedure import Procedure
from core.executors.base import Executor

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled


class ProcedureExecutor(Executor):
    def __init__(self, procedure: Procedure, compiled: "Compiled"):
        self.procedure = procedure
        self.compiled = compiled

    def execute(self) -> BaseAtomicType:
        body = BodyExecutor(self.procedure.body, self.procedure.tree_variables, self.compiled)
        return body.execute()

    def async_execute(self):
        body = BodyExecutor(self.procedure.body, self.procedure.tree_variables, self.compiled)
        return body.async_execute()
