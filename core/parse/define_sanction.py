from typing import Optional, List

from core.exceptions import InvalidSyntaxError, InvalidLevelDegree
from core.types.line import Line
from core.types.sanctions import Sanction
from core.parse.base import Parser, Image, MetaObject
from core.parse.define_sequence import DefineSequenceParser
from core.tokens import Tokens
from core.types.severitys import Levels
from core.util import is_ignore_line
from util.console_worker import printer


class SanctionMetaObject(MetaObject):
    def __init__(self, stop_num: int, types: Optional[List[str]], severity: Optional[str],
                 procedural_aspects: Optional[str]):
        super().__init__(stop_num)
        self.types = types
        self.severity = severity
        self.procedural_aspects = procedural_aspects
        printer.logging(f"Создано SanctionMetadata с stop_num={stop_num}, types={types}, severity={severity}, "
                        f"procedural_aspects={procedural_aspects}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа Sanction с types={self.types}, severity={self.severity}, "
                        f"procedural_aspects={self.procedural_aspects}", level="INFO")
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
        printer.logging("Инициализация DefineSanctionParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных Sanction с stop_num={stop_num}, types={self.types}, "
                        f"severity={self.severity}, procedural_aspects={self.procedural_aspects}", level="INFO")
        return SanctionMetaObject(
            stop_num,
            types=self.types,
            severity=self.severity,
            procedural_aspects=self.procedural_aspects
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга санкции с jump={jump} {Sanction.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.sanction, Tokens.left_bracket]:
                    printer.logging("Обнаружено начало тела санкции", level="INFO")
                    ...
                case [Tokens.types, *types, Tokens.comma]:
                    sequence = DefineSequenceParser()
                    stop_num = sequence.parse(types, num)
                    self.types = sequence.create_metadata().seq
                    jump = self.next_num_line(stop_num)
                    printer.logging(f"Определены типы санкции: {self.types}", level="INFO")
                case [Tokens.degree, Tokens.of_rigor, degree, Tokens.comma]:
                    if degree not in Levels:
                        printer.logging(f"Некорректный уровень строгости: {degree}", level="ERROR")
                        raise InvalidLevelDegree(degree)

                    self.severity = degree
                    printer.logging(f"Уровень строгости установлен: {self.severity}", level="INFO")
                case [Tokens.procedural, Tokens.aspect, *procedural_aspect, Tokens.comma]:
                    self.procedural_aspects = self.parse_many_word_to_str(procedural_aspect)
                    printer.logging(f"Определены процедурные аспекты: {self.procedural_aspects}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг санкции завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг санкции завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
