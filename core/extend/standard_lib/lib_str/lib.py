from pathlib import Path
from typing import Optional

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
name_module = "строки"


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


@builder.collect(func_name='длина_строки')
class StringLength(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number, String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String):
            raise ErrorValue("Первый аргумент должен быть строкой.")

        return Number(len(args[0].value))


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


@builder.collect(func_name='объединить_строки')
class StringConcat(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = -1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.exceptions import ErrorValue

        if not all(isinstance(x, String) for x in args):
            raise ErrorValue("Все аргументы должны быть строками")

        parts = [x for x in self.parse_args(args)]
        return String(''.join(parts))


@builder.collect(func_name='разделить_строку')
class StringSplit(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2  # Строка и разделитель

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String, Array
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String) or not isinstance(args[1], String):
            raise ErrorValue("Ожидались две строки (текст и разделитель)")

        text, delimiter = self.parse_args(args)
        return Array([String(x) for x in text.split(delimiter)])


@builder.collect(func_name='заменить_в_строке')
class StringReplace(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 3  # Текст, что заменить, на что заменить

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.exceptions import ErrorValue

        if not all(isinstance(x, String) for x in args):
            raise ErrorValue("Все аргументы должны быть строками")

        text, old, new = self.parse_args(args)
        return String(text.replace(old, new))


@builder.collect(func_name='найти_в_строке')
class StringFind(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2  # Строка и подстрока

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number, String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String) or not isinstance(args[1], String):
            raise ErrorValue("Ожидались две строки")

        text, substring = self.parse_args(args)
        return Number(text.find(substring))


@builder.collect(func_name='подстрока')
class Substring(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 3  # Строка, начало, конец

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String, Number
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String) or not all(isinstance(x, Number) for x in args[1:]):
            raise ErrorValue("Неверные типы аргументов")

        text, start, end = self.parse_args(args)
        return String(text[int(start):int(end)])


@builder.collect(func_name='верхний_регистр')
class UpperCase(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String):
            raise ErrorValue("Аргумент должен быть строкой")

        text = self.parse_args(args)[0]
        return String(text.upper())


@builder.collect(func_name='нижний_регистр')
class LowerCase(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String):
            raise ErrorValue("Аргумент должен быть строкой")

        text = self.parse_args(args)[0]
        return String(text.lower())


@builder.collect(func_name='убрать_пробелы')
class Strip(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String):
            raise ErrorValue("Аргумент должен быть строкой")

        text = self.parse_args(args)[0]
        return String(text.strip())


@builder.collect(func_name='начинается_с')
class StartsWith(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Boolean, String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String) or not isinstance(args[1], String):
            raise ErrorValue("Ожидались две строки")

        text, prefix = self.parse_args(args)
        return Boolean(text.startswith(prefix))


@builder.collect(func_name='заканчивается_на')
class EndsWith(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Boolean, String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String) or not isinstance(args[1], String):
            raise ErrorValue("Ожидались две строки")

        text, suffix = self.parse_args(args)
        return Boolean(text.endswith(suffix))


@builder.collect(func_name='регулярное_выражение')
class RegexMatch(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import re

        from core.types.atomic import Boolean, String
        from core.exceptions import ErrorValue

        if not isinstance(args[0], String) or not isinstance(args[1], String):
            raise ErrorValue("Ожидались две строки")

        text, pattern = self.parse_args(args)
        try:
            return Boolean(bool(re.match(pattern, text)))
        except re.error:
            raise ErrorValue("Некорректное регулярное выражение")


if __name__ == '__main__':
    builder.build_python_extend(f"{standard_lib_path}{name_module}")
