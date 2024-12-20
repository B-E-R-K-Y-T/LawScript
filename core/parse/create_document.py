from typing import Optional, Type

from core.exceptions import InvalidSyntaxError
from core.types.documents import Document
from core.parse.base import Parser, parse_execute, Metadata, Image
from core.parse.define_disposition import DefineDispositionParser
from core.parse.define_hypothesis import DefineHypothesisParser
from core.parse.define_sanction import DefineSanctionParser
from core.token import Token
from core.util import is_ignore_line
from util.console_worker import printer


class DocumentMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, *args):
        super().__init__(stop_num)
        self.name = name
        self.args = args
        printer.logging(f"Создан объект DocumentMetadata с stop_num={stop_num}, name='{name}', args={args}", level="INFO")

    def create_image(self):
        printer.logging(f"Создание образа документа с name='{self.name}', args={self.args}", level="INFO")
        return Image(
            name=self.name,
            obj=Document,
            image_args=self.args
        )


class CreateDocumentParser(Parser):
    def __init__(self):
        self.document_name: Optional[str] = None
        self.hypothesis: Optional[Metadata] = None
        self.disposition: Optional[Metadata] = None
        self.sanction: Optional[Metadata] = None
        self.jump = 0
        printer.logging("Инициализация CreateDocumentParser", level="INFO")

    def create_metadata(self, stop_num: int) -> Metadata:
        printer.logging(f"Создание метаданных документа с stop_num={stop_num}, document_name='{self.document_name}', hypothesis='{self.hypothesis}', disposition='{self.disposition}', sanction='{self.sanction}'", level="INFO")
        return DocumentMetadata(
            stop_num,
            self.document_name,
            self.hypothesis,
            self.disposition,
            self.sanction
        )

    def parse(self, body: list[str], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга документа с jump={jump}, строки: {body}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.create, Token.document, document_name, Token.start_body]:
                    self.document_name = document_name
                    printer.logging(f"Найдена секция 'create document' с document_name='{document_name}'", level="INFO")
                case [Token.disposition, Token.start_body]:
                    printer.logging("Начало секции 'disposition'", level="INFO")
                    meta = self.execute_parse(DefineDispositionParser, body, num)
                    self.disposition = meta
                    printer.logging("Секция 'disposition' успешно распознана.", level="INFO")
                case [Token.sanction, Token.start_body]:
                    printer.logging("Начало секции 'sanction'", level="INFO")
                    meta = self.execute_parse(DefineSanctionParser, body, num)
                    self.sanction = meta
                    printer.logging("Секция 'sanction' успешно распознана.", level="INFO")
                case [Token.hypothesis, Token.start_body]:
                    printer.logging("Начало секции 'hypothesis'", level="INFO")
                    meta = self.execute_parse(DefineHypothesisParser, body, num)
                    self.hypothesis = meta
                    printer.logging("Секция 'hypothesis' успешно распознана.", level="INFO")
                case [Token.end_body]:
                    printer.logging("Парсинг документа завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line)

        printer.logging("Парсинг документа завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
