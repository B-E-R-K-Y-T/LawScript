from typing import Type

from src.core.exceptions import InvalidSyntaxError
from src.core.parse.base import parse_execute, Parser, MetaObject
from src.core.parse.checker_actual_situation import CheckerParser
from src.core.parse.classes.define_class import DefineClassParser
from src.core.parse.create_document import CreateDocumentParser
from src.core.parse.create_actual_situation import CreateActualSituationParser
from src.core.parse.define_condition import DefineConditionParser
from src.core.parse.define_duty import DefineDutyParser
from src.core.parse.define_object import DefineObjectParser
from src.core.parse.define_law import DefineLawParser
from src.core.parse.define_rule import DefineRuleParser
from src.core.parse.define_subject import DefineSubjectParser
from src.core.parse.procedure.define_execute_block import DefineExecuteBlockParser
from src.core.parse.procedure.define_procedure import DefineProcedureParser
from src.core.parse.type_sanction import TypeSanctionParser
from src.core.tokens import Tokens
from src.core.types.line import Line
from src.core.util import is_ignore_line
from src.util.build_tools.compile import Compiled
from src.util.console_worker import printer


class AbstractSyntaxTreeBuilder:
    def __init__(self, code: list[Line]):
        self.code = code
        self.meta_code = []
        self.jump = -1
        printer.logging("Инициализация AbstractSyntaxTreeBuilder", level="INFO")

    def create_meta(self, parser: Type[Parser], num: int):
        parser = parser()
        meta = parse_execute(parser, self.code, num)
        self.jump = meta.stop_num
        self.meta_code.append(meta)
        printer.logging(
            f"Создана мета-структура с использованием {parser.__class__.__name__} на строке {num}",
            level="INFO"
        )

    def build(self) -> list[MetaObject]:
        for num, line in enumerate(self.code):
            if isinstance(line, Compiled):
                self.meta_code.append(line)
                continue

            if num <= self.jump:
                printer.logging(f"Пропуск строки {num} (переход по jump)", level="DEBUG")
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорирование пустой или комментарий строки {num}", level="DEBUG")
                continue

            match line.split():
                case [Tokens.define, Tokens.of_sanction, *_]:
                    self.create_meta(TypeSanctionParser, num)
                case [Tokens.define, Tokens.a_procedure, *_]:
                    self.create_meta(DefineProcedureParser, num)
                case [Tokens.create, Tokens.document, *_]:
                    self.create_meta(CreateDocumentParser, num)
                case [Tokens.create, Tokens.the_actual, Tokens.the_situation, *_]:
                    self.create_meta(CreateActualSituationParser, num)
                case [Tokens.check, *_]:
                    self.create_meta(CheckerParser, num)
                case [Tokens.define, Tokens.law, *_]:
                    self.create_meta(DefineLawParser, num)
                case [Tokens.define, Tokens.duty, *_]:
                    self.create_meta(DefineDutyParser, num)
                case [Tokens.define, Tokens.rule, *_]:
                    self.create_meta(DefineRuleParser, num)
                case [Tokens.define, Tokens.subject, *_]:
                    self.create_meta(DefineSubjectParser, num)
                case [Tokens.define, Tokens.object, *_]:
                    self.create_meta(DefineObjectParser, num)
                case [Tokens.define, Tokens.condition, *_]:
                    self.create_meta(DefineConditionParser, num)
                case [Tokens.execute, *_]:
                    self.create_meta(DefineExecuteBlockParser, num)
                case [Tokens.define, Tokens.class_, *_]:
                    self.create_meta(DefineClassParser, num)
                case [Tokens.extend, Tokens.class_, *_]:
                    self.create_meta(DefineClassParser, num)
                case _:
                    printer.logging(f"Ошибка синтаксиса в строке {num}: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line.split(), info=line.get_file_info())

        printer.logging("Построение AST завершено", level="INFO")
        return self.meta_code
