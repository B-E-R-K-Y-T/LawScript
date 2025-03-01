from typing import Optional

from core.exceptions import InvalidSyntaxError
from core.parse.base import MetaObject, Image, Parser, is_identifier
from core.parse.table.body import TableBodyParser
from core.tokens import Tokens
from core.types.atomic import String
from core.types.line import Line, Info
from core.types.table import TableFactory, TableImage, Table
from core.util import is_ignore_line
from util.console_worker import printer


class DefineTableMetaObject(MetaObject):
    def __init__(
            self, stop_num: int, name: str, table_image: TableImage, info: Info
    ):
        super().__init__(stop_num)
        self.name = name
        self.table_image = table_image
        self.info = info

    def create_image(self) -> Image:
        return Image(
            name=self.name,
            obj=TableFactory,
            image_args=(self.table_image,),
            info=self.info
        )


class DefineTableParser(Parser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.table_name: Optional[str] = None
        self.this = None
        self.body: Optional[MetaObject] = None

    def create_metadata(self, stop_num: int) -> MetaObject:
        return DefineTableMetaObject(
            stop_num,
            name=self.table_name,
            table_image=TableImage(
                table=Table,
                body=self.body,
                this=self.this,
            ),
            info=self.info
        )

    def execute_parse_define(self, table_name, this, body, num, info_line, base: Optional[str] = None):
        if not is_identifier(table_name):
            raise InvalidSyntaxError(
                f"Неверный синтаксис. Название таблицы должно быть идентификатором: {table_name}",
                info=info_line
            )

        if not is_identifier(this):
            raise InvalidSyntaxError(
                f"Неверный синтаксис. Ссылка на экземпляр должна быть идентификатором: {this}",
                info=info_line
            )

        if base is not None and not is_identifier(base):
            raise InvalidSyntaxError(
                f"Неверный синтаксис. Ссылка на базовую таблицу должна быть идентификатором: {base}",
                info=info_line
            )

        self.table_name = table_name
        self.this = String(str(this))
        self.body = self.execute_parse(TableBodyParser, body, self.next_num_line(num))
        self.jump = self.previous_num_line(self.jump)

    def parse(self, body: list[Line], jump) -> int:
        self.jump = jump

        for num, line in enumerate(body):
            if num < self.jump:
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку: {line}", level="INFO")
                continue

            if self.info is None:
                self.info = line.get_file_info()

            info_line = line.get_file_info()
            line = self.separate_line_to_token(line)

            match line:
                case [Tokens.define, Tokens.a_table, Tokens.left_bracket, this, Tokens.right_bracket, table_name, Tokens.left_bracket]:
                    self.execute_parse_define(table_name, this, body, num, info_line)
                case [Tokens.define, Tokens.a_table, Tokens.left_bracket, this, Tokens.right_bracket, table_name, Tokens.extends, base, Tokens.left_bracket]:
                    self.execute_parse_define(table_name, this, body, num, info_line, base)
                case [Tokens.right_bracket]:
                    return num
                case _:
                    printer.logging(f"Неверный синтаксис: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=info_line)

        raise InvalidSyntaxError
