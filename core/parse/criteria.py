from typing import Optional

from core.exceptions import InvalidSyntaxError, InvalidType
from core.parse.base import Parser, Metadata, Image, is_integer, is_float
from core.token import Token
from core.types.conditions import Modify, Only, LessThan, GreaterThan, Between, NotOnly
from core.types.criteria import Criteria
from core.util import is_ignore_line


class DefineCriteriaMetadata(Metadata):
    def __init__(self, stop_num: int, criteria: dict[str, Modify]):
        super().__init__(stop_num)
        self.criteria = criteria

    def create_image(self) -> Image:
        return Image(
            name=str(id(self)),
            obj=Criteria,
            image_args=(self.criteria,)
        )


class DefineCriteriaParser(Parser):
    def __init__(self):
        self.criteria: Optional[dict[str, Modify]] = {}

    def create_metadata(self, stop_num: int) -> Metadata:
        return DefineCriteriaMetadata(
            stop_num,
            criteria=self.criteria,
        )

    def parse(self, body: list[str], jump) -> int:
        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.criteria, Token.start_body]:
                    ...
                case [name_criteria, Token.only, *value, Token.comma]:
                    self.criteria[name_criteria] = Only(self.parse_many_word_to_str(value))
                case [name_criteria, Token.not_, Token.may, Token.be, *value, Token.comma]:
                    self.criteria[name_criteria] = NotOnly(self.parse_many_word_to_str(value))
                case [name_criteria, Token.less, value, Token.comma]:
                    if is_float(value):
                        value = float(value)
                    elif is_integer(value):
                        value = int(value)
                    else:
                        raise InvalidType(value, "число", line)

                    self.criteria[name_criteria] = LessThan(value)
                case [name_criteria, Token.greater, value, Token.comma]:
                    if is_float(value):
                        value = float(value)
                    elif is_integer(value):
                        value = int(value)
                    else:
                        raise InvalidType(value, "число", line)

                    self.criteria[name_criteria] = GreaterThan(value)
                case [name_criteria, Token.between, value1, Token.and_, value2, Token.comma]:
                    values = []

                    for value in (value1, value2):
                        if is_float(value):
                            values.append(float(value))
                        elif is_integer(value):
                            values.append(int(value))
                        else:
                            raise InvalidType(value, "число", line)

                    self.criteria[name_criteria] = Between(*values)
                case [Token.end_body]:
                    return num
                case _:
                    raise InvalidSyntaxError(line=line)

        raise InvalidSyntaxError
