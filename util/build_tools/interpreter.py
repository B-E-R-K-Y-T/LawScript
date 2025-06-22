from core.executors.execute_block import ExecuteBlockExecutor
from core.types.checkers import CheckerSituation
from core.types.execute_block import ExecuteBlock
from util.build_tools.compile import Compiled
from core.executors.checker_execute import CheckerSituationExecutor


class Interpreter:
    def __init__(self, compiled: Compiled):
        self.compiled = compiled

    def run(self):
        for name, obj in self.compiled.compiled_code.items():
            if isinstance(obj, CheckerSituation):
                executor = CheckerSituationExecutor(obj, self.compiled)
                executor.execute()
            elif isinstance(obj, ExecuteBlock):
                executor = ExecuteBlockExecutor(obj, self.compiled)
                executor.execute()
