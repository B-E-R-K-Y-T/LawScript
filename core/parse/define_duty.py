from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.line import Line
from core.types.obligations import Obligation
from core.util import is_ignore_line
from util.console_worker import printer


class DefineDutyMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, description: str):
        super().__init__(stop_num)
        self.name = name
        self.description = description
        printer.logging(f"Создано DefineDutyMetadata с stop_num={stop_num}, name={name}, description={description}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа Obligation с name={self.name}, description={self.description}", level="INFO")
        return Image(
            name=self.name,
            obj=Obligation,
            image_args=(self.description,)
        )


class DefineDutyParser(Parser):
    def __init__(self):
        self.name_obligation: Optional[str] = None
        self.description: Optional[str] = None
        printer.logging("Инициализация DefineDutyParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных DefineDuty с stop_num={stop_num}, name={self.name_obligation}, description={self.description}", level="INFO")
        return DefineDutyMetaObject(
            stop_num,
            name=self.name_obligation,
            description=self.description,
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineDuty с jump={jump} {Obligation.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.duty, name_obligation, Tokens.left_bracket]:
                    self.name_obligation = name_obligation
                    printer.logging(f"Обнаружено определение обязанности: {self.name_obligation}", level="INFO")
                case [Tokens.description, *description, Tokens.comma]:
                    self.description = " ".join(description)
                    printer.logging(f"Добавлено описание обязанности: {self.description}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг обязанности завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг обязанности завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
