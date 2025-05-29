from typing import Optional

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()


@builder.collect(func_name='в_строку')
class ToString(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.tokens import Tokens

        args = self.parse_args(args)
        arg = args[0]

        if isinstance(arg, bool):
            if arg:
                return String(Tokens.true)
            else:
                return String(Tokens.false)

        return String(str(arg))


@builder.collect(func_name='форматировать_строку')
class StringFormat(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.offset_required_args = 2
        self.count_args = -1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String):
            raise ErrorValue("Первый аргумент должен быть строкой.")

        line, *pattern = self.parse_args(args)

        return String(line.format(*pattern))


if __name__ == '__main__':
    builder.build_python_extend("строки")
