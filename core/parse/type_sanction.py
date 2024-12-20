from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.types.sanction_types import SanctionType
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.util import is_ignore_line


class TypeSanctionMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, *args):
        super().__init__(stop_num)
        self.name = name
        self.args = args

    def create_image(self):
        return Image(
            name=self.name,
            obj=SanctionType,
            image_args=self.args
        )


class TypeSanctionParser(Parser):
    def __init__(self):
        self.name_sanction_type: Optional[str] = None
        self.article: Optional[str] = None
        self.name: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return TypeSanctionMetadata(
            stop_num,
            self.name,
            self.name_sanction_type,
            self.article
        )

    def parse(self, body: list[str], jump: int) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.define, Token.of_sanction, name, Token.start_body]:
                    self.name_sanction_type = name
                    self.name = name
                case [Token.article, *article, Token.comma]:
                    self.article = self.parse_many_word_to_str(article)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
