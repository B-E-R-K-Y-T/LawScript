from typing import Union

from numba.core.target_extension import target_override

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser, is_identifier
from core.parse.procedure.define import DefineProcedureParser
from core.tokens import Tokens, NOT_ALLOWED_TOKENS
from core.types.basetype import BaseType
from core.types.line import Line, Info
from core.types.procedure import Body, AssignField, Expression, When, Loop, Print, Else, Return, Continue, Break, \
    AssignOverrideVariable, While
from core.util import is_ignore_line
from util.console_worker import printer


class DefineBodyMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, commands: list[Union[MetaObject, BaseType]], info: Info):
        super().__init__(stop_num)
        self.name = name
        self.commands = commands
        self.info = info

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Body,
            image_args=(self.commands,),
            info=self.info
        )


class TableBodyParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.commands: list[Union[MetaObject, BaseType]] = []
        printer.logging("Инициализация BodyParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных тела с stop_num={stop_num}, commands={self.commands}", level="INFO")
        return DefineBodyMetaObject(
            stop_num,
            name=str(id(self)),
            commands=self.commands,
            info=self.info
        )

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга тела с jump={self.jump} {Body.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)
            printer.logging(f"Парсинг строки: {line}", level="INFO")

            match line:
                case [Tokens.assign, name, Tokens.equal, *expr, Tokens.end_expr]:
                    if not is_identifier(name):
                        raise InvalidSyntaxError(
                            f"Имя переменной должно состоять только из букв и цифр! Переменная: {name}",
                            line=line,
                            info=self.info
                        )

                    if name in NOT_ALLOWED_TOKENS:
                        raise InvalidSyntaxError(
                            f"Неверный синтаксис. Нельзя использовать операторы в выражениях: {name}",
                            info=self.info
                        )

                    self.commands.append(AssignField(name, Expression(str(), expr, self.info), self.info))
                    printer.logging(f"Добавлена команда AssignField с именем: {name} и выражением: {expr}",
                                    level="INFO")
                case [Tokens.define, Tokens.a_procedure, *_]:
                    self.commands.append(self.execute_parse(DefineProcedureParser, body, num))
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг тела завершен: 'right_bracket' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг тела завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
