from pathlib import Path
from typing import Optional

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
MOD_NAME = "ввод_вывод"


@builder.collect(func_name='вывод')
class Print(PyExtendWrapper):
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

        print(args[0], sep=sep, end=end)

        return VOID


@builder.collect(func_name='ввод')
class Input(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import convert_py_type_to_atomic_type

        parsed_args = self.parse_args(args)

        return convert_py_type_to_atomic_type(input(parsed_args[0]))


@builder.collect(func_name='прочитать_файл')
class ReadFile(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import os
        from config import script_dir_storage
        from src.core.types.atomic import String, Array
        from src.core.exceptions import ErrorValue, FileError

        path = args[0]

        if not isinstance(path, String):
            raise ErrorValue("Аргумент должен быть строкой.")

        path = self.parse_args(args)[0]
        lines = []

        # Формируем полный путь относительно рабочей директории
        # Если путь абсолютный, os.path.join корректно его обработает
        full_path = os.path.join(script_dir_storage.LW_SCRIPT_DIR, path)

        # Нормализуем путь (убираем ../, ./ и т.д.)
        full_path = os.path.normpath(full_path)

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Убираем символы новой строки в конце
                    clean_line = line.rstrip('\n\r')
                    lines.append(String(clean_line))
        except FileNotFoundError:
            # Пробуем также исходный путь (на случай абсолютных путей)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        clean_line = line.rstrip('\n\r')
                        lines.append(String(clean_line))
            except FileNotFoundError:
                raise FileError(path)
        except Exception as e:
            raise FileError(f"Ошибка чтения файла '{path}': {str(e)}")

        return Array(lines)


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
