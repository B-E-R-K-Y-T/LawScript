from core.types.checkers import CheckerSituation
from core.types.conditions import ResultCondition
from core.util import kill_process
from util.build_tools.compile import Compiled
from util.console_worker import printer
from core.executors.base import Executor


class CheckerSituationExecutor(Executor):
    def __init__(self, obj: CheckerSituation, compiled: Compiled):
        self.checker = obj
        self.compiled = compiled

    def execute(self):
        try:
            check_result: dict[str, ResultCondition] = self.checker.check(self.compiled)
        except TypeError as e:
            kill_process(f"{e}Имя проверки: {self.checker.name}")
            return

        printer.print_info(
            f"Отчет проверки: {self.checker.name} об анализе соответствия ситуации: '{self.checker.fact_situation.name}' "
            f"документу '{self.checker.document.name}' "
            f"по следующим критериям:\n"
        )

        table_data = {
            "Название критерия": [],
            "Фактические данные": [],
            "Результат": [],
            "Тип проверки": [],
        }

        for criteria, result_condition in check_result.items():
            result = self.checker.check_result_map[result_condition.result]

            table_data["Название критерия"].append(criteria)
            table_data["Фактические данные"].append(result_condition.value_fact_data)
            table_data["Результат"].append(result)
            table_data["Тип проверки"].append(result_condition.modify)

        printer.print_table(table_data, title=f"Результаты анализа проверкой: '{self.checker.name}'")
