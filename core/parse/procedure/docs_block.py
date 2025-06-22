from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.docs import Docs
from core.types.line import Line, Info
from core.util import is_ignore_line


class DocsBlockMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, docs_text: str, info: Info):
        super().__init__(stop_num)
        self.name = name
        self.docs_text = docs_text
        self.info = info

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=Docs,
            image_args=(self.docs_text,),
            info=self.info
        )


class DocsBlockParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name: Optional[str] = None
        self.docs_text = ""

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DocsBlockMetaObject(
            stop_num,
            name=self.name,
            docs_text=self.docs_text,
            info=self.info
        )

    def parse(self, body: list[Line], jump: int) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            self.info = line.get_file_info()
            line = line.split()

            match line:
                case[Tokens.right_bracket]:
                    return num
                case[Tokens.space]:
                    self.docs_text += "\n"
                case [*_]:
                    self.docs_text += f"{self.info.raw_line}\n"

        raise InvalidSyntaxError
