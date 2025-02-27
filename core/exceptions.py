from typing import Optional, Any

from core.tokens import Tokens
from core.types.line import Info
from core.types.severitys import Levels


class BaseError(Exception):
    def __init__(self, msg: Optional[str] = None, *, line: Optional[list[str]] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Ошибка."

        if line is not None:
            msg = f"{msg} Строка: '{" ".join(line)}'"

        if info is not None:
            msg = f"Ошибка: '{msg}' Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(msg)


class MaxRecursionError(BaseError):
    def __init__(self, msg: Optional[str] = None, *, line: Optional[list[str]] = None, info: Optional[Info] = None):
        if msg is None:
            msg = f"Превышена максимальная глубина рекурсии!"

        msg = f"{msg} Ошибка: 'Максимальная глубина рекурсии."

        super().__init__(
            msg=msg,
            line=line,
            info=info,
        )


class InvalidSyntaxError(BaseError):
    def __init__(self, msg: Optional[str] = None, *, line: Optional[list[str]] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Некорректный синтаксис"

        if line is not None:
            msg = f"{msg} Строка: '{" ".join(line)}'"

        if info is not None:
            msg = f"Ошибка: '{msg}' Файл: {info.file}, Номер строки: {info.num}"

        super().__init__(msg)


class InvalidLevelDegree(BaseError):
    def __init__(self, degree: str):
        super().__init__(
            f"Значение: '{degree}' запрещено для типа '{Tokens.degree} {Tokens.of_rigor}'. "
            f"Используйте один из следующих типов: {[str(level) for level in Levels]}"
        )


class InvalidType(BaseError):
    def __init__(self, value: Any, type_: str, line: Optional[list[str]] = None):
        msg = f"Значение: '{value}' должно иметь тип: '{type_}'!"

        if line is not None:
            msg = f"Ошибка в строке: '{" ".join(line)} ' \n{msg}"

        super().__init__(msg)


class UnknownType(BaseError):
    def __init__(self, msg: Optional[str] = None):
        if msg is None:
            msg = "Неизвестный тип!"

        super().__init__(msg)


class ErrorType(BaseError):
    def __init__(self, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Ошибка типа!"

        if info is not None:
            msg = f"Ошибка: '{msg}' Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(msg)


class NameNotDefine(BaseError):
    def __init__(self, msg: Optional[str] = None, name: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Имя не определено!"

        if name is not None:
            msg = f"Ошибка: '{msg}' Имя: '{name}' используется до его определения!"

        if info is not None:
            msg = f"Ошибка: '{msg}' Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(msg)


class FieldNotDefine(BaseError):
    def __init__(self, field: str, define: str):
        super().__init__(
            f"Поле: '{field}' не определено в '{define}'"
        )


class NameAlreadyExist(BaseError):
    def __init__(self, name: str):
        super().__init__(f"Имя: '{name}' уже существует")


class EmptyReturn(BaseError):
    def __init__(self, msg: Optional[str] = None):
        if msg is None:
           msg = "Возвращаемое значение пусто"

        super().__init__(msg)


class InvalidExpression(BaseError):
    def __init__(self, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
           msg = "Некорректное выражение"

        if info is not None:
            msg = f"Ошибка: '{msg}' Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(msg)


class DivisionByZeroError(BaseError):
    def __init__(self, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Деление на ноль"

        super().__init__(msg, info=info)


class ArgumentError(BaseError):
    def __init__(self, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Ошибка аргумента"

        super().__init__(msg, info=info)
