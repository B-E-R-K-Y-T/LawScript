from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.obligations import Obligation
from core.util import is_ignore_line


class DefineDutyMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, description: str):
        super().__init__(stop_num)
        self.name = name
        self.description = description

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Obligation,
            image_args=(self.description,)
        )


class DefineDutyParser(Parser):
    def __init__(self):
        self.name_obligation: Optional[str] = None
        self.description: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return DefineDutyMetadata(
            stop_num,
            name=self.name_obligation,
            description=self.description,
        )

    def parse(self, body: list[str], jump) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.define, Token.duty, name_obligation, Token.start_body]:
                    self.name_obligation = name_obligation
                case [Token.description, *description, Token.comma]:
                    self.description = " ".join(description)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
