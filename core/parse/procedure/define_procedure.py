from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser
from core.parse.procedure.body import BodyParser
from core.tokens import Tokens
from core.types.procedure import Procedure, Body
from core.util import is_ignore_line


class DefineProcedureMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, body: Optional[MetaObject], arguments_name: list[Optional[str]]):
        super().__init__(stop_num)
        self.name = name
        self.body = body
        self.arguments_name = arguments_name

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Procedure,
            image_args=(self.body, self.arguments_name)
        )


class DefineProcedureParser(Parser):
    def __init__(self):
        super().__init__()
        self.procedure_name: Optional[str] = None
        self.arguments_name: list[Optional[str]] = []
        self.body: Optional[MetaObject] = None

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DefineProcedureMetaObject(
            stop_num,
            name=self.procedure_name,
            body=self.body,
            arguments_name=self.arguments_name,
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
                case [Tokens.define, Tokens.a_procedure, name_condition, Tokens.left_bracket, *arguments, Tokens.right_bracket, Tokens.left_bracket]:
                    arguments = "".join(arguments).split(Tokens.comma)
                    if not all(arguments):
                        raise InvalidSyntaxError(line=line)

                    self.procedure_name = name_condition
                    self.arguments_name = arguments
                    self.body = self.execute_parse(BodyParser, body, self.next_num_line(num))
                    self.jump = self.previous_num_line(self.jump)
                case [Tokens.right_bracket]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
