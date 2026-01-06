from pathlib import Path
from typing import Optional

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
MOD_NAME = "ввод_вывод"


@builder.collect(func_name='вывод')
class ViewObjectFields(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 3
        self.offset_required_args = 1
        self.replace_map = {
            "\\n": "\n",      # Новая строка
            "\\t": "\t",      # Табуляция
            "\\r": "\r",      # Возврат каретки
            "\\\\": "\\",     # Обратный слеш
            "\\'": "'",       # Одинарная кавычка
            '\\"': '"',       # Двойная кавычка
            "\\b": "\b",      # Backspace
            "\\f": "\f",      # Form feed
            "\\v": "\v",      # Вертикальная табуляция
            "\\a": "\a",      # Звонок (bell)
        }

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import VOID

        parsed_args = self.parse_args(args)
        sep, end = "", ""

        if len(args) > 1:
            sep = parsed_args[1]

        if len(args) > 2:
            end = parsed_args[2]

        for old, new in self.replace_map.items():
            sep = sep.replace(old, new)
            end = end.replace(old, new)

        print(parsed_args[0], sep=sep, end=end)

        return VOID


@builder.collect(func_name='ввод')
class ViewObjectFields(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import convert_py_type_to_atomic_type

        parsed_args = self.parse_args(args)

        return convert_py_type_to_atomic_type(input(parsed_args[0]))


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
