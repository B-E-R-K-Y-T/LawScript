from typing import Optional, Any

from core.exceptions import InvalidSyntaxError, InvalidType
from core.parse.base import Parser, Metadata, Image, is_integer, is_float
from core.token import Token
from core.types.documents import FactSituation
from core.util import is_ignore_line


class ActualSituationMetadata(Metadata):
    def __init__(
            self,
            stop_num: int,
            fact_name: str,
            *args
    ):
        super().__init__(stop_num)
        self.fact_name = fact_name
        self.args = args

    def create_image(self):
        return Image(
            name=self.fact_name,
            obj=FactSituation,
            image_args=self.args
        )


class CreateActualSituationParser(Parser):
    def __init__(self):
        self.fact_name: Optional[str] = None
        self.name_object: Optional[str] = None
        self.name_subject: Optional[str] = None
        self.data: Optional[dict[str, Any]] = None
        self.jump = 0

    def create_metadata(self, stop_num: int) -> Metadata:
        return ActualSituationMetadata(
            stop_num,
            self.fact_name,
            self.name_object,
            self.name_subject,
            self.data,
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
                case [Token.create, Token.the_actual, Token.the_situation, fact_name, Token.start_body]:
                    self.fact_name = fact_name
                case [Token.object, name_object, Token.comma]:
                    self.name_object = name_object
                case [Token.subject, name_subject, Token.comma]:
                    self.name_subject = name_subject
                case [Token.data, *_]:
                    meta = self.execute_parse(DataParser, body, num)
                    self.data = meta.data
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError


class CollectionData(Metadata):
    def __init__(
            self,
            stop_num: int,
            data: dict[str, Any],
            *args
    ):
        super().__init__(stop_num)
        self.data = data
        self.args = args

    def create_image(self): ...


class DataParser(Parser):
    def __init__(self):
        self.collection_data: dict[str, Any] = {}
        self.jump = 0

    def create_metadata(self, stop_num: int) -> CollectionData:
        return CollectionData(
            stop_num,
            self.collection_data,
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
                case [Token.data, Token.start_body]:
                    ...
                case [name_data, *data, Token.comma]:
                    value = self.parse_many_word_to_str(data)

                    if is_float(value):
                        value = float(value)
                    elif is_integer(value):
                        value = int(value)

                    self.collection_data[name_data] = value
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
