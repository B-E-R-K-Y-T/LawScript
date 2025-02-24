from core.types.checkers import CheckerSituation
from util.build_tools.compile import Compiled
from core.executors.checker_execute import CheckerSituationExecute


class Interpreter:
    def __init__(self, compiled: Compiled):
        self.compiled = compiled

    def run(self):
        for name, obj in self.compiled.compiled_code.items():
            if isinstance(obj, CheckerSituation):
                executor = CheckerSituationExecute(obj, self.compiled)
                executor.execute()
