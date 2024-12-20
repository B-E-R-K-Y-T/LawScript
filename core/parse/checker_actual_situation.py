from typing import Optional

from core.exceptions import InvalidSyntaxError, NameNotDefine
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.checkers import CheckerSituation
from core.util import is_ignore_line


class CheckerActualSituationMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, document_name: str, fact_situation_name: str):
        super().__init__(stop_num)
        self.name = name
        self.document_name = document_name
        self.fact_situation_name = fact_situation_name

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=CheckerSituation,
            image_args=(self.document_name, self.fact_situation_name)
        )


class CheckerParser(Parser):
    def __init__(self):
        self.name: Optional[str] = None
        self.situation_name: Optional[str] = None
        self.document_name: Optional[str] = None
        self.jump = 0

    def create_metadata(self, stop_num: int) -> Metadata:
        return CheckerActualSituationMetadata(
            stop_num,
            name=self.name,
            document_name=self.document_name,
            fact_situation_name=self.situation_name,
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
                case [Token.check, name, Token.start_body]:
                    self.name = name
                case [Token.actual, Token.situation, situation_name, Token.comma]:
                    self.situation_name = situation_name
                case [Token.document, document_name, Token.comma]:
                    self.document_name = document_name
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
