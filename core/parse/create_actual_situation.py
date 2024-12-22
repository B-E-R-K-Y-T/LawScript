from typing import Optional, Any

from core.exceptions import InvalidSyntaxError, InvalidType
from core.parse.base import Parser, MetaObject, Image, is_integer, is_float
from core.tokens import Tokens
from core.types.documents import FactSituation
from core.types.line import Line
from core.util import is_ignore_line
from util.console_worker import printer


class ActualSituationMetaObject(MetaObject):
    def __init__(
            self,
            stop_num: int,
            fact_name: str,
            *args
    ):
        super().__init__(stop_num)
        self.fact_name = fact_name
        self.args = args
        printer.logging(f"Создан объект ActualSituationMetadata с stop_num={stop_num}, fact_name='{fact_name}', args={args}", level="INFO")

    def create_image(self):
        printer.logging(f"Создание образа факта с name='{self.fact_name}', args={self.args}", level="INFO")
        return Image(
            name=self.fact_name,
            obj=FactSituation,
            image_args=self.args
        )


class CreateActualSituationParser(Parser):
    def __init__(self):
        self.fact_name: Optional[str] = None
        self.name_object: Optional[str] = None
        self.name_subject: Optional[str] = None
        self.data: Optional[dict[str, Any]] = None
        self.jump = 0
        printer.logging("Инициализация CreateActualSituationParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных с stop_num={stop_num}, fact_name='{self.fact_name}', name_object='{self.name_object}', name_subject='{self.name_subject}'", level="INFO")
        return ActualSituationMetaObject(
            stop_num,
            self.fact_name,
            self.name_object,
            self.name_subject,
            self.data,
        )

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга с jump={jump}, строки: {body}", level="INFO")

        for num, line in enumerate(body):
            info = line.get_file_info()

            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.create, Tokens.the_actual, Tokens.the_situation, fact_name, Tokens.left_bracket]:
                    self.fact_name = fact_name
                    printer.logging(f"Найдена секция 'create actual situation' с fact_name='{fact_name}'", level="INFO")
                case [Tokens.object, name_object, Tokens.comma]:
                    self.name_object = name_object
                    printer.logging(f"Найден объект с name_object='{name_object}'", level="INFO")
                case [Tokens.subject, name_subject, Tokens.comma]:
                    self.name_subject = name_subject
                    printer.logging(f"Найден субъект с name_subject='{name_subject}'", level="INFO")
                case [Tokens.data, *_]:
                    meta = self.execute_parse(DataParser, body, num)
                    self.data = meta.data
                    printer.logging(f"Данные успешно парсены: {self.data}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError


class CollectionData(MetaObject):
    def __init__(
            self,
            stop_num: int,
            data: dict[str, Any],
            *args
    ):
        super().__init__(stop_num)
        self.data = data
        self.args = args
        printer.logging(f"Создан объект CollectionData с stop_num={stop_num}, data={data}", level="INFO")

    def create_image(self): ...


class DataParser(Parser):
    def __init__(self):
        self.collection_data: dict[str, Any] = {}
        self.jump = 0
        printer.logging("Инициализация DataParser", level="INFO")

    def create_metadata(self, stop_num: int) -> CollectionData:
        printer.logging(f"Создание метаданных CollectionData с stop_num={stop_num}, collection_data={self.collection_data}", level="INFO")
        return CollectionData(
            stop_num,
            self.collection_data,
        )

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга данных с jump={jump}", level="INFO")

        for num, line in enumerate(body):
            info = line.get_file_info()

            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.data, Tokens.left_bracket]:
                    printer.logging("Начало секции данных, ожидается ввод", level="INFO")
                case [name_data, *data, Tokens.comma]:
                    value = self.parse_many_word_to_str(data)

                    if is_float(value):
                        value = float(value)
                    elif is_integer(value):
                        value = int(value)

                    self.collection_data[name_data] = value
                    printer.logging(f"Добавлено data: {name_data} = {value}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг данных завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис в DataParser: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг данных завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
