from typing import Optional

from core.exceptions import InvalidSyntaxError, InvalidType
from core.parse.base import Parser, MetaObject, Image, is_integer, is_float
from core.tokens import Tokens
from core.types.conditions import Modify, Only, LessThan, GreaterThan, Between, NotEqual
from core.types.criteria import Criteria
from core.types.line import Line
from core.util import is_ignore_line
from util.console_worker import printer


class DefineCriteriaMetaObject(MetaObject):
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

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных DefineCriteria с stop_num={stop_num} и criteria={self.criteria}",
                        level="INFO")
        return DefineCriteriaMetaObject(
            stop_num,
            criteria=self.criteria,
        )

    @staticmethod
    def parse_to_num(value: str, line):
        if is_float(value):
            return float(value)
        if is_integer(value):
            return int(value)

        raise InvalidType(value, "число", line)

    def process_not_may_be_case(self, name_criteria, value, line):
        """Обрабатывает случай с 'not may be'."""
        if len(value) == 1:
            return self.parse_single_value(value[0], line)
        return self.parse_many_word_to_str(value)

    def parse_single_value(self, value: str, line):
        """Попытка преобразовать одно значение в число, иначе в строку."""
        try:
            return self.parse_to_num(value, line)
        except InvalidType:
            return self.parse_many_word_to_str([value])

    def parse(self, body: list[Line], jump) -> int:
        printer.logging(f"Начало парсинга DefineCriteria с jump={jump} {Criteria.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.criteria, Tokens.left_bracket]:
                    printer.logging("Обнаружена секция 'criteria'", level="INFO")
                case [name_criteria, Tokens.only, *value, Tokens.comma]:
                    self.criteria[name_criteria] = Only(self.parse_many_word_to_str(value))
                    printer.logging(f"Добавлено условие 'Only' для {name_criteria} с значениями {value}", level="INFO")
                case [name_criteria, Tokens.not_, Tokens.may, Tokens.be, *value, Tokens.comma]:
                    processed_value = self.process_not_may_be_case(name_criteria, value, line)
                    self.criteria[name_criteria] = NotEqual(processed_value)
                    printer.logging(
                        f"Добавлено условие 'NotEqual' для {name_criteria} с значениями {value}", level="INFO"
                    )
                case [name_criteria, Tokens.less, value, Tokens.comma]:
                    value = self.parse_to_num(value, line)
                    self.criteria[name_criteria] = LessThan(value)
                    printer.logging(f"Добавлено условие 'LessThan' для {name_criteria} с значением {value}",
                                    level="INFO")
                case [name_criteria, Tokens.greater, value, Tokens.comma]:
                    value = self.parse_to_num(value, line)
                    self.criteria[name_criteria] = GreaterThan(value)
                    printer.logging(f"Добавлено условие 'GreaterThan' для {name_criteria} с значением {value}",
                                    level="INFO")
                case [name_criteria, Tokens.between, value1, Tokens.and_, value2, Tokens.comma]:
                    values = []

                    for value in (value1, value2):
                        values.append(self.parse_to_num(value, line))

                    self.criteria[name_criteria] = Between(*values)
                    printer.logging(f"Добавлено условие 'Between' для {name_criteria} с значениями {values}",
                                    level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг criteria завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг criteria завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
