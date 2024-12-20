from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import Parser, Metadata, Image
from core.token import Token
from core.types.rules import Rule
from core.util import is_ignore_line
from util.console_worker import printer


class DefineRuleMetadata(Metadata):
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

    def create_metadata(self, stop_num: int) -> Metadata:
        printer.logging(
            f"Создание метаданных Rule с stop_num={stop_num}, "
            f"name_rule={self.name_rule}, description={self.description}", level="INFO"
        )
        return DefineRuleMetadata(
            stop_num,
            name=self.name_rule,
            description=self.description,
        )

    def parse(self, body: list[str], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineRule с jump={jump}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            line = self.prepare_line(line)

            match line:
                case [Token.define, Token.rule, name_rule, Token.start_body]:
                    self.name_rule = name_rule
                    printer.logging(f"Обнаружено определение правила: {self.name_rule}", level="INFO")
                case [Token.description, *description, Token.comma]:
                    self.description = self.parse_many_word_to_str(description)
                    printer.logging(f"Добавлено описание правила: {self.description}", level="INFO")
                case [Token.end_body]:
                    printer.logging("Парсинг правила завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line)

        printer.logging("Парсинг правила завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
