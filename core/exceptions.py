from collections.abc import Iterable
from difflib import SequenceMatcher
from typing import Optional, Any, TYPE_CHECKING

from core.tokens import Tokens
from core.types.line import Info
from core.types.severitys import Levels

if TYPE_CHECKING:
    from core.types.variable import Scope


def get_probable_tokens(word: str, sequence: Optional[Iterable[str]] = Tokens, threshold=0.6):
    """Возвращает вероятные токены с учётом опечаток и регистра."""
    word = word.upper()  # Нормализуем регистр
    suggestions = []

    for item in sequence:
        normalized_item = item.upper()
        # Используем SequenceMatcher для учёта опечаток
        ratio = SequenceMatcher(None, word, normalized_item).ratio()

        # Дополнительные критерии
        starts_with_match = normalized_item.startswith(word[0])
        length_similarity = 1 - abs(len(normalized_item) - len(word)) / max(len(normalized_item), len(word))

        # Комбинированный рейтинг
        score = 0.7 * ratio + 0.2 * length_similarity + 0.1 * starts_with_match

        if score >= threshold:
            suggestions.append((item, score))

    # Сортируем по убыванию рейтинга
    return sorted(suggestions, key=lambda x: x[1], reverse=True)


class BaseError(Exception):
    def __init__(self, msg: Optional[str] = None, *, line: Optional[list[str]] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Ошибка."

        if line is not None:
            msg = f"{msg} Строка: '{" ".join(line)}'"

        if info is not None:
            msg = f"{msg} Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

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
            for word in line:
                if word not in Tokens:
                    sorted_matches = get_probable_tokens(word)
                    probable_tokens = ""

                    for i, (token, percent) in enumerate(sorted_matches[:3], 1):
                        probable_tokens += f"{i}. {token}\n"

                    if probable_tokens:
                        msg = (
                            f"{msg}\n\n"
                            f"Возможно, Вы имели ввиду? \n{probable_tokens}\n"
                        )
                        break
                else:
                    msg = f"{msg} Строка: '{" ".join(line)}'"

        super().__init__(msg, info=info)


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
            msg = f"{msg} Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(msg)


class ErrorValue(BaseError):
    def __init__(self, msg: Optional[str] = None, value: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Некорректное значение!"

        if value is not None:
            msg = f"{msg} Значение: '{value}'"

        if info is not None:
            msg = f"{msg} Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(msg)


class NameNotDefine(BaseError):
    def __init__(
            self, msg: Optional[str] = None, name: Optional[str] = None,
            info: Optional[Info] = None, scopes: Optional[list['Scope']] = None
    ):
        if msg is None:
            msg = "Имя не определено!"

        if name is not None:
            sorted_matches = []

            if scopes is not None:
                seq = []

                for scope in scopes:
                    for var in scope.variables.values():
                        seq.append(var.name)

                sorted_matches = get_probable_tokens(name, seq)

            if not sorted_matches:
                sorted_matches = get_probable_tokens(name)

            probable_tokens = ""

            for i, (token, percent) in enumerate(sorted_matches[:3], 1):
                probable_tokens += f"{i}. {token}\n"

            if probable_tokens:
                msg = (
                    f"{msg} Имя: '{name}' используется до его определения!\n\n"
                    f"Возможно, Вы имели ввиду? \n{probable_tokens}\n"
                )
            else:
                msg = f"{msg} Имя: '{name}' используется до его определения! "

        if info is not None:
            msg = f"{msg} Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(f"{msg}")


class FieldNotDefine(BaseError):
    def __init__(self, field: str, define: str):
        super().__init__(
            f"Поле: '{field}' не определено в '{define}'"
        )


class NameAlreadyExist(BaseError):
    def __init__(self, name: str, *, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = f"Имя: '{name}' уже существует"

        if info is not None:
            if info.file is not None:
                msg = f"{msg} Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"
            else:
                msg = f"{msg} Строка: {info.raw_line}"

        super().__init__(msg)


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
            msg = f"{msg} Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(f"{msg}")


class DivisionByZeroError(BaseError):
    def __init__(self, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Деление на ноль"

        super().__init__(msg, info=info)


class ErrorOverflow(BaseError):
    def __init__(self, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Переполнение стека!"

        msg = f"{msg} Переполнение стека."

        super().__init__(
            msg=msg,
            info=info
        )


class ArgumentError(BaseError):
    def __init__(self, msg: Optional[str] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Ошибка аргумента"

        super().__init__(msg, info=info)


class ErrorIndex(BaseError):
    def __init__(self, msg: Optional[str] = None, index: Optional[int] = None, info: Optional[Info] = None):
        if msg is None:
            msg = "Некорректный индекс"

        if index is not None:
            msg = f"{msg} Индекс: '{index}'"

        if info is not None:
            msg = f"{msg} Файл: {info.file}, Номер строки: {info.num}, Строка: {info.raw_line}"

        super().__init__(msg)
