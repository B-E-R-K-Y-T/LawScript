from typing import Optional, Any

from core.tokens import Tokens
from core.types.line import Line, Info
from core.types.severitys import Levels


class BaseError(Exception):
    pass


class InvalidSyntaxError(BaseError):
    def __init__(self, msg: Optional[str] = None, *, line: Optional[list[str]] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Некорректный синтаксис"

        if line is not None:
            msg = f"{msg}\nСтрока: '{" ".join(line)}'"

        if info is not None:
            msg = f"Файл: {info.file}, Номер строки: {info.num}\n{msg}"

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

        super().__init__(
            msg
        )


class UnknownType(BaseError):
    def __init__(self, msg: Optional[str] = None):
        if msg is None:
            msg = "Неизвестный тип!"

        super().__init__(msg)


class NameNotDefine(BaseError):
    def __init__(self, msg: Optional[str] = None, name: Optional[str] = None):
        if msg is None:
            msg = "Имя не определено!"

        if name is not None:
            msg = f"Ошибка: '{msg}' Имя: '{name}' используется до его определения!"

        super().__init__(msg)


class FieldNotDefine(BaseError):
    def __init__(self, field: str, define: str):
        super().__init__(
            f"Поле: '{field}' не определено в '{define}'"
        )


class NameAlreadyExist(BaseError):
    def __init__(self, name: str):
        super().__init__(f"Имя: '{name}' уже существует")
