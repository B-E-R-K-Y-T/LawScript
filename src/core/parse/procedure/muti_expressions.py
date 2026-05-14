from typing import Final

from src.core.exceptions import InvalidSyntaxError
from src.core.parse.base import MetaObject, Image, Parser
from src.core.tokens import Tokens, NOT_ALLOWED_TOKENS
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


_DEFAULT_LEFT_BRACKET: Final[int] = 1


class MultiExpressionParser(Parser):
    left_bracket = _DEFAULT_LEFT_BRACKET

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

    @classmethod
    def init_left_bracket(cls, expr: list[str]):
        cls.left_bracket = expr.count(Tokens.left_bracket)

    @classmethod
    def set_default_left_bracket(cls):
        cls.left_bracket = _DEFAULT_LEFT_BRACKET

    def clean_comma(self):
        if (
                len(self.expressions) > 1 and
                self.expressions[-2] == Tokens.comma and
                self.expressions[-1] == Tokens.right_bracket
        ):
            self.expressions.pop(-2)

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга выражений с jump={self.jump} {Body.__name__}", level="INFO")

        left_bracket, right_bracket = self.left_bracket, 0

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)
            printer.logging(f"Парсинг строки: {line}", level="INFO")

            is_string = False

            for offset, token in enumerate(line):
                if token == Tokens.quotation:
                    is_string = not is_string

                if is_string:
                    self.expressions.append(token)
                    continue

                if token in NOT_ALLOWED_TOKENS:
                    raise InvalidSyntaxError(
                        msg=f"Обнаружен недопустимый токен '{token}' в многострочном выражении.",
                        line=line, info=self.info
                    )

                if token == Tokens.right_bracket:
                    right_bracket += 1

                if token == Tokens.left_bracket:
                    left_bracket += 1

                if right_bracket == left_bracket:
                    # TODO: Подумать, как сделать более красиво
                    if offset + 2 < len(line):
                        expr = " ".join(line)
                        arrow = " " * (offset + 3) + "^"

                        raise InvalidSyntaxError(
                            msg=f"Некорректный символ после закрытой скобки: \n\n{expr}\n{arrow}\n\n",
                            line=line, info=self.info
                        )

                    self.expressions.append(token)
                    self.clean_comma()
                    return num

                self.expressions.append(token)
                self.clean_comma()

        if right_bracket != left_bracket:
            raise InvalidSyntaxError(info=self.info)
