from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.types.dispositions import Disposition
from core.parse.base import Parser, MetaObject, Image
from core.tokens import Tokens
from core.types.line import Line, Info
from core.util import is_ignore_line
from util.console_worker import printer


class DispositionMetaObject(MetaObject):
    def __init__(self, stop_num: int, right: Optional[str], duty: Optional[str], rule: Optional[str], info: Info):
        super().__init__(stop_num)
        self.right = right
        self.duty = duty
        self.rule = rule
        self.info = info
        printer.logging(f"Создано DispositionMetadata с stop_num={stop_num}, right={right}, duty={duty}, rule={rule}", level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание образа Disposition с right={self.right}, duty={self.duty}, rule={self.rule}", level="INFO")
        return Image(
            name=self.right,
            obj=Disposition,
            image_args=(self.right, self.duty, self.rule),
            info=self.info,
        )


class DefineDispositionParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.right: Optional[str] = None
        self.duty: Optional[str] = None
        self.rule: Optional[str] = None
        printer.logging("Инициализация DefineDispositionParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных Disposition с stop_num={stop_num}, right={self.right}, duty={self.duty}, rule={self.rule}", level="INFO")
        return DispositionMetaObject(
            stop_num,
            right=self.right,
            duty=self.duty,
            rule=self.rule,
            info=self.info
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга DefineDisposition с jump={jump} {Disposition.__name__}", level="INFO")

        for num, line in enumerate(body):
            if num < jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.disposition, Tokens.left_bracket]:
                    printer.logging("Обнаружено начало определения disposition", level="INFO")
                    ...
                case [Tokens.law, right, Tokens.comma]:
                    self.right = right
                    printer.logging(f"Добавлено право: {self.right}", level="INFO")
                case [Tokens.duty, duty, Tokens.comma]:
                    self.duty = duty
                    printer.logging(f"Добавлено обязанность: {self.duty}", level="INFO")
                case [Tokens.rule, rule, Tokens.comma]:
                    self.rule = rule
                    printer.logging(f"Добавлено правило: {self.rule}", level="INFO")
                case [Tokens.right_bracket]:
                    printer.logging("Парсинг disposition завершен: 'end_body' найден", level="INFO")
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        printer.logging("Парсинг disposition завершен с ошибкой: неверный синтаксис", level="ERROR")
        raise InvalidSyntaxError
