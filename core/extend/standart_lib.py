from typing import Optional


from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.atomic import Number, String, Boolean
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()


@builder.collect(func_name='print')
class Print(PyExtendWrapper):
    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Void

        print(*self.parse_args(args))

        return Void()


@builder.collect(func_name='input')
class Input(PyExtendWrapper):
    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.exceptions import BaseError
        from core.types.atomic import String

        args = self.parse_args(args)
        start_line = ">>>"

        if args:
            start_line = args[0]

        if isinstance(start_line, str):
            res = input(start_line)
            return String(res)

        raise BaseError(f"Неверный тип ввода! Ввод должен быть строкой, а введено: '{start_line}'")


@builder.collect(func_name='to_number')
class ToNumber(PyExtendWrapper):
    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.exceptions import BaseError, ErrorType
        from core.types.atomic import Number

        args = self.parse_args(args)
        arg = None

        if not args:
            raise BaseError(f"Функция {self.func_name} принимает только один аргумент!")

        if args:
            if len(args) != 1:
                raise BaseError(f"Функция {self.func_name} принимает только один аргумент!")

            arg = args[0]

        for t in [int, float]:
            try:
                return Number(t(arg))
            except ValueError:
                continue

        raise ErrorType(f"Невозможно преобразовать '{arg}' в число")


@builder.collect(func_name='to_string')
class ToString(PyExtendWrapper):
    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.exceptions import BaseError
        from core.types.atomic import String
        from core.tokens import Tokens

        args = self.parse_args(args)

        if args:
            if len(args) != 1:
                raise BaseError(f"Функция {self.func_name} принимает только один аргумент!")

            arg = args[0]

            if isinstance(arg, bool):
                if arg:
                    return String(Tokens.true)
                else:
                    return String(Tokens.false)

            return String(str(arg))


@builder.collect(func_name='func_wa')
class FuncWa(PyExtendWrapper):
    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number
        args = self.parse_args(args)
        return Number(int(args[0]) + 1)


if __name__ == '__main__':
    builder.build_python_extend("lib")
    print(builder.wrappers[0].call([Number(1)]))
    # print(builder.wrappers[1].call())
    print(builder.wrappers[2].call([String("1.2")]))
    print(builder.wrappers[3].call([Boolean(True)]))
