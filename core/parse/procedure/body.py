from typing import Union

from numba.core.target_extension import target_override

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser, is_identifier
from core.tokens import Tokens, NOT_ALLOWED_TOKENS
from core.types.basetype import BaseType
from core.types.line import Line, Info
from core.types.procedure import Body, AssignField, Expression, When, Loop, Print, Else, Return, Continue, Break, \
    AssignOverrideVariable, While, ElseWhen
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


class BodyParser(Parser):
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

    def parse_loop(self, expr, line: list[str], body: list[Line], num: int) -> Loop:
        expr = list(expr)

        # Проверяю, что в подстроке: "a ДО b" строки: "ЦИКЛ ОТ a ДО b (" "ДО" встречается только 1 раз
        if expr.count(Tokens.to) != 1:
            raise InvalidSyntaxError(
                f"Оператор '{Tokens.to}' должен встречаться в определении цикла только 1 раз!",
                line=line,
                info=self.info
            )

        sep_idx = expr.index(Tokens.to)
        start_expr = expr[:sep_idx]
        end_expr = expr[sep_idx + 1:]

        loop = Loop(
            str(), Expression(str(), start_expr, self.info), Expression(str(), end_expr, self.info),
            self.execute_parse(BodyParser, body, self.next_num_line(num))
        )
        loop.set_info(self.info)

        return loop

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
                case [Tokens.print_, *expr, Tokens.end_expr]:
                    self.commands.append(Print(str(), Expression(str(), expr, self.info)))
                    printer.logging(f"Добавлена команда Print с выражением: {expr}", level="INFO")
                case [Tokens.else_, Tokens.left_bracket]:
                    err_msg = f"Перед '{Tokens.else_}' всегда должен быть блок '{Tokens.when}'"

                    if not self.commands:
                        raise InvalidSyntaxError(err_msg, line=line, info=self.info)

                    previous_command = self.commands[len(self.commands) - 1]

                    if (
                            not isinstance(previous_command, When) and
                            not isinstance(previous_command, ElseWhen)
                    ):
                        raise InvalidSyntaxError(err_msg, line=line, info=self.info)

                    if isinstance(previous_command, When) and previous_command.else_ is not None:
                        raise InvalidSyntaxError(err_msg, line=line, info=self.info)

                    self.commands.append(Else(str(), self.execute_parse(BodyParser, body, self.next_num_line(num))))
                    printer.logging("Добавлена команда Else", level="INFO")
                case [Tokens.else_, Tokens.when, *expr, Tokens.then, Tokens.left_bracket]:
                    err_msg = (
                        f"Перед '{Tokens.else_} {Tokens.when}' "
                        f"всегда должен быть блок '{Tokens.when}' или '{Tokens.else_} {Tokens.when}'"
                    )

                    if not self.commands:
                        raise InvalidSyntaxError(err_msg, line=line, info=self.info)

                    previous_command = self.commands[len(self.commands) - 1]

                    if (
                            not isinstance(previous_command, When) and
                            not isinstance(previous_command, ElseWhen)
                    ):
                        raise InvalidSyntaxError(err_msg, line=line, info=self.info)

                    if isinstance(previous_command, When) and previous_command.else_ is not None:
                        raise InvalidSyntaxError(err_msg, line=line, info=self.info)

                    self.commands.append(
                        ElseWhen(
                            str(), Expression(str(), expr, self.info),
                            self.execute_parse(BodyParser, body, self.next_num_line(num))
                        )
                    )
                    printer.logging("Добавлена команда ElseWhen", level="INFO")
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
                case [Tokens.when, *expr, Tokens.then, Tokens.left_bracket]:
                    when_body = self.execute_parse(BodyParser, body, self.next_num_line(num))
                    else_ = None
                    else_whens = []
                    right_brackets = 0

                    for num_, line_ in enumerate(body[self.jump:]):
                        if is_ignore_line(line_):
                            continue

                        tokens = self.separate_line_to_token(line_)

                        match tokens:
                            case [Tokens.else_, Tokens.left_bracket]:
                                break

                            case [Tokens.when, *_, Tokens.then, Tokens.left_bracket]:
                                break

                            case [Tokens.right_bracket]:
                                right_brackets += 1

                                if right_brackets == 2:
                                    break

                            case [Tokens.else_, Tokens.when, *expr_, Tokens.then, Tokens.left_bracket]:
                                body_else_when = self.execute_parse(BodyParser, body, self.next_num_line(self.jump))
                                else_whens.append(
                                        ElseWhen(
                                        str(), Expression(str(), expr_, self.info), body_else_when
                                    )
                                )

                            case _:
                                right_brackets = 0

                    if body[self.jump].startswith(Tokens.else_):
                        body_else_ = self.execute_parse(BodyParser, body, self.next_num_line(self.jump))
                        else_ = Else(str(), body_else_)

                    when = When(
                        str(), Expression(str(), expr, self.info), when_body, else_, else_whens
                    )
                    when.set_info(self.info)

                    self.commands.append(when)
                    printer.logging("Добавлена команда When", level="INFO")
                case [Tokens.while_, *expr, Tokens.left_bracket]:
                    self.commands.append(
                        While(
                            str(), Expression(str(), expr, self.info),
                            self.execute_parse(BodyParser, body, self.next_num_line(num))
                        )
                    )
                    printer.logging("Добавлена команда While", level="INFO")
                case [Tokens.loop, Tokens.from_, *expr, Tokens.left_bracket]:
                    loop = self.parse_loop(expr, line, body, num)

                    self.commands.append(loop)
                    printer.logging("Добавлена команда Loop", level="INFO")
                case [Tokens.loop, var_name, Tokens.from_, *expr, Tokens.left_bracket]:
                    if not is_identifier(var_name):
                        raise InvalidSyntaxError(
                            f"Имя переменной должно состоять только из букв и цифр! Переменная: {var_name}",
                            line=line,
                            info=self.info
                        )

                    if var_name in NOT_ALLOWED_TOKENS:
                        raise InvalidSyntaxError(
                            f"Неверный синтаксис. Нельзя использовать зарезервированные слова{var_name}",
                            info=self.info
                        )

                    loop = self.parse_loop(expr, line, body, num)

                    loop.name_loop_var = var_name
                    self.commands.append(loop)
                    printer.logging("Добавлена команда Loop", level="INFO")
                case [Tokens.return_, *expr, Tokens.end_expr]:
                    self.commands.append(Return(str(), Expression(str(), expr, self.info)))
                    printer.logging(f"Добавлена команда Return с выражением: {expr}", level="INFO")
                    return self.next_num_line(num)
                case [Tokens.continue_, Tokens.end_expr]:
                    self.commands.append(Continue(str(), self.info))
                    printer.logging(f"Добавлена команда Continue", level="INFO")
                case [Tokens.break_, Tokens.end_expr]:
                    self.commands.append(Break(str(), self.info))
                    printer.logging(f"Добавлена команда Break", level="INFO")
                case [*expr, Tokens.end_expr]:
                    if Tokens.equal in expr:
                        if expr.count(Tokens.equal) > 1:
                            raise InvalidSyntaxError(
                                f"Оператор '{Tokens.equal}' должен встречаться в определении выражения только 1 раз!",
                                line=line,
                                info=self.info
                            )

                        equal_idx = expr.index(Tokens.equal)
                        target, override = expr[:equal_idx], expr[equal_idx + 1:]

                        self.commands.append(
                            AssignOverrideVariable(
                                str(),
                                Expression(str(), target, self.info),
                                Expression(str(), override, self.info),
                                self.info
                            )
                        )
                        continue

                    self.commands.append(Expression(str(), expr, self.info))
                    printer.logging(f"Добавлена команда Expression с выражением: {expr}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг тела завершен: 'right_bracket' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг тела завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
