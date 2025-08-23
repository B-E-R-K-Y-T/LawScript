from typing import Union

from src.core.exceptions import InvalidExpression, BaseError
from src.core.extend.function_wrap import PyExtendWrapper
from src.core.parse.base import is_integer, is_float, is_identifier
from src.core.tokens import Tokens, ServiceTokens
from src.core.types.atomic import Number, String, Boolean, Void, VOID
from src.core.types.basetype import BaseAtomicType
from src.core.types.line import Info
from src.core.types.operation import Operator
from src.core.types.procedure import LinkedProcedure, Procedure, ProcedureContextName
from src.util.console_worker import printer

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
    Tokens.comma,
    Tokens.wait,
    Tokens.attr_access,
    ServiceTokens.unary_minus,
    ServiceTokens.unary_plus,
    ServiceTokens.in_background,
}


class AttrAccess:
    def __init__(self, expr: list[Union[Operator, BaseAtomicType]]):
        self.expr = expr


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
        if filtered_expr[-1] in ALLOW_OPERATORS - {Tokens.left_bracket, Tokens.right_bracket, Tokens.true, Tokens.false}:
            raise InvalidExpression(
                f"Выражение: {' '.join(str(item) for item in expr)} не может заканчиваться на: '{filtered_expr[-1]}'"
            )

    in_count = sum(1 for op in filtered_expr if op == Tokens.in_)
    background_count = sum(1 for op in filtered_expr if op == Tokens.background)

    if in_count != background_count:
        raise InvalidExpression(
            f"В выражении: {' '.join(str(item) for item in expr)} "
            f"не может быть оператора '{Tokens.in_}' без '{Tokens.background}'"
        )

    count_left_bracket = sum(1 for op in filtered_expr if op == Tokens.left_bracket)
    count_right_bracket = sum(1 for op in filtered_expr if op == Tokens.right_bracket)

    if count_left_bracket > count_right_bracket:
        diff = count_left_bracket - count_right_bracket

        raise InvalidExpression(
            f"В выражении: '{' '.join(str(item) for item in expr)}' не хватает {diff} закрывающих скобок: '{Tokens.right_bracket}'"
        )

    if count_right_bracket > count_left_bracket:
        diff = count_right_bracket - count_left_bracket

        raise InvalidExpression(
            f"В выражении: '{' '.join(str(item) for item in expr)}' не хватает {diff} открывающих скобок: '{Tokens.left_bracket}'"
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
        Tokens.wait,
        Tokens.attr_access
    )

    for op in filtered_expr:
        if op == previous_op:
            raise InvalidExpression(
                f"В выражении: '{' '.join(str(item) for item in expr)}' не может быть подряд два оператора: '{op}'"
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
        if isinstance(op, (LinkedProcedure, Procedure, PyExtendWrapper)):
            continue

        if op not in allowed_ops:
            if not is_integer(op) and not is_float(op) and not is_identifier(op):
                raise InvalidExpression(
                    f"В выражении: '{' '.join(str(item) for item in expr)}' не может быть оператора: '{op}'"
                )

    count_double_comma = 0

    for op in filtered_expr:
        if count_double_comma > 1:
            raise InvalidExpression(f"В выражении: {' '.join(str(item) for item in expr)} не может быть подряд больше одной запятой")

        if op == Tokens.comma:
            count_double_comma += 1
        else:
            count_double_comma = 0


def prepare_expr(expr: list[str]) -> list:
    printer.logging(f"Начало подготовки выражения. Исходное выражение: {expr}", level="DEBUG")

    i = 0
    while i < len(expr):
        if expr[i] == Tokens.quotation:
            printer.logging(f"Обнаружена открывающая кавычка на позиции {i}", level="DEBUG")
            start_idx = i
            i += 1
            string_parts = []

            while i < len(expr) and expr[i] != Tokens.quotation:
                item = expr[i]
                printer.logging(f"Обработка элемента строки: {item}", level="TRACE")

                if isinstance(item, LinkedProcedure):
                    item = item.func.name
                    printer.logging(f"Преобразование LinkedProcedure в имя: {item}", level="TRACE")

                string_parts.append(item)
                i += 1

            if i < len(expr) and expr[i] == Tokens.quotation:
                string_value = ''.join(string_parts)
                printer.logging(f"Сформирована строка: {string_value}", level="DEBUG")
                expr[start_idx:i + 1] = [String(string_value)]
                i = start_idx + 1
            else:
                printer.logging("Не найдена закрывающая кавычка", level="WARNING")
                i = start_idx + 1
        else:
            i += 1

    printer.logging(f"Выражение после обработки строк: {expr}", level="DEBUG")

    is_string = False
    i = len(expr) - 1

    while i >= 0:
        op = expr[i]
        printer.logging(f"Обработка оператора {op} на позиции {i}", level="TRACE")

        if op == Tokens.quotation:
            is_string = not is_string
            printer.logging(f"Переключение флага строки: {is_string}", level="TRACE")

        if is_string:
            i -= 1
            continue

        if i < len(expr) - 1:
            next_op = expr[i + 1]

            if op == Tokens.not_ and next_op == Tokens.bool_equal:
                printer.logging("Обнаружена комбинация операторов not и =", level="DEBUG")
                expr[i:i + 2] = [Tokens.bool_not_equal]
                i -= 1
                continue

            if op == Tokens.in_ and next_op == Tokens.background:
                printer.logging("Обнаружена комбинация операторов in и background", level="DEBUG")
                expr[i:i + 2] = [ServiceTokens.in_background]
                i -= 1
                continue

        if i > 0 and expr[i - 1] == Tokens.attr_access:
            printer.logging(f"Обнаружена цепочка атрибутов на позиции {i}", level="DEBUG")
            end_idx = i
            start_idx = end_idx - 1

            while start_idx >= 0 and expr[start_idx] == Tokens.attr_access:
                start_idx -= 2

            start_idx += 1
            printer.logging(f"Начало цепочки атрибутов: {start_idx}, конец: {end_idx}", level="DEBUG")

            if start_idx >= 0 and end_idx < len(expr):
                attr_access_expr = expr[start_idx:end_idx + 1]
                printer.logging(f"Выделенная цепочка атрибутов: {attr_access_expr}", level="DEBUG")

                if Tokens.left_bracket in attr_access_expr or Tokens.right_bracket in attr_access_expr:
                    printer.logging("Обнаружены скобки в цепочке атрибутов", level="ERROR")
                    raise InvalidExpression("Нельзя разрывать цепочки атрибутов скобками")

                expr[start_idx:end_idx + 1] = [AttrAccess(_build_rpn(attr_access_expr))]
                printer.logging(f"Замена цепочки на AttrAccess", level="DEBUG")
                i = start_idx

        i -= 1

    printer.logging(f"Финальное выражение после подготовки: {expr}", level="DEBUG")
    return expr


def detect_unary(expr: list[str], offset, op, type_op) -> bool:
    aw_without_right_bracket = ALLOW_OPERATORS - {Tokens.right_bracket}
    left_op = expr[offset - 1] in aw_without_right_bracket

    return left_op and op == type_op


def build_rpn_stack(expr: list[str], meta_info: Info) -> list[Union[Operator, BaseAtomicType]]:
    try:
        check_correct_expr(expr)
        new_expr = prepare_expr(expr)
        return _build_rpn(new_expr)
    except BaseError as e:
        raise InvalidExpression(str(e), meta_info)
    except IndexError:
        prepared_expr = []

        for item in expr:
            if isinstance(item, String):
                prepared_expr.append(f"\"{item}\"")
            else:
                prepared_expr.append(str(item))

        raise InvalidExpression(f"Выражение: '{' '.join(prepared_expr)}' не может быть преобразовано в RPN-стек", meta_info)


def _build_rpn(expr: list[str]) -> list[Union[Operator, BaseAtomicType]]:
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
                    stack.append(ProcedureContextName(Operator(op)))
                    printer.logging(f"Функция '{op}' добавлена в стек, так как за ней следует открывающая скобка",
                                    level="INFO")
                    continue

            result_stack.append(op)
            printer.logging(f"Оператор '{op}' добавлен в результирующий стек", level="INFO")
            continue

        if op == Tokens.left_bracket:
            if len(expr) > 2 and offset != 0 and (is_identifier(expr[offset - 1]) or isinstance(expr[offset - 1], AttrAccess)) and expr[offset - 1] not in {*ALLOW_OPERATORS, Tokens.true, Tokens.false}:
                result_stack.append(ServiceTokens.arg_separator)

            stack.append(op)
            printer.logging(f"Открывающая скобка '{op}' добавлена в стек", level="INFO")

        elif op == Tokens.right_bracket:
            previous_op = expr[offset - 1]

            if previous_op == Tokens.left_bracket:
                stack.append(ServiceTokens.void_arg)
                result_stack.pop(-1)

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

        elif op == Tokens.comma:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if stack[-1] not in [Tokens.left_bracket, Tokens.right_bracket]:
                    for _ in range(len(stack)):
                        if stack[-1] in [
                            Tokens.left_bracket, Tokens.right_bracket, Tokens.comma,
                        ]:
                            break

                        op_ = stack.pop(-1)
                        result_stack.append(op_)

                result_stack.append(op)
                break

        elif op == Tokens.attr_access:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if stack[-1] in [
                    Tokens.exponentiation, Tokens.left_bracket, Tokens.right_bracket, Tokens.wait, Tokens.attr_access
                ]:
                    for _ in range(len(stack)):
                        if stack[-1] in [
                            Tokens.left_bracket, Tokens.right_bracket, Tokens.exponentiation
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

                if stack[-1] in [
                    Tokens.exponentiation, Tokens.left_bracket, Tokens.right_bracket, Tokens.wait, Tokens.attr_access
                ]:
                    for _ in range(len(stack)):
                        if stack[-1] in [
                            Tokens.left_bracket, Tokens.right_bracket, Tokens.exponentiation
                        ]:
                            break

                        op_ = stack.pop(-1)
                        result_stack.append(op_)

                stack.append(op)
                break

        elif op == ServiceTokens.in_background:
            while True:
                if len(stack) == 0:
                    if detect_unary(expr, offset, op, ServiceTokens.in_background):
                        stack.append(ServiceTokens.in_background)
                        printer.logging(f"Оператор '{ServiceTokens.in_background}' добавлен в стек (пустой стек)", level="INFO")
                        break

                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break
                else:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек", level="INFO")
                    break

        elif op == Tokens.wait:
            while True:
                if len(stack) == 0:
                    if detect_unary(expr, offset, op, Tokens.wait):
                        stack.append(Tokens.wait)
                        printer.logging(f"Оператор '{Tokens.wait}' добавлен в стек (пустой стек)", level="INFO")
                        break

                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break
                else:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек", level="INFO")
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
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.exponentiation,
                        ServiceTokens.unary_minus, ServiceTokens.unary_plus, Tokens.wait, Tokens.attr_access
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
                        Tokens.star, Tokens.div, Tokens.exponentiation, Tokens.wait,
                        ServiceTokens.unary_minus, ServiceTokens.unary_plus, Tokens.attr_access
                    ]:
                        for _ in range(len(stack)):
                            if stack[-1] not in [
                                Tokens.star, Tokens.div, Tokens.wait,
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
                    if stack[-1] in [
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.not_, Tokens.wait, Tokens.attr_access
                    ]:
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
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.not_, Tokens.and_, Tokens.wait,
                        Tokens.attr_access
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
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus,
                        Tokens.not_, Tokens.and_, Tokens.or_, Tokens.wait, Tokens.attr_access
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
                        Tokens.star, Tokens.div, Tokens.plus, Tokens.minus, Tokens.attr_access,
                        Tokens.not_, Tokens.and_, Tokens.or_, Tokens.bool_equal,Tokens.bool_not_equal,
                        Tokens.greater, Tokens.less, Tokens.exponentiation, Tokens.wait,
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

    def flatten(lst):
        flat_list = []
        for item in lst:
            if isinstance(item, ProcedureContextName) and isinstance(item.operator.operator, AttrAccess):
                flat_list.extend(flatten(item.operator.operator.expr))
                continue

            if isinstance(item, AttrAccess):
                flat_list.extend(flatten(item.expr))
            else:
                flat_list.append(item)
        return flat_list

    result_stack = flatten(result_stack)

    printer.logging(f"Завершено построение RPN-стека. Результат: {result_stack}", level="INFO")

    return compile_rpn(result_stack)

def compile_rpn(expr):
    printer.logging(f"\nКомпиляция RPN-выражения: {expr}", level="INFO")
    compiled_stack = []
    jump = 0

    for offset, op in enumerate(expr):
        printer.logging(f"Компиляция элемента [{offset}]: {op}", level="TRACE")
        if offset < jump:
            continue

        if op == Tokens.void:
            op = VOID

        if isinstance(op, Operator):
            compiled_stack.append(op)
            continue

        if isinstance(op, BaseAtomicType):
            compiled_stack.append(op)
            continue

        if isinstance(op, ProcedureContextName):
            compiled_stack.append(op)
            continue

        if op in ALLOW_OPERATORS:
            compiled_stack.append(Operator(op))
            continue

        if isinstance(op, (LinkedProcedure, Procedure, PyExtendWrapper)):
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

        compiled_stack.append(Operator(op))

    printer.logging(f"Итоговый скомпилированный стек: {compiled_stack}", level="DEBUG")
    return compiled_stack
