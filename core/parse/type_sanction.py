from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.types.line import Line, Info
from core.types.sanction_types import SanctionType
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.util import is_ignore_line
from util.console_worker import printer


class TypeSanctionMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, info: Info, *args):
        super().__init__(stop_num)
        self.name = name
        self.info = info
        self.args = args
        printer.logging(f"Создано TypeSanctionMetadata: stop_num={stop_num}, name={name}, args={args}", level="INFO")

    def create_image(self):
        printer.logging(f"Создание образа SanctionType: name={self.name}, args={self.args}", level="INFO")
        return Image(
            name=self.name,
            obj=SanctionType,
            image_args=self.args,
            info=self.info
        )


class TypeSanctionParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name_sanction_type: Optional[str] = None
        self.article: Optional[str] = None
        self.name: Optional[str] = None
        printer.logging("Инициализация TypeSanctionParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных TypeSanction: stop_num={stop_num}, name={self.name}, "
                        f"name_sanction_type={self.name_sanction_type}, article={self.article}", level="INFO")
        return TypeSanctionMetaObject(
            stop_num,
            self.name,
            self.info,
            self.name_sanction_type,
            self.article
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга TypeSanction с jump={jump} {SanctionType.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="DEBUG")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.of_sanction, name, Tokens.left_bracket]:
                    self.name_sanction_type = name
                    self.name = name
                    printer.logging(f"Определен тип санкции: {self.name_sanction_type}", level="INFO")
                case [Tokens.article, *article, Tokens.comma]:
                    self.article = self.parse_sequence_words_to_str(article)
                    printer.logging(f"Добавлена статья: {self.article}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг типа санкции завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг типа санкции завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
