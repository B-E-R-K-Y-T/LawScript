from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.classes import ClassDefinition
from core.types.line import Line, Info
from core.util import is_ignore_line
from util.console_worker import printer


class DefineClassMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, name_subject: str, info: Info):
        super().__init__(stop_num)
        self.name = name
        self.name_subject = name_subject
        self.info = info

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=ClassDefinition,
            image_args=(self.name_subject,),
            info=self.info,
        )


class DefineClassParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name_subject_define: Optional[str] = None
        self.name_subject: Optional[str] = None

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DefineClassMetaObject(
            stop_num,
            name=self.name_subject_define,
            name_subject=self.name_subject,
            info=self.info,
        )

    def parse(self, body: list[Line], jump: int) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="DEBUG")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.subject, name_subject, Tokens.left_bracket]:
                    self.name_subject_define = name_subject
                    printer.logging(f"Обнаружено определение субъекта: {self.name_subject_define}", level="INFO")
                case [Tokens.name, *name_subject, Tokens.comma]:
                    self.name_subject = self.parse_sequence_words_to_str(name_subject)
                    printer.logging(f"Добавлено имя субъекта: {self.name_subject}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг субъекта завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг субъекта завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
