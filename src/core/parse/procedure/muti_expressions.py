from src.core.exceptions import InvalidSyntaxError
from src.core.parse.base import MetaObject, Image, Parser
from src.core.tokens import Tokens
from src.core.types.line import Line, Info
from src.core.types.procedure import Body, Expression
from src.core.util import is_ignore_line
from src.util.console_worker import printer


class MultiExpressionMetaObject(MetaObject):
    def __init__(
            self, stop_num: int, name: str,
            expressions: list[str], info: Info
    ):
        super().__init__(stop_num)
        self.name = name
        self.expressions = expressions
        self.info = info

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Expression,
            image_args=(self.expressions, self.info),
            info=self.info
        )


class MultiExpressionParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.expressions: list[str] = []
        printer.logging("Инициализация MultiExpressionParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MultiExpressionMetaObject:
        printer.logging(
            f"Создание метаданных выражений с stop_num={stop_num}, commands={self.expressions}", level="INFO"
        )
        return MultiExpressionMetaObject(
            stop_num,
            name=str(id(self)),
            expressions=self.expressions,
            info=self.info
        )

    def clean_comma(self):
        if len(self.expressions) and self.expressions[-1] == Tokens.comma:
            self.expressions.pop(-1)

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга выражений с jump={self.jump} {Body.__name__}", level="INFO")

        left_bracket, right_bracket = 1, 0

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
                case [*_, Tokens.left_bracket]:
                    left_bracket += 1
                    self.expressions.extend(line)

                case [*expr, Tokens.right_bracket, Tokens.comma]:
                    right_bracket += 1
                    printer.logging(f"Найдена ')', с запятой. right={right_bracket}, left={left_bracket}",
                                    level="DEBUG")

                    self.clean_comma()
                    self.expressions.extend([*expr, Tokens.right_bracket])

                    if right_bracket == left_bracket:
                        return num

                case [*expr, Tokens.comma]:
                    self.expressions.extend([*expr, Tokens.comma])

                case [*expr, Tokens.right_bracket]:
                    right_bracket += 1
                    printer.logging(f"Найдена ')' без запятой. right={right_bracket}, left={left_bracket}, expr={expr}",
                                    level="DEBUG")

                    self.clean_comma()
                    self.expressions.extend([*expr, Tokens.right_bracket])
                    if right_bracket == left_bracket:
                        printer.logging("Парсинг выражений завершен: 'right_bracket' найден", level="INFO")
                        return num

                case [*expr, Tokens.right_bracket, Tokens.end_expr]:
                    self.clean_comma()
                    self.expressions.extend([*expr, Tokens.right_bracket])

                    printer.logging("Парсинг выражений завершен: 'right_bracket' найден", level="INFO")
                    return num

                case [*expr, Tokens.end_expr]:
                    self.clean_comma()
                    self.expressions.extend(expr)
                    printer.logging("Парсинг выражений завершен: 'end_expr' найден", level="INFO")
                    return num

                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг выражений с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError(info=self.info)
