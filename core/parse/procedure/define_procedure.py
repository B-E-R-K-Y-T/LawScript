from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser
from core.parse.procedure.body import BodyParser
from core.tokens import Tokens
from core.types.atomic import Void
from core.types.line import Line, Info
from core.types.procedure import Procedure
from core.util import is_ignore_line
from util.console_worker import printer


class DefineProcedureMetaObject(MetaObject):
    def __init__(
            self, stop_num: int, name: str, body: Optional[MetaObject], arguments_name: list[Optional[str]], info: Info
    ):
        super().__init__(stop_num)
        self.name = name
        self.body = body
        self.arguments_name = arguments_name
        self.info = info

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Procedure,
            image_args=(self.body, self.arguments_name),
            info=self.info
        )


class DefineProcedureParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.procedure_name: Optional[str] = None
        self.arguments_name: list[Optional[str]] = []
        self.body: Optional[MetaObject] = None
        printer.logging("Инициализация DefineProcedureParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(
            f"Создание метаданных процедуры с stop_num={stop_num}, name={self.procedure_name}, body={self.body}, arguments_name={self.arguments_name}",
            level="INFO")
        return DefineProcedureMetaObject(
            stop_num,
            name=self.procedure_name,
            body=self.body,
            arguments_name=self.arguments_name,
            info=self.info
        )

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга процедуры с jump={self.jump} {Procedure.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.a_procedure, name_condition, Tokens.left_bracket, *arguments, Tokens.right_bracket, Tokens.left_bracket]:
                    arguments = "".join(arguments).split(Tokens.comma)
                    if not all(arguments):
                        self.arguments_name = []
                    else:
                        self.arguments_name = arguments

                    self.procedure_name = name_condition
                    self.body = self.execute_parse(BodyParser, body, self.next_num_line(num))
                    self.jump = self.previous_num_line(self.jump)
                    printer.logging(
                        f"Добавлена процедура: name={self.procedure_name}, arguments_name={self.arguments_name}",
                        level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг процедуры завершен: 'right_bracket' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг процедуры завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
