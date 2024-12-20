from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.types.dispositions import Disposition
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.util import is_ignore_line


class DispositionMetadata(Metadata):
    def __init__(self, stop_num: int, right: Optional[str], duty: Optional[str], rule: Optional[str]):
        super().__init__(stop_num)
        self.right = right
        self.duty = duty
        self.rule = rule

    def create_image(self) -> Image:
        return Image(
            name=self.right,
            obj=Disposition,
            image_args=(self.right, self.duty, self.rule)
        )


class DefineDispositionParser(Parser):
    def __init__(self):
        self.right: Optional[str] = None
        self.duty: Optional[str] = None
        self.rule: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return DispositionMetadata(
            stop_num,
            right=self.right,
            duty=self.duty,
            rule=self.rule
        )

    def parse(self, body: list[str], jump: int) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.disposition, Token.start_body]:
                    ...
                case [Token.law, right, Token.comma]:
                    self.right = right
                case [Token.duty, duty, Token.comma]:
                    self.duty = duty
                case [Token.rule, rule, Token.comma]:
                    self.rule = rule
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
