import uuid
from typing import Optional

from src.core.exceptions import InvalidSyntaxError
from src.core.parse.base import MetaObject, Image
from src.core.parse.procedure.body import BodyParser
from src.core.parse.procedure.muti_expressions import MultiExpressionParser
from src.core.tokens import Tokens
from src.core.types.execute_block import ExecuteBlock
from src.core.types.line import Line, Info
from src.core.types.procedure import Expression
from src.core.util import is_ignore_line
from src.util.console_worker import printer


class DefineExecuteBlockMetaObject(MetaObject):
    def __init__(self, stop_num: int, name: str, expressions: list[Expression], info: Info):
        super().__init__(stop_num)
        self.name = name
        self.expressions = expressions
        self.info = info
        printer.logging(
            f"Создано DefineExecuteBlockMetaObject с stop_num={stop_num}, name={name}, expressions={expressions}",
            level="INFO")

    def create_image(self) -> Image:
        printer.logging(f"Создание Image для ExecuteBlock с name={self.name}", level="DEBUG")
        return Image(
            name=self.name,
            obj=ExecuteBlock,
            image_args=(self.expressions,),
            info=self.info
        )


class DefineExecuteBlockParser(BodyParser):
    def __init__(self):
        super().__init__()
        self.info = None
        self.name: Optional[str] = None
        self.expressions: list[Expression] = []
        printer.logging("Инициализация DefineExecuteBlockParser", level="INFO")

    def create_metadata(self, stop_num: int) -> MetaObject:
        printer.logging(
            f"Создание метаданных ExecuteBlock с stop_num={stop_num}, name={self.name}, expressions={len(self.expressions)} выражений",
            level="INFO"
        )
        return DefineExecuteBlockMetaObject(
            stop_num,
            name=self.name,
            expressions=self.expressions,
            info=self.info
        )

    def parse(self, body: list[Line], jump: int) -> int:
        self.jump = jump
        printer.logging(f"Начало парсинга ExecuteBlock с jump={jump}", level="INFO")

        for num, line in enumerate(body):
            if num < self.jump:
                printer.logging(f"Пропуск строки {num} (jump={jump})", level="DEBUG")
                continue

            if is_ignore_line(line):
                printer.logging(f"Игнорируем строку {num}: {line}", level="DEBUG")
                continue

            if self.info is None:
                self.info = line.get_file_info()
                printer.logging(f"Установка информации о файле: {self.info}", level="DEBUG")

            line_info = line.get_file_info()
            self.auto_added_end_token_for_expr(line)
            line = self.separate_line_to_token(line)
            self.body_check_tokens(line)
            printer.logging(f"Обработка строки {num}: {line}", level="DEBUG")

            match line:
                case [Tokens.execute, Tokens.left_bracket]:
                    self.name = uuid.uuid4().hex
                    printer.logging(f"Начало ExecuteBlock, сгенерировано имя: {self.name}", level="INFO")
                    continue

                case [*expr, Tokens.end_expr]:
                    expression = Expression(str(), expr, line_info)
                    self.expressions.append(expression)
                    printer.logging(
                        f"Добавлено выражение в ExecuteBlock: {expression}, всего выражений: {len(self.expressions)}",
                        level="INFO"
                    )

                case [*expr, Tokens.left_bracket]:
                    expr = [*expr, Tokens.left_bracket]
                    MultiExpressionParser.init_left_bracket(expr)

                    res_expr = self.execute_parse(MultiExpressionParser, body, self.next_num_line(num))

                    MultiExpressionParser.set_default_left_bracket()

                    expr.extend(res_expr.expressions)

                    expression = Expression(str(), expr, line_info)
                    self.expressions.append(expression)

                    printer.logging(
                        f"Добавлено выражение в ExecuteBlock: {expression}, всего выражений: {len(self.expressions)}",
                        level="INFO"
                    )

                case [Tokens.right_bracket]:
                    printer.logging(
                        f"Завершение парсинга ExecuteBlock, найдено {len(self.expressions)} выражений",
                        level="INFO"
                    )
                    return num

                case _:
                    printer.logging(f"Неверный синтаксис в ExecuteBlock: {line}", level="ERROR")
                    raise InvalidSyntaxError(line=line, info=line_info)

        printer.logging("Ошибка парсинга ExecuteBlock: не найден закрывающий токен", level="ERROR")
        raise InvalidSyntaxError(f"Не найден закрывающий токен: '{Tokens.right_bracket}'", info=self.info)
