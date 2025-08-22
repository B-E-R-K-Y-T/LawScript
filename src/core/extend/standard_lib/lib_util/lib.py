from typing import Optional

from pathlib import Path

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/_/"
MOD_NAME = "util"


@builder.collect(func_name='_глубокое_копирование')
class DeepCopy(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from copy import deepcopy

        return deepcopy(args[0])


@builder.collect(func_name='_словарь_в_таблицу')
class PrintPrettyTable(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from rich.table import Table as RichTable
        from rich import print as rich_print
        from rich.box import SQUARE

        from src.core.types.atomic import Table, Void
        from src.core.exceptions import ErrorValue

        if not isinstance(args[0], Table):
            raise ErrorValue("Аргумент должен быть таблицей!")

        # Получаем словарь из таблицы
        table_data: dict = self.parse_args(args)[0]

        # Создаем красивую таблицу
        rich_table = RichTable(box=SQUARE, header_style="bold magenta")

        # Добавляем колонки
        if table_data:
            # Предполагаем, что это словарь {ключ: значение}
            rich_table.add_column("Ключ", style="cyan")
            rich_table.add_column("Значение", style="green")

            # Добавляем строки
            for key, value in table_data.items():
                rich_table.add_row(str(key), str(value))
        else:
            # Пустая таблица
            rich_table.add_column("Пустая таблица", justify="center")
            rich_table.add_row("Нет данных")

        # Выводим таблицу
        rich_print(rich_table)

        return Void()


if __name__ == '__main__':
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")
