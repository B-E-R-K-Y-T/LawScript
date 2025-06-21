import uuid
from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.execute_block import ExecuteBlock
from core.types.line import Line, Info
from core.types.procedure import Expression
from core.util import is_ignore_line
from util.console_worker import printer


class DefineExecuteBlockMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, expressions: list[Expression], info: Info):
        super().__init__(stop_num)
        self.name = name
        self.expressions = expressions
        self.info = info
        printer.logging(f"Создано DefineExecuteBlockMetaObject с stop_num={stop_num}, name={name}, expressions={expressions}", level="INFO")

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=ExecuteBlock,
            image_args=(self.expressions,),
            info=self.info
        )


class DefineExecuteBlockParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name: Optional[str] = None
        self.expressions: list[Expression] = []

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DefineExecuteBlockMetaObject(
            stop_num,
            name=self.name,
            expressions=self.expressions,
            info=self.info
        )

    def parse(self, body: list[Line], jump: int) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.execute, Tokens.left_bracket]:
                    self.name = uuid.uuid4().hex
                    continue
                case [*expr, Tokens.end_expr]:
                    self.expressions.append(Expression(str(), expr, self.info))
                    printer.logging(f"Добавлено выражение: {self.expressions}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг блока вызова процедуры завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        raise InvalidSyntaxError
