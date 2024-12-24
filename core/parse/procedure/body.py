from typing import Union

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser
from core.tokens import Tokens
from core.types.basetype import BaseType
from core.types.line import Line
from core.types.procedure import Body, AssignField, Expression, When, Loop, Print, Else, Return
from core.util import is_ignore_line
from util.console_worker import printer


class DefineBodyMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, commands: list[Union[MetaObject, BaseType]]):
        super().__init__(stop_num)
        self.name = name
        self.commands = commands

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Body,
            image_args=(self.commands,)
        )


class BodyParser(Parser):
    def __init__(self):
        super().__init__()
        self.commands: list[Union[MetaObject, BaseType]] = []
        printer.logging("Инициализация BodyParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных тела с stop_num={stop_num}, commands={self.commands}", level="INFO")
        return DefineBodyMetaObject(
            stop_num,
            name=str(id(self)),
            commands=self.commands
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

            info = line.get_file_info()
            line = self.separate_line_to_token(line)
            printer.logging(f"Парсинг строки: {line}", level="INFO")

            match line:
                case [Tokens.print_, *expr, Tokens.end_expr]:
                    self.commands.append(Print(str(), Expression(str(), expr)))
                    printer.logging(f"Добавлена команда Print с выражением: {expr}", level="INFO")
                case [Tokens.else_, Tokens.left_bracket]:
                    err_msg = f"Перед '{Tokens.else_}' всегда должен быть блок '{Tokens.when}'"

                    if not self.commands:
                        raise InvalidSyntaxError(err_msg, line=line, info=info)

                    if not isinstance(self.commands[len(self.commands) - 1], When):
                        raise InvalidSyntaxError(err_msg, line=line, info=info)

                    self.commands.append(Else(str(), self.execute_parse(BodyParser, body, self.next_num_line(num))))
                    printer.logging("Добавлена команда Else", level="INFO")
                case [Tokens.assign, name, Tokens.equal, *expr, Tokens.end_expr]:
                    self.commands.append(AssignField(name, Expression(str(), expr)))
                    printer.logging(f"Добавлена команда AssignField с именем: {name} и выражением: {expr}",
                                    level="INFO")
                case [Tokens.when, *expr, Tokens.then, Tokens.left_bracket]:
                    when_body = self.execute_parse(BodyParser, body, self.next_num_line(num))
                    else_ = None

                    if body[self.jump].startswith(Tokens.else_):
                        else_ = self.execute_parse(BodyParser, body, self.next_num_line(num))

                    self.commands.append(
                        When(
                            str(), Expression(str(), expr), when_body, else_
                        )
                    )
                    printer.logging("Добавлена команда When", level="INFO")
                case [Tokens.loop, Tokens.from_, *expr, Tokens.left_bracket]:
                    expr = list(expr)

                    # Проверяю, что в подстроке: "a ДО b" строки: "ЦИКЛ ОТ a ДО b (" "ДО" встречается только 1 раз
                    if expr.count(Tokens.to) != 1:
                        raise InvalidSyntaxError(
                            f"Оператор '{Tokens.to}' должен встречаться в определении цикла только 1 раз!",
                            line=line,
                            info=info
                        )

                    sep_idx = expr.index(Tokens.to)
                    start_expr = expr[:sep_idx]
                    end_expr = expr[sep_idx + 1:]

                    self.commands.append(
                        Loop(
                            str(), Expression(str(), start_expr), Expression(str(), end_expr),
                            self.execute_parse(BodyParser, body, self.next_num_line(num))
                        )
                    )
                    printer.logging("Добавлена команда Loop", level="INFO")
                case [Tokens.return_, *expr, Tokens.end_expr]:
                    self.commands.append(Return(str(), Expression(str(), expr)))
                    printer.logging(f"Добавлена команда Return с выражением: {expr}", level="INFO")
                    return self.next_num_line(num)
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг тела завершен: 'right_bracket' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг тела завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
