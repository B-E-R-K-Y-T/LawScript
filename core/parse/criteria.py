from typing import Optional

from core.exceptions import InvalidSyntaxError, InvalidType
from core.parse.base import Parser, Metadata, Image, is_integer, is_float
from core.token import Token
from core.types.conditions import Modify, Only, LessThan, GreaterThan, Between, NotOnly
from core.types.criteria import Criteria
from core.util import is_ignore_line
from util.console_worker import printer


class DefineCriteriaMetadata(Metadata):
    def __init__(self, stop_num: int, criteria: dict[str, Modify]):
        super().__init__(stop_num)
        self.criteria = criteria
        printer.logging(f"Создано DefineCriteriaMetadata с stop_num={stop_num} и criteria={criteria}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа DefineCriteriaMetadata с criteria={self.criteria}", level="INFO")
        return Image(
            name=str(id(self)),
            obj=Criteria,
            image_args=(self.criteria,)
        )


class DefineCriteriaParser(Parser):
    def __init__(self):
        self.criteria: Optional[dict[str, Modify]] = {}
        printer.logging("Инициализация DefineCriteriaParser", level="INFO")

    def create_metadata(self, stop_num: int) -> Metadata:
        printer.logging(f"Создание метаданных DefineCriteria с stop_num={stop_num} и criteria={self.criteria}", level="INFO")
        return DefineCriteriaMetadata(
            stop_num,
            criteria=self.criteria,
        )

    def parse(self, body: list[str], jump) -> int:
        printer.logging(f"Начало парсинга DefineCriteria с jump={jump}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.criteria, Token.start_body]:
                    printer.logging("Обнаружена секция 'criteria'", level="INFO")
                case [name_criteria, Token.only, *value, Token.comma]:
                    self.criteria[name_criteria] = Only(self.parse_many_word_to_str(value))
                    printer.logging(f"Добавлено условие 'Only' для {name_criteria} с значениями {value}", level="INFO")
                case [name_criteria, Token.not_, Token.may, Token.be, *value, Token.comma]:
                    self.criteria[name_criteria] = NotOnly(self.parse_many_word_to_str(value))
                    printer.logging(f"Добавлено условие 'NotOnly' для {name_criteria} с значениями {value}", level="INFO")
                case [name_criteria, Token.less, value, Token.comma]:
                    if is_float(value):
                        value = float(value)
                    elif is_integer(value):
                        value = int(value)
                    else:
                        raise InvalidType(value, "число", line)

                    self.criteria[name_criteria] = LessThan(value)
                    printer.logging(f"Добавлено условие 'LessThan' для {name_criteria} с значением {value}", level="INFO")
                case [name_criteria, Token.greater, value, Token.comma]:
                    if is_float(value):
                        value = float(value)
                    elif is_integer(value):
                        value = int(value)
                    else:
                        raise InvalidType(value, "число", line)

                    self.criteria[name_criteria] = GreaterThan(value)
                    printer.logging(f"Добавлено условие 'GreaterThan' для {name_criteria} с значением {value}", level="INFO")
                case [name_criteria, Token.between, value1, Token.and_, value2, Token.comma]:
                    values = []

                    for value in (value1, value2):
                        if is_float(value):
                            values.append(float(value))
                        elif is_integer(value):
                            values.append(int(value))
                        else:
                            raise InvalidType(value, "число", line)

                    self.criteria[name_criteria] = Between(*values)
                    printer.logging(f"Добавлено условие 'Between' для {name_criteria} с значениями {values}", level="INFO")
                case [Token.end_body]:
                    printer.logging("Парсинг criteria завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line)

        printer.logging("Парсинг criteria завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
