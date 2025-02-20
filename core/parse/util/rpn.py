from core.exceptions import InvalidExpression
from core.tokens import Tokens
from util.console_worker import printer


def build_rpn_stack(expr: list[str]) -> list[str]:
    printer.logging(f"Начало построения RPN-стека из выражения: {expr}", level="INFO")

    stack = []
    result_stack = []
    allow_operators = (
        Tokens.left_bracket,
        Tokens.right_bracket,
        Tokens.star,
        Tokens.div,
        Tokens.plus,
        Tokens.minus,
    )

    for offset, op in enumerate(expr):
        printer.logging(f"Текущий оператор: {op}, стек: {stack}, результат стек: {result_stack}", level="DEBUG")

        if op not in allow_operators:
            if 0 <= offset < len(expr) - 1:
                next_op = expr[offset + 1]

                if next_op == Tokens.left_bracket:
                    stack.append(op)
                    printer.logging(f"Функция '{op}' добавлена в стек, так как за ней следует открывающая скобка",
                                    level="INFO")
                    continue

            result_stack.append(op)
            printer.logging(f"Оператор '{op}' добавлен в результат стек", level="INFO")
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
                printer.logging(f"Оператор '{op_}' добавлен в результат стек", level="INFO")

        elif op in [Tokens.star, Tokens.div, Tokens.plus, Tokens.minus]:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    printer.logging(f"Оператор '{op}' добавлен в стек (пустой стек)", level="INFO")
                    break

                if stack[-1] in [Tokens.star, Tokens.div]:
                    result_stack.append(stack.pop())
                    result_stack.append(op)
                    printer.logging(
                        f"Добавлен оператор '{op}' в результат стек, так как верхний элемент стека '{stack[-1]}' имеет больший приоритет",
                        level="INFO")
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

    for op in reversed(stack):
        if op in [Tokens.left_bracket, Tokens.right_bracket]:
            continue

        result_stack.append(op)
        printer.logging(f"Оператор '{op}' добавлен в результат стек из оставшегося стека", level="INFO")

    printer.logging(f"Завершено построение RPN-стека. Результат: {result_stack}", level="INFO")

    return result_stack
