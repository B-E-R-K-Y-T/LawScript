from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.hypothesis import Hypothesis
from core.util import is_ignore_line


class HypothesisMetadata(Metadata):
    def __init__(self, stop_num: int, *args):
        super().__init__(stop_num)
        self.args = args

    def create_image(self):
        return Image(
            name=str(id(self)),
            obj=Hypothesis,
            image_args=self.args
        )


class DefineHypothesisParser(Parser):
    def __init__(self):
        self.subject: Optional[str] = None
        self.object: Optional[str] = None
        self.condition: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return HypothesisMetadata(
            stop_num,
            self.subject,
            self.object,
            self.condition
        )

    def parse(self, body: list[str], jump: int) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.hypothesis, Token.start_body]:
                    ...
                case [Token.subject, subject, Token.comma]:
                    self.subject = subject
                case [Token.object, object, Token.comma]:
                    self.object = object
                case [Token.condition, condition, Token.comma]:
                    self.condition = condition
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
