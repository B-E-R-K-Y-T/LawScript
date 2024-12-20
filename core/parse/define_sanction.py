from typing import Optional, List

from core.exceptions import InvalidSyntaxError, InvalidLevelDegree
from core.types.sanctions import Sanction
from core.parse.base import Parser, Image, Metadata
from core.parse.define_sequence import DefineSequenceParser
from core.token import Token
from core.types.severitys import Levels
from core.util import is_ignore_line


class SanctionMetadata(Metadata):
    def __init__(self, stop_num: int, types: Optional[List[str]], severity: Optional[str],
                 procedural_aspects: Optional[str]):
        super().__init__(stop_num)
        self.types = types
        self.severity = severity
        self.procedural_aspects = procedural_aspects

    def create_image(self) -> Image:
        return Image(
            name=str(id(self)),
            obj=Sanction,
            image_args=(self.types, self.severity, self.procedural_aspects)
        )


class DefineSanctionParser(Parser):
    def __init__(self):
        self.types: Optional[str] = None
        self.severity: Optional[str] = None
        self.procedural_aspects: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return SanctionMetadata(
            stop_num,
            types=self.types,
            severity=self.severity,
            procedural_aspects=self.procedural_aspects
        )

    def parse(self, body: list[str], jump) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.sanction, Token.start_body]:
                    ...
                case [Token.types, *types, Token.comma]:
                    sequence = DefineSequenceParser()
                    stop_num = sequence.parse(types, num)
                    self.types = sequence.create_metadata().seq
                    jump = self.next_num_line(stop_num)
                case [Token.degree, Token.of_rigor, degree, Token.comma]:
                    if degree not in Levels:
                        raise InvalidLevelDegree(degree)

                    self.severity = degree
                case [Token.procedural, Token.aspect, *procedural_aspect, Token.comma]:
                    self.procedural_aspects = self.parse_many_word_to_str(procedural_aspect)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
