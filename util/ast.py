from typing import Type

from core.exceptions import InvalidSyntaxError
from core.parse.base import parse_execute, Parser, Metadata
from core.parse.checker_actual_situation import CheckerParser
from core.parse.create_document import CreateDocumentParser
from core.parse.create_actual_situation import CreateActualSituationParser
from core.parse.define_condition import DefineConditionParser
from core.parse.define_duty import DefineDutyParser
from core.parse.define_object import DefineObjectParser
from core.parse.define_law import DefineLawParser
from core.parse.define_rule import DefineRuleParser
from core.parse.define_subject import DefineSubjectParser
from core.parse.type_sanction import TypeSanctionParser
from core.token import Token
from core.util import is_ignore_line


class AbstractSyntaxTreeBuilder:
    def __init__(self, code: list[str]):
        self.code = code
        self.meta_code = []
        self.jump = -1

    def create_meta(self, parser: Type[Parser], num: int):
        parser = parser()
        meta = parse_execute(parser, self.code, num)
        self.jump = meta.stop_num
        self.meta_code.append(meta)

    def build(self) -> list[Metadata]:
        for num, line in enumerate(self.code):
            if num <= self.jump:
                continue

            if is_ignore_line(line):
                continue

            match line.split():
                case [Token.define, Token.of_sanction, *_]:
                    self.create_meta(TypeSanctionParser, num)
                case [Token.create, Token.document, *_]:
                    self.create_meta(CreateDocumentParser, num)
                case [Token.create, Token.the_actual, Token.the_situation, *_]:
                    self.create_meta(CreateActualSituationParser, num)
                case [Token.check, *_]:
                    self.create_meta(CheckerParser, num)
                case [Token.define, Token.law, *_]:
                    self.create_meta(DefineLawParser, num)
                case [Token.define, Token.duty, *_]:
                    self.create_meta(DefineDutyParser, num)
                case [Token.define, Token.rule, *_]:
                    self.create_meta(DefineRuleParser, num)
                case [Token.define, Token.subject, *_]:
                    self.create_meta(DefineSubjectParser, num)
                case [Token.define, Token.object, *_]:
                    self.create_meta(DefineObjectParser, num)
                case [Token.define, Token.condition, *_]:
                    self.create_meta(DefineConditionParser, num)
                case _:
                    raise InvalidSyntaxError(f"Некорректная строка: {line}")

        return self.meta_code
