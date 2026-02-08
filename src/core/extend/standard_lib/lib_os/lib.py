from typing import Optional

from pathlib import Path
from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
MOD_NAME = "ос"


@builder.collect(func_name='нормализовать_путь')
class PathNormalizer(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.extend.standard_lib.util import path_normpath
        from src.core.types.atomic import String
        from src.core.exceptions import ErrorType

        path = args[0]

        if not isinstance(path, String):
            raise ErrorType(f"Аргумент должен иметь тип '{String.type_name()}'!")

        return String(path_normpath(path.value))


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
