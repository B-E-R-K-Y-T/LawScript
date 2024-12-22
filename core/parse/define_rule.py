from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.line import Line
from core.types.rules import Rule
from core.util import is_ignore_line
from util.console_worker import printer


class DefineRuleMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, description: str):
        super().__init__(stop_num)
        self.name = name
        self.description = description
        printer.logging(f"Создано DefineRuleMetadata с stop_num={stop_num}, name={name}, description={description}",
                        level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа Rule с name={self.name}, description={self.description}", level="INFO")
        return Image(
            name=self.name,
            obj=Rule,
            image_args=(self.description,)
        )


class DefineRuleParser(Parser):
    def __init__(self):
        self.name_rule: Optional[str] = None
        self.description: Optional[str] = None
        printer.logging("Инициализация DefineRuleParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(
            f"Создание метаданных Rule с stop_num={stop_num}, "
            f"name_rule={self.name_rule}, description={self.description}", level="INFO"
        )
        return DefineRuleMetaObject(
            stop_num,
            name=self.name_rule,
            description=self.description,
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineRule с jump={jump} {Rule.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.rule, name_rule, Tokens.left_bracket]:
                    self.name_rule = name_rule
                    printer.logging(f"Обнаружено определение правила: {self.name_rule}", level="INFO")
                case [Tokens.description, *description, Tokens.comma]:
                    self.description = self.parse_many_word_to_str(description)
                    printer.logging(f"Добавлено описание правила: {self.description}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг правила завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info)

        printer.logging("Парсинг правила завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
