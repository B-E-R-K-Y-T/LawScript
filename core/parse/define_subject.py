from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.line import Line
from core.types.subjects import Subject
from core.util import is_ignore_line
from util.console_worker import printer


class DefineSubjectMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, name_subject: str):
        super().__init__(stop_num)
        self.name = name
        self.name_subject = name_subject
        printer.logging(f"Создано DefineSubjectMetadata с stop_num={stop_num}, name={name}, name_subject={name_subject}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа Subject с name={self.name}, name_subject={self.name_subject}", level="INFO")
        return Image(
            name=self.name,
            obj=Subject,
            image_args=(self.name_subject,)
        )


class DefineSubjectParser(Parser):
    def __init__(self):
        self.name_subject_define: Optional[str] = None
        self.name_subject: Optional[str] = None
        printer.logging("Инициализация DefineSubjectParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных Subject с stop_num={stop_num}, name_subject_define={self.name_subject_define}, name_subject={self.name_subject}", level="INFO")
        return DefineSubjectMetaObject(
            stop_num,
            name=self.name_subject_define,
            name_subject=self.name_subject,
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineSubject с jump={jump} {Subject.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="DEBUG")
                continue

            info = line.get_file_info()
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
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг субъекта завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
