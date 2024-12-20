from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.hypothesis import Hypothesis
from core.util import is_ignore_line
from util.console_worker import printer


class HypothesisMetadata(Metadata):
    def __init__(self, stop_num: int, *args):
        super().__init__(stop_num)
        self.args = args
        printer.logging(f"Создано HypothesisMetadata с stop_num={stop_num}, args={args}", level="INFO")

    def create_image(self):
        printer.logging(f"Создание образа Hypothesis с args={self.args}", level="INFO")
        return Image(
            name=str(id(self)),
            obj=Hypothesis,
            image_args=self.args
        )


class DefineHypothesisParser(Parser):
    def __init__(self):
        self.subject: Optional[str] = None
        self.object: Optional[str] = None
        self.condition: Optional[str] = None
        printer.logging("Инициализация DefineHypothesisParser", level="INFO")

    def create_metadata(self, stop_num: int) -> Metadata:
        printer.logging(f"Создание метаданных Hypothesis с stop_num={stop_num}, subject={self.subject}, object={self.object}, condition={self.condition}", level="INFO")
        return HypothesisMetadata(
            stop_num,
            self.subject,
            self.object,
            self.condition
        )

    def parse(self, body: list[str], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineHypothesis с jump={jump}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.hypothesis, Token.start_body]:
                    printer.logging("Обнаружено начало гипотезы", level="INFO")
                case [Token.subject, subject, Token.comma]:
                    self.subject = subject
                    printer.logging(f"Добавлен субъект гипотезы: {self.subject}", level="INFO")
                case [Token.object, object, Token.comma]:
                    self.object = object
                    printer.logging(f"Добавлен объект гипотезы: {self.object}", level="INFO")
                case [Token.condition, condition, Token.comma]:
                    self.condition = condition
                    printer.logging(f"Добавлено условие гипотезы: {self.condition}", level="INFO")
                case [Token.end_body]:
                    printer.logging("Парсинг гипотезы завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line)

        printer.logging("Парсинг гипотезы завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
