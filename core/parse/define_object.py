from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.objects import Object
from core.util import is_ignore_line
from util.console_worker import printer


class DefineObjectMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, name_object: str):
        super().__init__(stop_num)
        self.name = name
        self.name_object = name_object
        printer.logging(f"Создано DefineObjectMetadata с stop_num={stop_num}, name={name}, name_object={name_object}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа Object с name={self.name}, name_object={self.name_object}", level="INFO")
        return Image(
            name=self.name,
            obj=Object,
            image_args=(self.name_object,)
        )


class DefineObjectParser(Parser):
    def __init__(self):
        self.name_object_define: Optional[str] = None
        self.name_object: Optional[str] = None
        printer.logging("Инициализация DefineObjectParser", level="INFO")

    def create_metadata(self, stop_num: int) -> Metadata:
        printer.logging(f"Создание метаданных Object с stop_num={stop_num}, name_object_define={self.name_object_define}, name_object={self.name_object}", level="INFO")
        return DefineObjectMetadata(
            stop_num,
            name=self.name_object_define,
            name_object=self.name_object,
        )

    def parse(self, body: list[str], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineObject с jump={jump}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.define, Token.object, name_object, Token.start_body]:
                    self.name_object_define = name_object
                    printer.logging(f"Обнаружено определение объекта: {self.name_object_define}", level="INFO")
                case [Token.name, *name_object, Token.comma]:
                    self.name_object = " ".join(name_object)
                    printer.logging(f"Добавлено имя объекта: {self.name_object}", level="INFO")
                case [Token.end_body]:
                    printer.logging("Парсинг объекта завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line)

        printer.logging("Парсинг объекта завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
