from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser, is_identifier
from core.parse.procedure.body import BodyParser
from core.tokens import Tokens, NOT_ALLOWED_TOKENS
from core.types.line import Line, Info
from core.types.procedure import Procedure, Expression
from core.types.variable import Variable
from core.util import is_ignore_line
from util.console_worker import printer


class DefineProcedureMetaObject(MetaObject):
    def __init__(
            self, stop_num: int, name: str, body: Optional[MetaObject],
            arguments_name: list[Optional[str]], info: Info, default_arguments: Optional[dict[str, Expression]]
    ):
        super().__init__(stop_num)
        self.name = name
        self.body = body
        self.arguments_name = arguments_name
        self.default_arguments = default_arguments
        self.info = info

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Procedure,
            image_args=(self.body, self.arguments_name, self.default_arguments),
            info=self.info
        )


class DefineProcedureParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.procedure_name: Optional[str] = None
        self.arguments_name: list[Optional[str]] = []
        self.default_arguments: Optional[dict[str, Expression]] = None
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
            default_arguments=self.default_arguments,
            info=self.info
        )

    def parse_args(self, arguments, info_line: Info) -> None:
        printer.logging(f"Начало парсинга аргументов: {arguments}", level="DEBUG")

        required_arguments = []
        default_arguments = []
        default_arguments_expressions = []

        printer.logging(f"Исходные аргументы: {arguments}", level="DEBUG")

        for offset, argument_token in enumerate(arguments):
            printer.logging(f"Обработка токена [{offset}]: '{argument_token}'", level="DEBUG")

            if argument_token == Tokens.equal and offset > 0:
                printer.logging(f"Найден аргумент с значением по умолчанию на позиции {offset}", level="DEBUG")
                required_arguments.pop(-1)
                default = arguments[offset - 1:]
                printer.logging(f"Выделена часть для обработки значений по умолчанию: {default}", level="DEBUG")

                for default_offset, default_argument_token in enumerate(default):
                    printer.logging(f"Обработка default токена [{default_offset}]: '{default_argument_token}'",
                                    level="DEBUG")

                    if default_argument_token == Tokens.equal and default_offset > 0:
                        name = default[default_offset - 1]
                        default_arguments.append(name)
                        printer.logging(f"Добавлен аргумент с default: {name}", level="DEBUG")

                        if default_arguments_expressions:
                            comma_index = default_arguments_expressions[-1].rfind(Tokens.comma)
                            default_arguments_expressions[-1] = default_arguments_expressions[-1][:comma_index]
                            printer.logging(f"Обрезано выражение после запятой: {default_arguments_expressions[-1]}",
                                            level="DEBUG")

                        default_arguments_expressions.append("")
                        printer.logging("Создан новый буфер для выражения", level="DEBUG")
                        continue

                    if default_arguments_expressions:
                        default_arguments_expressions[-1] += default_argument_token + " "
                        printer.logging(
                            f"Добавлено в выражение: '{default_argument_token}', текущее: '{default_arguments_expressions[-1]}'",
                            level="DEBUG")

                if default_arguments_expressions:
                    for expr in default_arguments_expressions:
                        if not expr:
                            printer.logging("Пустое выражение для аргумента по умолчанию", level="ERROR")
                            raise InvalidSyntaxError("Ошибка в аргументах по умолчанию.", info=info_line)
                    printer.logging(f"Проверка выражений завершена: {default_arguments_expressions}", level="DEBUG")

                break

            if argument_token != Tokens.comma:
                required_arguments.append(argument_token)
                printer.logging(f"Добавлен обязательный аргумент: '{argument_token}'", level="DEBUG")

        default_arguments_names_values = {}
        printer.logging(f"Обязательные аргументы: {required_arguments}", level="INFO")
        printer.logging(f"Аргументы с default: {default_arguments}", level="INFO")
        printer.logging(f"Выражения для default: {default_arguments_expressions}", level="INFO")

        for offset, expr in enumerate(default_arguments_expressions):
            expr += Tokens.end_expr
            default_arguments_expressions[offset] = expr
            printer.logging(f"Добавлен end_expr к выражению [{offset}]: '{expr}'", level="DEBUG")

        if len(default_arguments_expressions) == len(default_arguments):
            for name, expression in zip(default_arguments, default_arguments_expressions):
                printer.logging(f"Создание Expression для '{name}': '{expression}'", level="DEBUG")
                expr = Expression(
                    name, self.separate_line_to_token(Line(expression, info_line.num)), info_line
                )
                expr.raw_operations = expr.raw_operations[:-1]
                default_arguments_names_values[name] = expr
                printer.logging(f"Создан Expression для аргумента '{name}'", level="DEBUG")
        else:
            printer.logging(
                f"Несоответствие количества аргументов и выражений: args={len(default_arguments)}, exprs={len(default_arguments_expressions)}",
                level="ERROR"
            )
            raise InvalidSyntaxError("Ошибка в аргументах по умолчанию", info=info_line)

        arguments = required_arguments + default_arguments
        printer.logging(f"Объединенный список аргументов: {arguments}", level="INFO")

        previous_arg = ""

        for offset, arg_name in enumerate(arguments):
            current_arg = arguments[offset]
            printer.logging(f"Проверка уникальности аргумента [{offset}]: '{arg_name}'", level="DEBUG")

            if current_arg == previous_arg:
                printer.logging(f"Обнаружен дубликат аргумента: '{arg_name}'", level="ERROR")
                raise InvalidSyntaxError(
                    f"Неверный синтаксис. Аргументы не могут использовать одно и то же имя: '{arg_name}'",
                    info=info_line
                )

            previous_arg = arg_name

        for name, expr in default_arguments_names_values.items():
            if self.default_arguments is None:
                self.default_arguments = {}
                printer.logging("Инициализация словаря default_arguments", level="DEBUG")

            if not is_identifier(name):
                printer.logging(f"Некорректное имя аргумента: '{name}'", level="ERROR")
                raise InvalidSyntaxError(f"Неверный синтаксис. Неверное имя аргумента: {name}", info=info_line)

            self.default_arguments[name] = expr
            printer.logging(f"Добавлен default аргумент: '{name}' = '{expr}'", level="DEBUG")

        if not all(arguments):
            self.arguments_name = []
            printer.logging("Список аргументов пуст", level="DEBUG")
        else:
            self.arguments_name = arguments
            printer.logging(f"Финальный список аргументов: {self.arguments_name}", level="INFO")

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга процедуры с jump={self.jump} {Procedure.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            if self.info is None:
                self.info = line.get_file_info()

            info_line = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.a_procedure, name_condition, Tokens.left_bracket, *arguments, Tokens.right_bracket, Tokens.left_bracket]:
                    self.parse_args(arguments, info_line)

                    for arg in self.arguments_name:
                        if arg in NOT_ALLOWED_TOKENS or not is_identifier(arg):
                            raise InvalidSyntaxError(
                                f"Неверный синтаксис. Нельзя использовать операторы в объявлениях аргументов: {arg}",
                                info=info_line
                            )

                    self.procedure_name = name_condition
                    self.body = self.execute_parse(BodyParser, body, self.next_num_line(num))
                    self.jump = self.previous_num_line(self.jump)

                    printer.logging(
                        f"Добавлена процедура: name={self.procedure_name}, arguments_name={self.arguments_name}",
                        level="INFO"
                    )
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг процедуры завершен: 'right_bracket' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info_line)

        printer.logging("Парсинг процедуры завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
