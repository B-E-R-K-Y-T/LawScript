from core.exceptions import InvalidExpression
from core.parse.base import is_integer, is_float
from core.tokens import Tokens
from core.types.atomic import Number, String, Boolean
from util.console_worker import printer

ALLOW_OPERATORS = (
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
)


def check_bracket(expr: list[str]):
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


def build_rpn_stack(expr: list[str]) -> list[str]:
    check_bracket(expr)

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

        elif op in [Tokens.star, Tokens.div, Tokens.plus, Tokens.minus]:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if op in [Tokens.plus, Tokens.minus]:
                    if stack[-1] in [Tokens.star, Tokens.div, Tokens.plus, Tokens.minus]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket,
                                Tokens.and_, Tokens.or_,  Tokens.not_, Tokens.bool_equal
                            ]:
                               break

                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    stack.append(op)
                    break

                if op in [Tokens.star, Tokens.div]:
                    if stack[-1] in [Tokens.plus, Tokens.minus]:
                        stack.append(op)
                        break

                    elif stack[-1] in [Tokens.star, Tokens.div]:
                        for _ in range(len(stack)):
                            if stack[-1] not in [
                                Tokens.plus, Tokens.minus,
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

        elif op in [Tokens.and_, Tokens.or_,  Tokens.not_, Tokens.bool_equal]:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if op == Tokens.not_:
                    if stack[-1] in [Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.not_]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket, Tokens.and_, Tokens.or_, Tokens.bool_equal
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
                                Tokens.left_bracket, Tokens.right_bracket, Tokens.or_, Tokens.bool_equal
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
                                Tokens.left_bracket, Tokens.right_bracket, Tokens.bool_equal
                            ]:
                               break

                            op_ = stack.pop(-1)
                            result_stack.append(op_)

                    stack.append(op)
                    break

                if op == Tokens.bool_equal:
                    if stack[-1] in [
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus,
                        Tokens.not_, Tokens.and_, Tokens.or_, Tokens.bool_equal,
                    ]:
                        for _ in range(len(stack)):
                            if stack[-1] in [
                                Tokens.left_bracket, Tokens.right_bracket, Tokens.or_, Tokens.bool_equal
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
            compiled_stack.append(op)
            continue

        if is_integer(op):
            compiled_stack.append(Number(int(op)))
            continue
        elif is_float(op):
            compiled_stack.append(Number(float(op)))
            continue

        if op == Tokens.true:
            compiled_stack.append(Boolean(True))
            continue
        elif op == Tokens.false:
            compiled_stack.append(Boolean(False))
            continue

        if op == Tokens.quotation:
            step = offset
            res_op = ""

            while step < len(expr)-1:
                step += 1
                next_op = expr[step]

                if next_op == Tokens.quotation:
                    jump = step + 1
                    break

                res_op += next_op
            else:
                raise InvalidExpression(
                    f"В выражении: '{' '.join(expr)}' не хватает закрывающей кавычки: '{Tokens.quotation}'"
                )

            compiled_stack.append(String(res_op))
            continue

        compiled_stack.append(op)

    return compiled_stack
