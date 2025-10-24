from pathlib import Path
from typing import Optional

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
MOD_NAME = "типы"


@builder.collect(func_name='получить_тип')
class GetType(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import String, BaseAtomicType
        from src.core.types.classes import ClassInstance, ClassDefinition

        from src.core.exceptions import ErrorType

        arg = args[0]

        if isinstance(arg, ClassInstance):
            return String(arg.class_name)

        elif isinstance(arg, ClassDefinition):
            return String(arg.name)

        elif isinstance(arg, BaseAtomicType):
            return String(arg.__class__.type_name())

        raise ErrorType(f"Аргумент: '{arg}' имеет неизвестный тип!")


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
