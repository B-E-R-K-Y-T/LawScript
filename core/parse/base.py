import re
from abc import ABC, abstractmethod
from typing import Type, Sequence
from enum import Enum

from core.exceptions import InvalidSyntaxError, InvalidExpression
from core.types.basetype import BaseType
from core.tokens import Tokens
from core.types.line import Line


class Operators(Enum):
    ADD = str(Tokens.plus)
    SUB = str(Tokens.minus)
    MUL = str(Tokens.star)
    DIV = str(Tokens.div)
    LPAR = str(Tokens.left_bracket)
    RPAR = str(Tokens.right_bracket)


def build_rpn_stack(expr: list[str]) -> list[str]:
    stack = []
    result_stack = []
    operators_map = {
        str(Tokens.left_bracket): Operators.LPAR,
        str(Tokens.right_bracket): Operators.RPAR,
        str(Tokens.star): Operators.MUL,
        str(Tokens.div): Operators.DIV,
        str(Tokens.plus): Operators.ADD,
        str(Tokens.minus): Operators.SUB,
    }
    print(expr)
    for op in expr:
        if op not in operators_map:
            result_stack.append(op)
            continue

        if operators_map[op] == Operators.LPAR:
            stack.append(op)

        elif operators_map[op] == Operators.RPAR:
            while True:
                try:
                    if stack[-1] == str(Tokens.left_bracket):
                        break
                except IndexError:
                    raise InvalidExpression(f"В выражении: '{' '.join(expr)}' не хватает закрывающей скобки")

                op_ = stack.pop()

                if op_ in [str(Tokens.left_bracket), str(Tokens.right_bracket)]:
                    continue

                result_stack.append(op_)

        elif operators_map[op] in [Operators.MUL, Operators.DIV, Operators.ADD, Operators.SUB]:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    break

                if stack[-1] in [str(Tokens.star), str(Tokens.div)]:
                    result_stack.append(stack.pop())
                    stack.append(op)
                    break
                else:
                    stack.append(op)
                    break

    for op in reversed(stack):
        if op in [str(Tokens.left_bracket), str(Tokens.right_bracket)]:
            continue

        result_stack.append(op)

    print(result_stack)

    return result_stack


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
    def parse(self, body: list[str], jump: int) -> int: ...

    @abstractmethod
    def create_metadata(self, stop_num: int) -> MetaObject: ...

    @staticmethod
    def parse_sequence_words_to_str(words: Sequence[str]):
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
    def separate_line_to_token(line: Line) -> list[str]:
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
                f"{", ".join([f"'{s}'" for s in end_symbols])}",
                info=line.get_file_info()
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
                        Tokens.plus, Tokens.minus, Tokens.div, Tokens.quotation
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


def parse_execute(parser: Parser, code: list[Line], num_line: int) -> MetaObject:
    stop_num = parser.parse(code, num_line)
    meta = parser.create_metadata(stop_num)

    return meta
