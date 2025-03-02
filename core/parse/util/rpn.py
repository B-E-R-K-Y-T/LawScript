from typing import Union

from core.exceptions import InvalidExpression, BaseError
from core.parse.base import is_integer, is_float, is_identifier
from core.tokens import Tokens, ServiceTokens
from core.types.atomic import Number, String, Boolean
from core.types.basetype import BaseAtomicType
from core.types.line import Info
from core.types.operation import Operator
from core.types.procedure import LinkedProcedure
from core.types.table import TableFactory
from util.console_worker import printer

ALLOW_OPERATORS = {
    Tokens.left_bracket,
    Tokens.right_bracket,
    Tokens.star,
    Tokens.div,
    Tokens.plus,
    Tokens.minus,
    Tokens.and_,
    Tokens.or_,
    Tokens.not_,
    Tokens.bool_equal,
    Tokens.bool_not_equal,
    Tokens.greater,
    Tokens.less,
    Tokens.exponentiation,
    Tokens.dot,
    ServiceTokens.unary_minus,
    ServiceTokens.unary_plus,
}


def check_correct_expr(expr: list[str]):
    filtered_expr = []
    filter_on = False

    for op in expr:
        if op == Tokens.quotation:
            if filter_on:
                filter_on = False
            else:
                filter_on = True

        if not filter_on:
            filtered_expr.append(op)

    if filtered_expr:
        if filtered_expr[-1] in ALLOW_OPERATORS - {Tokens.left_bracket, Tokens.right_bracket}:
            raise InvalidExpression(
                f"Выражение: {' '.join(expr)} не может заканчиваться на: '{filtered_expr[-1]}'"
            )

    count_left_bracket = sum(1 for op in filtered_expr if op == Tokens.left_bracket)
    count_right_bracket = sum(1 for op in filtered_expr if op == Tokens.right_bracket)

    if count_left_bracket > count_right_bracket:
        diff = count_left_bracket - count_right_bracket

        raise InvalidExpression(
            f"В выражении: '{' '.join(expr)}' не хватает {diff} закрывающих скобок: '{Tokens.right_bracket}'"
        )

    if count_right_bracket > count_left_bracket:
        diff = count_right_bracket - count_left_bracket

        raise InvalidExpression(
            f"В выражении: '{' '.join(expr)}' не хватает {diff} открывающих скобок: '{Tokens.left_bracket}'"
        )

    previous_op = None

    not_repeated_ops = (
        Tokens.minus,
        Tokens.plus,
        Tokens.div,
        Tokens.star,
        Tokens.and_,
        Tokens.or_,
        Tokens.not_,
        Tokens.bool_equal,
        Tokens.bool_not_equal,
        Tokens.greater,
        Tokens.less,
    )

    for op in filtered_expr:
        if op == previous_op:
            raise InvalidExpression(
                f"В выражении: '{' '.join(expr)}' не может быть подряд два оператора: '{op}'"
            )

        if op in not_repeated_ops:
            previous_op = op
        else:
            previous_op = None

    allowed_ops = {
        *ALLOW_OPERATORS,
        Tokens.true,
        Tokens.false,
        Tokens.quotation,
    }

    for op in filtered_expr:
        if isinstance(op, LinkedProcedure):
            continue

        if op not in allowed_ops:
            if isinstance(op, BaseAtomicType):
                continue

            if not is_integer(op) and not is_float(op) and not is_identifier(op):
                raise InvalidExpression(
                    f"В выражении: '{' '.join(expr)}' не может быть оператора: '{op}'"
                )

def detect_unary(expr: list[str], offset, op, type_op) -> bool:
    aw_without_right_bracket = ALLOW_OPERATORS - {Tokens.right_bracket}
    left_op = expr[offset - 1] in aw_without_right_bracket

    return left_op and op == type_op


def build_rpn_stack(expr: list[str], meta_info: Info) -> list[Union[Operator, BaseAtomicType]]:
    try:
        return _build_rpn(expr)
    except BaseError as e:
        raise InvalidExpression(str(e), meta_info)


def _build_rpn(expr: list[str]) -> list[Union[Operator, BaseAtomicType]]:
    check_correct_expr(expr)

    printer.logging(f"Начало построения RPN-стека из выражения: {expr}", level="INFO")

    stack = []
    result_stack = []
    jump = 0

    for offset, op in enumerate(expr):
        if offset < jump:
            continue

        printer.logging(f"Текущий оператор: {op}, стек: {stack}, результирующий стек: {result_stack}", level="DEBUG")

        if op == Tokens.quotation:
            result_stack.append(op)

            for sub_offset, sub_op in enumerate(expr[offset+1:]):
                result_stack.append(sub_op)

                if sub_op == Tokens.quotation:
                    jump = sub_offset + offset + 2
                    break

            continue

        if op == Tokens.right_bracket:
            previous_op = expr[offset - 1]

            if previous_op == Tokens.left_bracket:
                result_stack.append(ServiceTokens.void_arg)

        if op not in ALLOW_OPERATORS:
            if 0 <= offset < len(expr) - 1:
                next_op = expr[offset + 1]

                if next_op == Tokens.left_bracket:
                    stack.append(op)
                    printer.logging(f"Функция '{op}' добавлена в стек, так как за ней следует открывающая скобка",
                                    level="INFO")
                    continue

            result_stack.append(op)
            printer.logging(f"Оператор '{op}' добавлен в результирующий стек", level="INFO")
            continue

        if op == Tokens.left_bracket:
            stack.append(op)
            printer.logging(f"Открывающая скобка '{op}' добавлена в стек", level="INFO")

        elif op == Tokens.right_bracket:
            while True:
                if not stack:
                    raise InvalidExpression(
                        f"В выражении: '{' '.join(expr)}' не хватает открывающей скобки: '{Tokens.left_bracket}'"
                    )

                try:
                    if stack[-1] == Tokens.left_bracket:
                        stack.pop(-1)
                        printer.logging(f"Закрывающая скобка '{op}' обнаружена. Открывающая скобка удалена из стека.",
                                        level="INFO")

                        if not stack:
                            break

                        next_op = stack[-1]

                        # if next_op == Tokens.dot:
                        #     break

                        if next_op not in ALLOW_OPERATORS:
                            op_ = stack.pop()
                            result_stack.append(op_)

                        break
                except IndexError:
                    raise InvalidExpression(
                        f"В выражении: '{' '.join(expr)}' не хватает открывающей скобки: '{Tokens.left_bracket}'"
                    )

                op_ = stack.pop()
                if op_ in [Tokens.left_bracket, Tokens.right_bracket]:
                    continue

                result_stack.append(op_)
                printer.logging(f"Оператор '{op_}' добавлен в результирующий стек", level="INFO")

        elif op == Tokens.dot:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if stack[-1] in [Tokens.dot, Tokens.left_bracket, Tokens.right_bracket]:
                    for _ in range(len(stack)):
                        if stack[-1] in [
                            Tokens.left_bracket, Tokens.right_bracket, # Tokens.dot
                        ]:
                            break

                        op_ = stack.pop(-1)
                        result_stack.append(op_)

                stack.append(op)
                break

        elif op == Tokens.exponentiation:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if stack[-1] in [Tokens.dot, Tokens.exponentiation, Tokens.left_bracket, Tokens.right_bracket]:
                    for _ in range(len(stack)):
                        if stack[-1] in [
                            Tokens.left_bracket, Tokens.right_bracket, Tokens.exponentiation
                        ]:
                            break

                        op_ = stack.pop(-1)
                        result_stack.append(op_)

                stack.append(op)
                break

        elif op in [Tokens.star, Tokens.div, Tokens.plus, Tokens.minus]:
            while True:
                if len(stack) == 0:
                    if detect_unary(expr, offset, op, Tokens.minus):
                        stack.append(ServiceTokens.unary_minus)
                        printer.logging(f"Оператор '{ServiceTokens.unary_minus}' добавлен в стек (пустой стек)", level="INFO")
                        break
                    elif detect_unary(expr, offset, op, Tokens.plus):
                        stack.append(ServiceTokens.unary_plus)
                        printer.logging(f"Оператор '{ServiceTokens.unary_plus}' добавлен в стек (пустой стек)", level="INFO")
                        break

                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if op in [Tokens.plus, Tokens.minus]:
                    if stack[-1] in [
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.exponentiation, Tokens.dot,
                        ServiceTokens.unary_minus, ServiceTokens.unary_plus,
                    ]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket,
                                Tokens.and_, Tokens.or_,  Tokens.not_, Tokens.bool_equal, Tokens.bool_not_equal,
                            ]:
                               break

                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    if len(expr) >= offset:
                        if detect_unary(expr, offset, op, Tokens.minus):
                            stack.append(ServiceTokens.unary_minus)
                            break
                        elif detect_unary(expr, offset, op, Tokens.plus):
                            stack.append(ServiceTokens.unary_plus)
                            break

                    stack.append(op)
                    break

                if op in [Tokens.star, Tokens.div]:
                    if stack[-1] in [Tokens.plus, Tokens.minus]:
                        stack.append(op)
                        break

                    elif stack[-1] in [
                        Tokens.star, Tokens.div, Tokens.exponentiation, Tokens.dot,
                        ServiceTokens.unary_minus, ServiceTokens.unary_plus
                    ]:
                        for _ in range(len(stack)):
                            if stack[-1] not in [
                                Tokens.star, Tokens.div, Tokens.dot,
                                Tokens.left_bracket, Tokens.right_bracket,
                            ]:
                                break
                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    stack.append(op)
                    break

                elif stack[-1].isalnum():
                    result_stack.append(stack.pop())
                    stack.append(op)
                    printer.logging(f"Добавлен оператор '{op}' в стек, предыдущий элемент стека был '{stack[-1]}'",
                                    level="INFO")
                    break
                else:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек", level="INFO")
                    break

        elif op in [
            Tokens.and_, Tokens.or_,  Tokens.not_, Tokens.bool_equal,
            Tokens.bool_not_equal,  Tokens.greater, Tokens.less
        ]:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if op == Tokens.not_:
                    if stack[-1] in [Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.not_]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket,
                                Tokens.and_, Tokens.or_, Tokens.bool_equal,Tokens.bool_not_equal,
                                Tokens.greater, Tokens.less,  ServiceTokens.unary_plus, ServiceTokens.unary_minus,
                            ]:
                               break

                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    stack.append(op)
                    break

                if op == Tokens.and_:
                    if stack[-1] in [
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.not_, Tokens.and_
                    ]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket,
                                Tokens.or_, Tokens.bool_equal,Tokens.bool_not_equal, Tokens.greater, Tokens.less,
                                ServiceTokens.unary_plus, ServiceTokens.unary_minus,
                            ]:
                               break

                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    stack.append(op)
                    break

                if op == Tokens.or_:
                    if stack[-1] in [
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.not_, Tokens.and_, Tokens.or_
                    ]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket,
                                Tokens.bool_equal, Tokens.bool_not_equal, Tokens.greater, Tokens.less,
                                ServiceTokens.unary_plus, ServiceTokens.unary_minus,
                            ]:
                               break

                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    stack.append(op)
                    break

                if op in [Tokens.bool_equal, Tokens.bool_not_equal, Tokens.greater, Tokens.less]:
                    if stack[-1] in [
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus,
                        Tokens.not_, Tokens.and_, Tokens.or_, Tokens.bool_equal,Tokens.bool_not_equal,
                        Tokens.greater, Tokens.less, Tokens.exponentiation,
                        ServiceTokens.unary_plus, ServiceTokens.unary_minus,
                    ]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket
                            ]:
                               break

                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    stack.append(op)
                    break

    for op in reversed(stack):
        if op in [Tokens.left_bracket, Tokens.right_bracket]:
            continue

        result_stack.append(op)
        printer.logging(f"Оператор '{op}' добавлен в результирующий стек из оставшегося стека", level="INFO")

    printer.logging(f"Завершено построение RPN-стека. Результат: {result_stack}", level="INFO")

    return compile_rpn(result_stack)

def compile_rpn(expr):
    compiled_stack = []
    jump = 0

    for offset, op in enumerate(expr):
        if offset < jump:
            continue

        if op in ALLOW_OPERATORS:
            compiled_stack.append(Operator(op))
            continue

        if isinstance(op, LinkedProcedure):
            compiled_stack.append(op)
            continue

        if isinstance(op, TableFactory):
            compiled_stack.append(op)
            continue

        if isinstance(op, String):
            compiled_stack.append(op)
            continue

        if isinstance(op, Number):
            compiled_stack.append(op)
            continue

        if is_integer(op):
            compiled_stack.append(Number(int(op)))
            continue

        if op == Tokens.true:
            compiled_stack.append(Boolean(True))
            continue
        elif op == Tokens.false:
            compiled_stack.append(Boolean(False))
            continue

        compiled_stack.append(Operator(op))

    return compiled_stack
