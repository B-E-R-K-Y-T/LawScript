from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.subjects import Subject
from core.util import is_ignore_line


class DefineSubjectMetadata(Metadata):
    def __init__(self, stop_num: int, name: str, name_subject: str):
        super().__init__(stop_num)
        self.name = name
        self.name_subject = name_subject

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Subject,
            image_args=(self.name_subject,)
        )


class DefineSubjectParser(Parser):
    def __init__(self):
        self.name_subject_define: Optional[str] = None
        self.name_subject: Optional[str] = None

    def create_metadata(self, stop_num: int) -> Metadata:
        return DefineSubjectMetadata(
            stop_num,
            name=self.name_subject_define,
            name_subject=self.name_subject,
        )

    def parse(self, body: list[str], jump) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.define, Token.subject, name_subject, Token.start_body]:
                    self.name_subject_define = name_subject
                case [Token.name, *name_subject, Token.comma]:
                    self.name_subject = self.parse_many_word_to_str(name_subject)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
