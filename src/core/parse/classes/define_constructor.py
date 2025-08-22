from typing import Optional

from src.core.exceptions import InvalidSyntaxError
from src.core.parse.base import MetaObject, Image
from src.core.parse.classes.define_method import DefineMethodParser, DefineMethodMetaObject
from src.core.tokens import Tokens
from src.core.types.classes import Constructor
from src.core.types.line import Line, Info
from src.core.types.procedure import Expression
from src.core.util import is_ignore_line
from src.util.console_worker import printer


class DefineConstructorMetaObject(DefineMethodMetaObject):
    def __init__(
            self, stop_num: int, body: Optional[MetaObject], arguments_name: list[Optional[str]],
            info: Info, default_arguments: Optional[dict[str, Expression]], this: str
    ):
        printer.logging(f"Создание метаобъекта конструктора (стоп-номер: {stop_num})", level="DEBUG")
        printer.logging(f"Аргументы: {arguments_name}", level="TRACE")
        printer.logging(f"Аргументы по умолчанию: {default_arguments.keys() if default_arguments else 'нет'}",
                        level="TRACE")
        printer.logging(f"Ключевое слово 'this': {this}", level="TRACE")

        super().__init__(stop_num, "", body, arguments_name, info, default_arguments, this)

    def create_image(self) -> Image:
        printer.logging("Создание образа конструктора", level="DEBUG")
        return Image(
            name=self.name,
            obj=Constructor,
            image_args=(self.body, self.arguments_name, self.default_arguments, self.this),
            info=self.info
        )


class DefineConstructorParser(DefineMethodParser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.arguments_name: list[Optional[str]] = []
        self.default_arguments: Optional[dict[str, Expression]] = None
        self.body: Optional[MetaObject] = None
        self.this: Optional[str] = None
        printer.logging("Инициализация парсера конструктора", level="TRACE")

    def create_metadata(self, stop_num: int) -> DefineConstructorMetaObject:
        printer.logging(f"Создание метаданных конструктора (стоп-номер: {stop_num})", level="DEBUG")
        printer.logging(f"Количество аргументов: {len(self.arguments_name)}", level="TRACE")
        return DefineConstructorMetaObject(
            stop_num,
            body=self.body,
            arguments_name=self.arguments_name,
            default_arguments=self.default_arguments,
            this=self.this,
            info=self.info
        )

    def parse(self, body: list[Line], jump) -> int:
        printer.logging(f"Начало парсинга конструктора (строки {jump}-{len(body)})", level="INFO")
        self.jump = jump

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку {num}: {line}", level="TRACE")
                continue

            if self.info is None:
                self.info = line.get_file_info()
                printer.logging(f"Установка информации о файле: {self.info}", level="TRACE")

            info_line = line.get_file_info()
            line = self.separate_line_to_token(line)
            printer.logging(f"Обработка строки {num}: {line}", level="DEBUG")

            match line:
                case [
                    Tokens.define, Tokens.constructor, Tokens.left_bracket, this, Tokens.right_bracket,
                    Tokens.left_bracket, *arguments, Tokens.right_bracket, Tokens.left_bracket
                ]:
                    printer.logging("Обнаружено объявление конструктора", level="INFO")
                    printer.logging(f"Ключевое слово для this: {this}", level="DEBUG")
                    printer.logging(f"Аргументы конструктора: {arguments}", level="DEBUG")

                    self.parse_define_procedure(body, "", arguments, num, info_line)
                    self.this = this
                    printer.logging("Парсинг тела конструктора завершен", level="DEBUG")

                case [Tokens.right_bracket]:
                    printer.logging("Обнаружена закрывающая скобка конструктора", level="DEBUG")
                    printer.logging("Парсинг конструктора успешно завершен", level="INFO")
                    return num

                case _:
                    printer.logging(f"Неверный синтаксис в строке {num}: {line}", level="ERROR")
                    raise InvalidSyntaxError(info=info_line)

        printer.logging("Ошибка: не найдена закрывающая скобка конструктора", level="ERROR")
        raise InvalidSyntaxError
