from typing import Optional

from pathlib import Path

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
MOD_NAME = "аргументы_запуска"


@builder.collect(func_name='получить_аргументы_запуска')
class Request(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from config import global_storage
        from src.core.types.atomic import convert_py_type_to_atomic_type

        return convert_py_type_to_atomic_type(global_storage.SYS_ARGS)


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
