from typing import Optional

from src.core.exceptions import InvalidSyntaxError
from src.core.parse.base import Parser, MetaObject, Image
from src.core.tokens import Tokens
from src.core.types.laws import Law
from src.core.types.line import Line, Info
from src.core.util import is_ignore_line
from src.util.console_worker import printer


class DefineLawMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, name_law: str, description: str, info: Info):
        super().__init__(stop_num)
        self.name = name
        self.name_law = name_law
        self.description = description
        self.info = info
        printer.logging(f"Создано DefineLawMetadata с stop_num={stop_num}, name={name}, name_law={name_law}, description={description}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа Law с name={self.name}, description={self.description}", level="INFO")
        return Image(
            name=self.name,
            obj=Law,
            image_args=(self.description,),
            info=self.info
        )


class DefineLawParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name: Optional[str] = None
        self.name_law: Optional[str] = None
        self.description: Optional[str] = None
        printer.logging("Инициализация DefineLawParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных Law с stop_num={stop_num}, name={self.name}, name_law={self.name_law}, description={self.description}", level="INFO")
        return DefineLawMetaObject(
            stop_num,
            name=self.name,
            name_law=self.name_law,
            description=self.description,
            info=self.info
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineLaw с jump={jump} {Law.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.law, name_law, Tokens.left_bracket]:
                    self.name_law = name_law
                    self.name = name_law
                    printer.logging(f"Обнаружено определение закона: {self.name_law}", level="INFO")
                case [Tokens.description, *description, Tokens.comma]:
                    self.description = " ".join(description)
                    printer.logging(f"Добавлено описание закона: {self.description}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг закона завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг закона завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
