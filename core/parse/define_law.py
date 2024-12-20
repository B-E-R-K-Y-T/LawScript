from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.laws import Law
from core.util import is_ignore_line


class DefineLawMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, name_law: str, description: str):
        super().__init__(stop_num)
        self.name = name
        self.name_law = name_law
        self.description = description

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Law,
            image_args=(self.description,)
        )


class DefineLawParser(Parser):
    def __init__(self):
        self.name: Optional[str] = None
        self.name_law: Optional[str] = None
        self.description: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return DefineLawMetadata(
            stop_num,
            name=self.name,
            name_law=self.name_law,
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
                case [Token.define, Token.law, name_law, Token.start_body]:
                    self.name_law = name_law
                    self.name = name_law
                case [Token.description, *description, Token.comma]:
                    self.description = " ".join(description)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
