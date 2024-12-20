import pickle

from core.parse.base import Metadata
from core.token import Token
from core.types.basetype import BaseType
from core.types.checkers import CheckerSituation
from core.types.conditions import ResultCondition
from core.util import kill_process
from util.ast import AbstractSyntaxTreeBuilder
from util.compile import Compiler
from util.console_worker import printer


class Interpreter:
    def __init__(self, compiled: dict[str, BaseType]):
        self.compiled = compiled

    def run(self):
        for name, obj in self.compiled.items():
            if isinstance(obj, CheckerSituation):
                try:
                    check_result: dict[str, ResultCondition] = obj.check()
                except TypeError as e:
                    kill_process(f"{e}Имя проверки: {obj.name}")
                    return

                printer.print_info(
                    f"Отчет проверки: {obj.name} об анализе соответствия ситуации: '{obj.fact_situation.name}' "
                    f"документу '{obj.document.name}' "
                    f"по следующим критериям:\n"
                )

                table_data = {
                    "Название критерия": [],
                    "Результат": [],
                    "Тип проверки": [],
                }

                for criteria, result_condition in check_result.items():
                    table_data["Название критерия"].append(criteria)
                    table_data["Результат"].append(obj.check_result_map[result_condition.result])
                    table_data["Тип проверки"].append(result_condition.modify)

                printer.print_table(table_data, title=f"Результаты анализа проверкой: '{obj.name}'")


def preprocess(raw_code) -> list:
    raw_code = [line.strip() for line in raw_code.split("\n")]
    preprocessed = []

    for line in raw_code:
        match line.split(" "):
            case [Token.include, path]:
                try:
                    with open(path, "r", encoding="utf-8") as nested_file:
                        preprocessed.extend(preprocess_file(nested_file))
                except FileNotFoundError:
                    kill_process(f"Файл для включения не найден: {path}")
                except RecursionError:
                    kill_process(f"Обнаружен циклический импорт {path}")
            case _:
                preprocessed.append(line)

    return [line for line in preprocessed if line]


def preprocess_file(file) -> list:
    return preprocess(file.read())


def run_compiled_code(compiled: dict[str, BaseType]):
    interpreter = Interpreter(compiled)
    interpreter.run()


def run(raw_code: str):
    code = preprocess(raw_code)

    ast_builder = AbstractSyntaxTreeBuilder(code)
    ast: list[Metadata] = ast_builder.build()

    compiler = Compiler(ast)
    run_compiled_code(compiler.compile())


def run_file(path: str):
    if path.endswith('.law'):
        with open(path, "rb") as file:  # Используем бинарное чтение для .lawc
            compiled = pickle.load(file)
            run_compiled_code(compiled)
    else:
        with open(path, "r", encoding="utf-8") as file:
            run(file.read())
