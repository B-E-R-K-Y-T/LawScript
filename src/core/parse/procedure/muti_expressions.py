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
        if len(self.expressions) > 1 and self.expressions[-2] == Tokens.comma and self.expressions[-1] == Tokens.right_bracket:
            self.expressions.pop(-2)

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

            is_string = False

            for token in line:
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
                    self.expressions.append(token)
                    self.clean_comma()
                    return num

                self.expressions.append(token)
                self.clean_comma()

        if right_bracket != left_bracket:
            raise InvalidSyntaxError(info=self.info)
