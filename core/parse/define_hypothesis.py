from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.hypothesis import Hypothesis
from core.types.line import Line, Info
from core.util import is_ignore_line
from util.console_worker import printer


class HypothesisMetaObject(MetaObject):
    def __init__(self, stop_num: int, info: Info, *args):
        super().__init__(stop_num)
        self.info = info
        self.args = args
        printer.logging(f"Создано HypothesisMetadata с stop_num={stop_num}, args={args}", level="INFO")

    def create_image(self):
        printer.logging(f"Создание образа Hypothesis с args={self.args}", level="INFO")
        return Image(
            name=str(id(self)),
            obj=Hypothesis,
            image_args=self.args,
            info=self.info
        )


class DefineHypothesisParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.subject: Optional[str] = None
        self.object: Optional[str] = None
        self.condition: Optional[str] = None
        printer.logging("Инициализация DefineHypothesisParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных Hypothesis с stop_num={stop_num}, subject={self.subject}, object={self.object}, condition={self.condition}", level="INFO")
        return HypothesisMetaObject(
            stop_num,
            self.info,
            self.subject,
            self.object,
            self.condition
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineHypothesis с jump={jump} {Hypothesis.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.hypothesis, Tokens.left_bracket]:
                    printer.logging("Обнаружено начало гипотезы", level="INFO")
                case [Tokens.subject, subject, Tokens.comma]:
                    self.subject = subject
                    printer.logging(f"Добавлен субъект гипотезы: {self.subject}", level="INFO")
                case [Tokens.object, object, Tokens.comma]:
                    self.object = object
                    printer.logging(f"Добавлен объект гипотезы: {self.object}", level="INFO")
                case [Tokens.condition, condition, Tokens.comma]:
                    self.condition = condition
                    printer.logging(f"Добавлено условие гипотезы: {self.condition}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг гипотезы завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг гипотезы завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
