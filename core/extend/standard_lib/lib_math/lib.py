from pathlib import Path
from typing import Optional

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
name_module = "математика"


@builder.collect(func_name='степень')
class Pow(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        if not all(isinstance(x, Number) for x in args):
            raise ErrorValue("Аргументы должны быть числами")

        base, exponent = args

        # Проверка на комплексный результат при отрицательном основании и дробной степени
        if base.value < 0 and not exponent.value.is_integer():
            raise ErrorValue("Отрицательное основание с дробной степенью дает комплексный результат")

        return Number(math.pow(base.value, exponent.value))


@builder.collect(func_name='остаток')
class Mod(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        if not all(isinstance(x, Number) for x in args):
            raise ErrorValue("Аргументы должны быть числами")

        dividend, divisor = args

        if divisor.value == 0:
            raise ErrorValue("Деление на ноль невозможно")

        return Number(dividend.value % divisor.value)


@builder.collect(func_name='корень')
class Sqrt(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        arg = args[0]

        if not isinstance(arg, Number):
            raise ErrorValue("Аргумент должен быть числом")

        if arg.value < 0:
            raise ErrorValue("Нельзя извлечь корень из отрицательного числа")

        return Number(math.sqrt(arg.value))


@builder.collect(func_name='синус')
class Sin(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        arg = args[0]

        if not isinstance(arg, Number):
            raise ErrorValue("Аргумент должен быть числом")

        return Number(math.sin(arg.value))


@builder.collect(func_name='косинус')
class Cos(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        arg = args[0]

        if not isinstance(arg, Number):
            raise ErrorValue("Аргумент должен быть числом")

        return Number(math.cos(arg.value))


@builder.collect(func_name='пи')
class Pi(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        return Number(math.pi)


@builder.collect(func_name='модуль')
class Abs(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        arg = args[0]

        if not isinstance(arg, Number):
            raise ErrorValue("Аргумент должен быть числом")

        return Number(math.fabs(arg.value))


@builder.collect(func_name='округлить')
class Round(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        arg = args[0]

        if not isinstance(arg, Number):
            raise ErrorValue("Аргумент должен быть числом")

        return Number(round(arg.value))


@builder.collect(func_name='экспонента')
class Exp(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        arg = args[0]

        if not isinstance(arg, Number):
            raise ErrorValue("Аргумент должен быть числом")

        return Number(math.exp(arg.value))


@builder.collect(func_name='логарифм')
class Log(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        if not all(isinstance(x, Number) for x in args):
            raise ErrorValue("Аргументы должны быть числами")

        num, base = args

        if num.value <= 0 or base.value <= 0:
            raise ErrorValue("Аргументы должны быть положительными")

        return Number(math.log(num.value, base.value))


@builder.collect(func_name='тангенс')
class Tan(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import math

        from core.types.atomic import Number
        from core.exceptions import ErrorValue

        arg = args[0]

        if not isinstance(arg, Number):
            raise ErrorValue("Аргумент должен быть числом")

        return Number(math.tan(arg.value))


if __name__ == '__main__':
    builder.build_python_extend(f"{standard_lib_path}{name_module}")
