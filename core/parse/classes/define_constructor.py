from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image
from core.parse.classes.define_method import DefineMethodParser, DefineMethodMetaObject
from core.tokens import Tokens
from core.types.classes import Constructor
from core.types.line import Line, Info
from core.types.procedure import Expression
from core.util import is_ignore_line
from util.console_worker import printer


class DefineConstructorMetaObject(DefineMethodMetaObject):
    def __init__(
            self, stop_num: int, body: Optional[MetaObject], arguments_name: list[Optional[str]],
            info: Info, default_arguments: Optional[dict[str, Expression]], this: str
    ):
        super().__init__(stop_num, "", body, arguments_name, info, default_arguments, this)

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Constructor,
            image_args=(self.body, self.arguments_name, self.default_arguments, self.this),
            info=self.info
        )


class DefineConstructorParser(DefineMethodParser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.arguments_name: list[Optional[str]] = []
        self.default_arguments: Optional[dict[str, Expression]] = None
        self.body: Optional[MetaObject] = None
        self.this: Optional[str] = None

    def create_metadata(self, stop_num: int) -> DefineConstructorMetaObject:
        return DefineConstructorMetaObject(
            stop_num,
            body=self.body,
            arguments_name=self.arguments_name,
            default_arguments=self.default_arguments,
            this=self.this,
            info=self.info
        )

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump

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
                case [
                    Tokens.define, Tokens.constructor, Tokens.left_bracket, this, Tokens.right_bracket,
                    Tokens.left_bracket, *arguments, Tokens.right_bracket, Tokens.left_bracket
                ]:
                    self.parse_define_procedure(body, "", arguments, num, info_line)
                    self.this  = this
                case [Tokens.right_bracket]:
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info_line)

        raise InvalidSyntaxError
