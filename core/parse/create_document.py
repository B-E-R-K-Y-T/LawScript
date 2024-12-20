from typing import Optional, Type

from core.exceptions import InvalidSyntaxError
from core.types.documents import Document
from core.parse.base import Parser, parse_execute, Metadata, Image
from core.parse.define_disposition import DefineDispositionParser
from core.parse.define_hypothesis import DefineHypothesisParser
from core.parse.define_sanction import DefineSanctionParser
from core.token import Token
from core.util import is_ignore_line


class DocumentMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, *args):
        super().__init__(stop_num)
        self.name = name
        self.args = args

    def create_image(self):
        return Image(
            name=self.name,
            obj=Document,
            image_args=self.args
        )


class CreateDocumentParser(Parser):
    def __init__(self):
        self.document_name: Optional[str] = None
        self.hypothesis: Optional[Metadata] = None
        self.disposition: Optional[Metadata] = None
        self.sanction: Optional[Metadata] = None
        self.jump = 0

    def create_metadata(self, stop_num: int) -> Metadata:
        return DocumentMetadata(
            stop_num,
            self.document_name,
            self.hypothesis,
            self.disposition,
            self.sanction
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
                case [Token.create, Token.document, document_name, Token.start_body]:
                    self.document_name = document_name
                case [Token.disposition, Token.start_body]:
                    meta = self.execute_parse(DefineDispositionParser, body, num)
                    self.disposition = meta
                case [Token.sanction, Token.start_body]:
                    meta = self.execute_parse(DefineSanctionParser, body, num)
                    self.sanction = meta
                case [Token.hypothesis, Token.start_body]:
                    meta = self.execute_parse(DefineHypothesisParser, body, num)
                    self.hypothesis = meta
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
