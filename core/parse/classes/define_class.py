from typing import Optional

from core.exceptions import InvalidSyntaxError, NameAlreadyExist
from core.parse.base import Parser, MetaObject, Image
from core.parse.classes.define_constructor import DefineConstructorParser
from core.parse.classes.define_method import DefineMethodParser, DefineMethodMetaObject
from core.tokens import Tokens
from core.types.classes import ClassDefinition, Constructor, Method
from core.types.line import Line, Info
from core.util import is_ignore_line
from util.console_worker import printer


class DefineClassMetaObject(MetaObject):
    def __init__(
            self, stop_num: int, name: str, info: Info,
            parent: Optional[ClassDefinition] = None,
            methods: Optional[dict[str, DefineMethodMetaObject]] = None,
            constructor: Optional[Constructor] = None
    ):
        super().__init__(stop_num)
        self.name = name
        self.info = info
        self.parent = parent
        self.methods = methods
        self.constructor = constructor

    def create_image(self) -> Image:
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

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DefineClassMetaObject(
            stop_num,
            name=self.name,
            info=self.info,
            parent=self.parent,
            methods=self.methods,
            constructor=self.constructor,
        )

    def parse(self, body: list[Line], jump: int) -> int:
        self.jump = jump

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="DEBUG")
                continue

            self.info = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.class_, name, Tokens.left_bracket]:
                    self.name = name
                case [Tokens.extend, Tokens.class_, name, Tokens.from_, parent, Tokens.left_bracket]:
                    self.name = name
                    self.parent = parent
                case [
                    Tokens.define, Tokens.method, Tokens.left_bracket, _, Tokens.right_bracket, name, *_
                ]:
                    if name in self.methods.keys():
                        raise NameAlreadyExist(name, self.info)

                    method = self.execute_parse(DefineMethodParser, body, num)
                    self.methods[name] = method
                case [Tokens.define, Tokens.constructor, Tokens.left_bracket, _, Tokens.right_bracket, *_]:
                    self.constructor = self.execute_parse(DefineConstructorParser, body, num)
                case [Tokens.right_bracket]:
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=self.info)

        raise InvalidSyntaxError
