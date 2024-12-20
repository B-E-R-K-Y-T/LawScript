from typing import Any, Optional

from core.parse.base import Parser
from core.token import Token


class SequenceMetadata:
    def __init__(self, seq: list):
        self.seq = seq


class DefineSequenceParser(Parser):
    def __init__(self):
        self.sequence: Optional[list[Any]] = None

    def create_metadata(self) -> SequenceMetadata:
        if self.sequence is None:
            raise Exception

        return SequenceMetadata(self.sequence)

    def parse(self, body: list[str], jump: int) -> int:
        result = []

        for word in body:
            word = (
                word.
                replace("[", "").
                replace("]", "").
                replace(Token.comma, "")
            )

            if not word:
                continue

            result.append(word)

        self.sequence = result

        return jump
