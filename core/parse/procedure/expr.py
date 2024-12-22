from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser
from core.tokens import Tokens
from core.types.procedure import Expression, Add
from core.util import is_ignore_line


class DefineExpressionMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str):
        super().__init__(stop_num)
        self.name = name

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Expression,
            image_args=()
        )


class ExpressionParser(Parser):
    def __init__(self):
        super().__init__()

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DefineExpressionMetaObject(
            stop_num,
            name=str(id(self)),
        )

    def parse(self, expr: list[str], jump) -> int:
        self.jump = jump

        for num, operand in enumerate(expr):
            if num < self.jump:
                continue

            if is_ignore_line(operand):
                continue

            # line = self.separate_line_to_token(line)

            match operand:
                case Tokens.left_bracket:

                    print(expr)
                    self.execute_parse(ExpressionParser, expr, self.next_num_line(num))
                case Tokens.plus:
                    return Add
                case Tokens.right_bracket:
                    return num
                case Tokens.right_square_bracket:
                    return num
                case Tokens.end_expr:
                    return num
                case str(value):
                    print(value)
                    return num
                case _:
                    raise InvalidSyntaxError

        raise InvalidSyntaxError
