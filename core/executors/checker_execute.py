from core.types.checkers import CheckerSituation
from core.types.conditions import ResultCondition
from core.util import kill_process
from util.console_worker import printer
from core.executors.base import Executor


class CheckerSituationExecute(Executor):
    def __init__(self, obj: CheckerSituation):
        self.obj = obj

    def execute(self):
        try:
            check_result: dict[str, ResultCondition] = self.obj.check()
        except TypeError as e:
            kill_process(f"{e}Имя проверки: {self.obj.name}")
            return

        printer.print_info(
            f"Отчет проверки: {self.obj.name} об анализе соответствия ситуации: '{self.obj.fact_situation.name}' "
            f"документу '{self.obj.document.name}' "
            f"по следующим критериям:\n"
        )

        table_data = {
            "Название критерия": [],
            "Результат": [],
            "Тип проверки": [],
        }

        for criteria, result_condition in check_result.items():
            result = self.obj.check_result_map[result_condition.result]

            table_data["Название критерия"].append(criteria)
            table_data["Результат"].append(result)
            table_data["Тип проверки"].append(result_condition.modify)

        printer.print_table(table_data, title=f"Результаты анализа проверкой: '{self.obj.name}'")
