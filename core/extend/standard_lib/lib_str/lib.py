from pathlib import Path
from typing import Optional

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"


@builder.collect(func_name='в_строку')
class ToString(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.tokens import Tokens
        from core.types.procedure import LinkedProcedure

        if isinstance(args[0], LinkedProcedure):
            return String(str(args[0].func))

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
        from core.tokens import Tokens

        if not isinstance(args[0], String):
            raise ErrorValue("Первый аргумент должен быть строкой.")

        line, *tail_args = self.parse_args(args)

        for idx, tail_arg in enumerate(tail_args):
            if isinstance(tail_arg, bool):
                tail_arg = Tokens.true if tail_arg else Tokens.false
                tail_args[idx] = tail_arg

            elif tail_arg is None:
                tail_args[idx] = Tokens.void

        return String(line.format(*tail_args))


if __name__ == '__main__':
    builder.build_python_extend(f"{standard_lib_path}строки")
