from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.types.sanction_types import SanctionType
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.util import is_ignore_line
from util.console_worker import printer


class TypeSanctionMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, *args):
        super().__init__(stop_num)
        self.name = name
        self.args = args
        printer.logging(f"Создано TypeSanctionMetadata: stop_num={stop_num}, name={name}, args={args}", level="INFO")

    def create_image(self):
        printer.logging(f"Создание образа SanctionType: name={self.name}, args={self.args}", level="INFO")
        return Image(
            name=self.name,
            obj=SanctionType,
            image_args=self.args
        )


class TypeSanctionParser(Parser):
    def __init__(self):
        self.name_sanction_type: Optional[str] = None
        self.article: Optional[str] = None
        self.name: Optional[str] = None
        printer.logging("Инициализация TypeSanctionParser", level="INFO")

    def create_metadata(self, stop_num: int) -> Metadata:
        printer.logging(f"Создание метаданных TypeSanction: stop_num={stop_num}, name={self.name}, "
                        f"name_sanction_type={self.name_sanction_type}, article={self.article}", level="INFO")
        return TypeSanctionMetadata(
            stop_num,
            self.name,
            self.name_sanction_type,
            self.article
        )

    def parse(self, body: list[str], jump: int) -> int:
        printer.logging(f"Начало парсинга TypeSanction с jump={jump}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="DEBUG")
                continue

            line = self.separate_line_to_token(line)

            match line:
                case [Token.define, Token.of_sanction, name, Token.start_body]:
                    self.name_sanction_type = name
                    self.name = name
                    printer.logging(f"Определен тип санкции: {self.name_sanction_type}", level="INFO")
                case [Token.article, *article, Token.comma]:
                    self.article = self.parse_many_word_to_str(article)
                    printer.logging(f"Добавлена статья: {self.article}", level="INFO")
                case [Token.end_body]:
                    printer.logging("Парсинг типа санкции завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line)

        printer.logging("Парсинг типа санкции завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
