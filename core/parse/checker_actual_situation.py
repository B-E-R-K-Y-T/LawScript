from typing import Optional

from core.exceptions import InvalidSyntaxError, NameNotDefine
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.checkers import CheckerSituation
from core.util import is_ignore_line
from util.console_worker import printer


class CheckerActualSituationMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, document_name: str, fact_situation_name: str):
        super().__init__(stop_num)
        self.name = name
        self.document_name = document_name
        self.fact_situation_name = fact_situation_name
        printer.logging(f"Создан объект CheckerActualSituationMetadata с stop_num={stop_num}, name='{name}', document_name='{document_name}', fact_situation_name='{fact_situation_name}'", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа с name='{self.name}', document_name='{self.document_name}', fact_situation_name='{self.fact_situation_name}'", level="INFO")
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

    def create_metadata(self, stop_num: int) -> Metadata:
        printer.logging(f"Создание метаданных с stop_num={stop_num}", level="INFO")
        return CheckerActualSituationMetadata(
            stop_num,
            name=self.name,
            document_name=self.document_name,
            fact_situation_name=self.situation_name,
        )

    def parse(self, body: list[str], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга с jump={jump}, строки: {body}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.check, name, Token.start_body]:
                    self.name = name
                    printer.logging(f"Найдена секция 'check' с name='{name}'", level="INFO")
                case [Token.actual, Token.situation, situation_name, Token.comma]:
                    self.situation_name = situation_name
                    printer.logging(f"Найдена актуальная ситуация с name='{situation_name}'", level="INFO")
                case [Token.document, document_name, Token.comma]:
                    self.document_name = document_name
                    printer.logging(f"Найден документ с name='{document_name}'", level="INFO")
                case [Token.end_body]:
                    printer.logging("Парсинг завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line)

        printer.logging("Парсинг завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
