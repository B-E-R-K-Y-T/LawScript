from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.objects import Object
from core.util import is_ignore_line


class DefineObjectMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, name_object: str):
        super().__init__(stop_num)
        self.name = name
        self.name_object = name_object

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Object,
            image_args=(self.name_object,)
        )


class DefineObjectParser(Parser):
    def __init__(self):
        self.name_object_define: Optional[str] = None
        self.name_object: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return DefineObjectMetadata(
            stop_num,
            name=self.name_object_define,
            name_object=self.name_object,
        )

    def parse(self, body: list[str], jump) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.define, Token.object, name_object, Token.start_body]:
                    self.name_object_define = name_object
                case [Token.name, *name_object, Token.comma]:
                    self.name_object = " ".join(name_object)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
