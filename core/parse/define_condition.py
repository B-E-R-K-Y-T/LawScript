from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.parse.criteria import DefineCriteriaParser
from core.token import Token
from core.types.conditions import Condition
from core.util import is_ignore_line


class DefineConditionMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, description: str, criteria: Metadata):
        super().__init__(stop_num)
        self.name = name
        self.description = description
        self.criteria = criteria

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Condition,
            image_args=(self.description, self.criteria,)
        )


class DefineConditionParser(Parser):
    def __init__(self):
        self.name: Optional[str] = None
        self.name_condition: Optional[str] = None
        self.description: Optional[str] = None
        self.criteria: Optional[Metadata] = None
        self.jump = -1

    def create_metadata(self, stop_num: int) -> Metadata:
        return DefineConditionMetadata(
            stop_num,
            name=self.name_condition,
            description=self.description,
            criteria=self.criteria,
        )

    def parse(self, body: list[str], jump) -> int:
        self.jump = jump

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.define, Token.condition, name_condition, Token.start_body]:
                    self.name_condition = name_condition
                case [Token.description, *description, Token.comma]:
                    self.description = self.parse_many_word_to_str(description)
                case [Token.criteria, *_]:
                    meta = self.execute_parse(DefineCriteriaParser, body, num)
                    self.criteria = meta
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
