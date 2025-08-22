from typing import Optional

from src.core.exceptions import InvalidSyntaxError, NameAlreadyExist
from src.core.parse.base import Parser, MetaObject, Image
from src.core.parse.classes.define_constructor import DefineConstructorParser
from src.core.parse.classes.define_method import DefineMethodParser, DefineMethodMetaObject
from src.core.tokens import Tokens
from src.core.types.classes import ClassDefinition, Constructor
from src.core.types.line import Line, Info
from src.core.util import is_ignore_line
from src.util.console_worker import printer


class DefineClassMetaObject(MetaObject):
    def __init__(
            self, stop_num: int, name: str, info: Info,
            parent: Optional[ClassDefinition] = None,
            methods: Optional[dict[str, DefineMethodMetaObject]] = None,
            constructor: Optional[Constructor] = None
    ):
        printer.logging(f"Создание метаобъекта класса {name}", level="DEBUG")
        printer.logging(f"Родительский класс: {parent}", level="TRACE")
        printer.logging(f"Количество методов: {len(methods) if methods else 0}", level="TRACE")
        printer.logging(f"Конструктор: {'присутствует' if constructor else 'отсутствует'}", level="TRACE")

        super().__init__(stop_num)
        self.name = name
        self.info = info
        self.parent = parent
        self.methods = methods
        self.constructor = constructor

    def create_image(self) -> Image:
        printer.logging(f"Создание образа класса {self.name}", level="DEBUG")
        return Image(
            name=self.name,
            obj=ClassDefinition,
            image_args=(self.parent, self.methods, self.constructor),
            info=self.info,
        )


class DefineClassParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name: Optional[str] = None
        self.parent: Optional[ClassDefinition] = None
        self.methods: dict[str, DefineMethodMetaObject] = {}
        self.constructor: Optional[Constructor] = None
        printer.logging("Инициализация парсера класса", level="TRACE")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(f"Создание метаданных класса {self.name}", level="DEBUG")
        return DefineClassMetaObject(
            stop_num,
            name=self.name,
            info=self.info,
            parent=self.parent,
            methods=self.methods,
            constructor=self.constructor,
        )

    def parse(self, body: list[Line], jump: int) -> int:
        printer.logging(f"Начало парсинга класса (строки {jump}-{len(body)})", level="INFO")
        self.jump = jump

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку {num}: {line}", level="TRACE")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)
            printer.logging(f"Обработка строки {num}: {line}", level="DEBUG")

            match line:
                case [Tokens.define, Tokens.class_, name, Tokens.left_bracket]:
                    printer.logging(f"Объявление класса: {name}", level="INFO")
                    self.name = name

                case [Tokens.define, Tokens.class_, name, Tokens.extend, Tokens.from_, parent, Tokens.left_bracket]:
                    printer.logging(f"Объявление класса {name} с родителем {parent}", level="INFO")
                    self.name = name
                    self.parent = parent

                case [
                    Tokens.define, Tokens.method, Tokens.left_bracket, _, Tokens.right_bracket, name, *_
                ]:
                    printer.logging(f"Обнаружен метод {name} в классе {self.name}", level="DEBUG")
                    if name in self.methods.keys():
                        printer.logging(f"Ошибка: метод {name} уже существует", level="ERROR")
                        raise NameAlreadyExist(name, info=self.info)

                    printer.logging(f"Запуск парсера для метода {name}", level="TRACE")
                    method = self.execute_parse(DefineMethodParser, body, num)
                    self.methods[name] = method
                    printer.logging(f"Метод {name} успешно обработан", level="DEBUG")

                case [Tokens.define, Tokens.constructor, Tokens.left_bracket, _, Tokens.right_bracket, *_]:
                    printer.logging("Обнаружен конструктор класса", level="DEBUG")
                    if self.constructor is not None:
                        printer.logging("Ошибка: конструктор уже объявлен", level="ERROR")
                        raise NameAlreadyExist(
                            self.name,
                            msg=f"Конструктор уже был объявлен в классе '{self.name}'",
                            info=self.info
                        )

                    printer.logging("Запуск парсера конструктора", level="TRACE")
                    self.constructor = self.execute_parse(DefineConstructorParser, body, num)
                    printer.logging("Конструктор успешно обработан", level="DEBUG")

                case [Tokens.right_bracket]:
                    printer.logging(f"Завершение парсинга класса {self.name}", level="INFO")
                    printer.logging(f"Итоговые данные класса:", level="DEBUG")
                    printer.logging(f"- Родитель: {self.parent}", level="DEBUG")
                    printer.logging(f"- Методы: {list(self.methods.keys())}", level="DEBUG")
                    printer.logging(f"- Конструктор: {'присутствует' if self.constructor else 'отсутствует'}",
                                    level="DEBUG")
                    return num

                case _:
                    printer.logging(f"Неверный синтаксис в строке: {line}", level="ERROR")
                    raise InvalidSyntaxError(info=self.info)

        printer.logging("Ошибка: не найдена закрывающая скобка класса", level="ERROR")
        raise InvalidSyntaxError
