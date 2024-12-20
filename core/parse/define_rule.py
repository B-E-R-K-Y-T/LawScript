from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.rules import Rule
from core.util import is_ignore_line


class DefineRuleMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, description: str):
        super().__init__(stop_num)
        self.name = name
        self.description = description

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Rule,
            image_args=(self.description,)
        )


class DefineRuleParser(Parser):
    def __init__(self):
        self.name_rule: Optional[str] = None
        self.description: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return DefineRuleMetadata(
            stop_num,
            name=self.name_rule,
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
                case [Token.define, Token.rule, name_rule, Token.start_body]:
                    self.name_rule = name_rule
                case [Token.description, *description, Token.comma]:
                    self.description = self.parse_many_word_to_str(description)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
