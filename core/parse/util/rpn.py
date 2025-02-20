from core.exceptions import InvalidExpression
from core.tokens import Tokens


def build_rpn_stack(expr: list[str]) -> list[str]:
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
        if op not in allow_operators:
            if 0 <= offset < len(expr) - 1:
                next_op = expr[offset + 1]

                if next_op == Tokens.left_bracket:
                    stack.append(op)
                    continue

            result_stack.append(op)
            continue

        if op == Tokens.left_bracket:
            stack.append(op)

        elif op == Tokens.right_bracket:
            while True:
                if not stack:
                    raise InvalidExpression(
                        f"В выражении: '{' '.join(expr)}' не хватает открывающей скобки: '{Tokens.left_bracket}'"
                    )

                try:
                    if stack[-1] == Tokens.left_bracket:
                        stack.pop(-1)
                        break
                except IndexError:
                    raise InvalidExpression(
                        f"В выражении: '{' '.join(expr)}' не хватает открывающей скобки: '{Tokens.left_bracket}'"
                    )

                op_ = stack.pop()

                if op_ in [Tokens.left_bracket, Tokens.right_bracket]:
                    continue

                result_stack.append(op_)

        elif op in [Tokens.star, Tokens.div, Tokens.plus, Tokens.minus]:
            while True:
                if len(stack) == 0:
                    stack.append(op)
                    break

                if stack[-1] in [Tokens.star, Tokens.div]:
                    result_stack.append(stack.pop())
                    stack.append(op)
                    break
                elif stack[-1].isalnum():
                    result_stack.append(stack.pop())
                    stack.append(op)
                    break
                else:
                    stack.append(op)
                    break

    for op in reversed(stack):
        if op in [Tokens.left_bracket, Tokens.right_bracket]:
            continue

        result_stack.append(op)

    return result_stack
