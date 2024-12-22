import re
from typing import Union

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser
from core.tokens import Tokens
from core.types.basetype import BaseType
from core.types.procedure import Body, AssignField, Expression, When, Loop, Print, Else, Return
from core.util import is_ignore_line


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

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DefineBodyMetaObject(
            stop_num,
            name=str(id(self)),
            commands=self.commands
        )

    def parse(self, body: list[str], jump) -> int:
        self.jump = jump

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.print_, *expr, Tokens.end_expr]:
                    self.commands.append(Print(str(), Expression(str(), expr)))
                case [Tokens.else_, Tokens.left_bracket]:
                    if not self.commands:
                        raise InvalidSyntaxError(line=line)

                    if not isinstance(self.commands[len(self.commands) - 1], When):
                        raise InvalidSyntaxError(line=line)

                    self.commands.append(Else(str(), self.execute_parse(BodyParser, body, self.next_num_line(num))))
                case [Tokens.assign, name, Tokens.equal, *expr, Tokens.end_expr]:
                    self.commands.append(AssignField(name, Expression(str(), expr)))
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
                case [Tokens.loop, Tokens.from_, *expr, Tokens.left_bracket]:
                    expr = list(expr)

                    # Проверяю, что в подстроке: "1 ДО 100" строки: "ЦИКЛ ОТ 1 ДО 100 (" "ДО" встречается только 1 раз
                    if expr.count(Tokens.to) != 1:
                        raise InvalidSyntaxError(line=line)

                    sep_idx = expr.index(Tokens.to)

                    start_expr = expr[:sep_idx]
                    end_expr = expr[sep_idx + 1:]

                    self.commands.append(
                        Loop(
                            str(), Expression(str(), start_expr), Expression(str(), end_expr),
                            self.execute_parse(BodyParser, body, self.next_num_line(num))
                        )
                    )
                case [Tokens.return_, *expr]:
                    self.commands.append(Return(str(), Expression(str(), expr)))
                    return self.next_num_line(num)
                case [Tokens.right_bracket]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
