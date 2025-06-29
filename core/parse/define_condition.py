from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.parse.criteria import DefineCriteriaParser
from core.tokens import Tokens
from core.types.conditions import Condition
from core.types.line import Line, Info
from core.util import is_ignore_line
from util.console_worker import printer


class DefineConditionMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, description: str, criteria: MetaObject, info: Info):
        super().__init__(stop_num)
        self.info = info
        self.name = name
        self.description = description
        self.criteria = criteria
        printer.logging(f"Создано DefineConditionMetadata с stop_num={stop_num}, name={name}, description={description}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа DefineCondition с name={self.name}, description={self.description}, criteria={self.criteria}", level="INFO")
        return Image(
            name=self.name,
            obj=Condition,
            image_args=(self.description, self.criteria,),
            info=self.info,
        )


class DefineConditionParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name_condition: Optional[str] = None
        self.description: Optional[str] = None
        self.criteria: Optional[MetaObject] = None
        self.jump = -1
        printer.logging("Инициализация DefineConditionParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных DefineCondition с stop_num={stop_num}, name={self.name_condition}, description={self.description}, criteria={self.criteria}", level="INFO")
        return DefineConditionMetaObject(
            stop_num,
            name=self.name_condition,
            description=self.description,
            criteria=self.criteria,
            info=self.info,
        )

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга DefineCondition с jump={jump} {Condition.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.condition, name_condition, Tokens.left_bracket]:
                    self.name_condition = name_condition
                    printer.logging(f"Обнаружено определение условия: {name_condition}", level="INFO")
                case [Tokens.description, *description, Tokens.comma]:
                    self.description = self.parse_sequence_words_to_str(description)
                    printer.logging(f"Добавлено описание условия: {self.description}", level="INFO")
                case [Tokens.criteria, *_]:
                    meta = self.execute_parse(DefineCriteriaParser, body, num)
                    self.criteria = meta
                    printer.logging(f"Обработаны критерии для условия: {self.criteria}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг условия завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(info=self.info)

        printer.logging("Парсинг условия завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
