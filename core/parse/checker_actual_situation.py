from typing import Optional

from core.exceptions import InvalidSyntaxError, NameNotDefine
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.checkers import CheckerSituation
from core.types.line import Line
from core.util import is_ignore_line
from util.console_worker import printer


class CheckerActualSituationMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, document_name: str, fact_situation_name: str):
        super().__init__(stop_num)
        self.name = name
        self.document_name = document_name
        self.fact_situation_name = fact_situation_name
        printer.logging(
            f"Создан объект CheckerActualSituationMetadata с stop_num={stop_num}, name='{name}', document_name='{document_name}', fact_situation_name='{fact_situation_name}'",
            level="INFO")

    def create_image(self) -> Image:
        printer.logging(
            f"Создание образа с name='{self.name}', document_name='{self.document_name}', fact_situation_name='{self.fact_situation_name}'",
            level="INFO")
        return Image(
            name=self.name,
            obj=CheckerSituation,
            image_args=(self.document_name, self.fact_situation_name)
        )


class CheckerParser(Parser):
    def __init__(self):
        self.name: Optional[str] = None
        self.situation_name: Optional[str] = None
        self.document_name: Optional[str] = None
        self.jump = 0
        printer.logging("Инициализация CheckerParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных с stop_num={stop_num}", level="INFO")
        return CheckerActualSituationMetaObject(
            stop_num,
            name=self.name,
            document_name=self.document_name,
            fact_situation_name=self.situation_name,
        )

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга с jump={jump}, строки: {body}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.check, name, Tokens.left_bracket]:
                    self.name = name
                    printer.logging(f"Найдена секция 'check' с name='{name}'", level="INFO")
                case [Tokens.actual, Tokens.situation, situation_name, Tokens.comma]:
                    self.situation_name = situation_name
                    printer.logging(f"Найдена актуальная ситуация с name='{situation_name}'", level="INFO")
                case [Tokens.document, document_name, Tokens.comma]:
                    self.document_name = document_name
                    printer.logging(f"Найден документ с name='{document_name}'", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
