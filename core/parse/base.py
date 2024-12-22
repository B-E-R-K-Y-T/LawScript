import re
from abc import ABC, abstractmethod
from typing import Type, Any, Sequence

from core.exceptions import InvalidSyntaxError, NameNotDefine
from core.types.basetype import BaseType
from core.tokens import Tokens


def is_integer(s: str) -> bool:
    return bool(re.match(r"^-?\d+$", str(s)))


def is_float(s: str) -> bool:
    return bool(re.match(r"^-?\d+(\.\d+)?$", str(s)))


class Image:
    def __init__(self, name: str, obj: Type[BaseType], image_args: tuple):
        self.name = name
        self.obj = obj
        self.image_args = image_args

    def build(self) -> BaseType:
        return self.obj(self.name, *self.image_args)


class MetaObject(ABC):
    def __init__(self, stop_num: int):
        self.__stop_num = stop_num

    @property
    def stop_num(self) -> int: return self.__stop_num

    @abstractmethod
    def create_image(self, *args, **kwargs) -> Image: ...


class Parser(ABC):
    def __init__(self):
        self.jump: int = -1

    @abstractmethod
    def parse(self, body: list[str], jump: int) -> int:
        ...

    @abstractmethod
    def create_metadata(self, stop_num: int) -> MetaObject:
        ...

    @staticmethod
    def parse_many_word_to_str(words: Sequence[str]):
        return " ".join(words)

    def execute_parse(self, parser: Type["Parser"], code: list[str], num: int) -> MetaObject:
        parser = parser()
        meta = parse_execute(parser, code, num)
        self.jump = self.next_num_line(meta.stop_num)

        return meta

    @staticmethod
    def next_num_line(num_line: int) -> int:
        return num_line + 1

    @staticmethod
    def previous_num_line(num_line: int) -> int:
        return num_line - 1

    @staticmethod
    def separate_line_to_token(line: str) -> list[str]:
        # Убираем комментарии из строки
        for offset, symbol in enumerate(line):
            match symbol:
                case Tokens.comment:
                    line = line[:offset].rstrip()
                    break

        end_symbols = (Tokens.left_bracket, Tokens.right_bracket, Tokens.comma, Tokens.end_expr)

        for end_symbol in end_symbols:
            if line.endswith(end_symbol):
                break
        else:
            raise InvalidSyntaxError(
                f"Некорректная строка: '{line}', возможно Вы забыли один из этих знаков в конце: "
                f"{", ".join([f"'{s}'" for s in end_symbols])}"
            )

        separated_line = line.split()

        tokens = []

        for token in separated_line:
            if token in Tokens:
                tokens.append(token)
                continue

            unknown_token = ""

            for symbol in token:
                if symbol in (
                        Tokens.left_bracket, Tokens.right_bracket, Tokens.comma, Tokens.star,
                        Tokens.left_square_bracket, Tokens.right_square_bracket, Tokens.equal,
                        Tokens.plus, Tokens.minus, Tokens.div
                ):
                    if unknown_token:
                        tokens.append(unknown_token)
                        unknown_token = ""

                    tokens.append(symbol)
                else:
                    unknown_token += symbol

            if unknown_token:
                tokens.append(unknown_token)

        match list(tokens[-1]):
            case [*old, end]:
                if old:
                    tokens[-1] = "".join(old)
                    tokens.append(end)
                else:
                    tokens[-1] = end

        return tokens


    # def parse_expression(self, expression: Sequence[str]):
    #     print(expression)
    #



def parse_execute(parser: Parser, code: list[str], num_line: int) -> MetaObject:
    stop_num = parser.parse(code, num_line)
    meta = parser.create_metadata(stop_num)

    return meta
