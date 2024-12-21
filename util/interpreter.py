from core.types.checkers import CheckerSituation
from util.compile import Compiled
from util.executors.checker_execute import CheckerSituationExecute


class Interpreter:
    def __init__(self, compiled: Compiled):
        self.compiled = compiled.compiled_code

    def run(self):
        for name, obj in self.compiled.items():
            if isinstance(obj, CheckerSituation):
                executor = CheckerSituationExecute(obj)
                executor.execute()

