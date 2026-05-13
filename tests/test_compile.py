import pytest

from src.core.tokens import ServiceTokens
from src.core.types.atomic import Boolean, Number
from src.core.types.basetype import BaseAtomicType
from src.core.types.operation import Operator
from src.core.types.procedure import (
    When,
    Else,
    Loop,
    While,
    Context,
    Procedure,
    AssignField,
    ExceptionHandler,
    ProcedureContextName
)
from src.util.build_tools.starter import compile_string


# Базовые проверки Procedure и AssignField
def test_compile_procedure_structure():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЗАДАТЬ var = 1 + 2 * 3;
    )
    """
    compiled_proc = compile_string(code)
    proc_obj = compiled_proc.compiled_code.get("test")

    assert isinstance(proc_obj, Procedure)
    expr_var = proc_obj.body.commands[0]
    assert isinstance(expr_var, AssignField)
    assert expr_var.name == "var"
    assert expr_var.meta_info == expr_var.expression.meta_info


# Проверка арифметических выражений
arithmetic_test_data = [
    # (expression_str, raw_expr, raw_operations, expected_rpn)
    (
        "1 + 2 * 3",
        "1 + 2 * 3",
        ["1", "+", "2", "*", "3"],
        [Number(1), Number(2), Number(3), Operator("*"), Operator("+")],
    ),
    (
        "(1 + 2) * 3",
        "( 1 + 2 ) * 3",
        ["(", "1", "+", "2", ")", "*", "3"],
        [Number(1), Number(2), Operator("+"), Number(3), Operator("*")],
    ),
    (
        "10 - 5 + 2",
        "10 - 5 + 2",
        ["10", "-", "5", "+", "2"],
        [Number(10), Number(5), Operator("-"), Number(2), Operator("+")],
    ),
    (
        "2 ^ 3 + 1",
        "2 ^ 3 + 1",
        ["2", "^", "3", "+", "1"],
        [Number(2), Number(3), Operator("^"), Number(1), Operator("+")],
    ),
    (
        "10 / 2 * 3",
        "10 / 2 * 3",
        ["10", "/", "2", "*", "3"],
        [Number(10), Number(2), Operator("/"), Number(3), Operator("*")],
    ),
    (
        "-5 + 3",
        "- 5 + 3",
        ["-", "5", "+", "3"],
        [Number(5), Operator("-"), Number(3), Operator("+")],
    ),
    (
        "10 - 3 + 1",
        "10 - 3 + 1",
        ["10", "-", "3", "+", "1"],
        [Number(10), Number(3), Operator("-"), Number(1), Operator("+")],
    ),
    (
        "2 + 3 * 4 ^ 2",
        "2 + 3 * 4 ^ 2",
        ["2", "+", "3", "*", "4", "^", "2"],
        [Number(2), Number(3), Number(4), Number(2), Operator("^"), Operator("*"), Operator("+")],
    ),
    (
        "(5 - 2) * (3 + 1)",
        "( 5 - 2 ) * ( 3 + 1 )",
        ["(", "5", "-", "2", ")", "*", "(", "3", "+", "1", ")"],
        [
            Number(5), Number(2), Operator("-"),
            Number(3), Number(1), Operator("+"),
            Operator("*"),
        ],
    ),
]


@pytest.mark.parametrize(
    "expression_str,raw_expr,raw_operations,expected_rpn",
    arithmetic_test_data,
)
def test_compile_arithmetic_expressions(expression_str, raw_expr, raw_operations, expected_rpn):
    code = f"""
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЗАДАТЬ var = {expression_str};
    )
    """
    compiled_proc = compile_string(code)
    proc_obj = compiled_proc.compiled_code.get("test")

    expr_var = proc_obj.body.commands[0]
    assert isinstance(expr_var, AssignField)
    assert expr_var.expression.raw_expr == raw_expr
    assert expr_var.expression.raw_operations == raw_operations

    _assert_operations_match(expr_var.expression.operations, expected_rpn)


# Проверка булевых выражений
boolean_test_data = [
    (
        "ИСТИНА И ЛОЖЬ",
        "ИСТИНА И ЛОЖЬ",
        ["ИСТИНА", "И", "ЛОЖЬ"],
        [Boolean(True), Boolean(False), Operator("И")],
    ),
    (
        "5 БОЛЬШЕ 3",
        "5 БОЛЬШЕ 3",
        ["5", "БОЛЬШЕ", "3"],
        [Number(5), Number(3), Operator("БОЛЬШЕ")],
    ),
    (
        "НЕ ИСТИНА",
        "НЕ ИСТИНА",
        ["НЕ", "ИСТИНА"],
        [Boolean(True), Operator("НЕ")],
    ),
]


@pytest.mark.parametrize(
    "expression_str,raw_expr,raw_operations,expected_rpn",
    boolean_test_data,
)
def test_compile_boolean_expressions(expression_str, raw_expr, raw_operations, expected_rpn):
    code = f"""
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЗАДАТЬ var = {expression_str};
    )
    """
    compiled_proc = compile_string(code)
    proc_obj = compiled_proc.compiled_code.get("test")

    expr_var = proc_obj.body.commands[0]
    assert isinstance(expr_var, AssignField)
    assert expr_var.expression.raw_expr == raw_expr
    assert expr_var.expression.raw_operations == raw_operations

    _assert_operations_match(expr_var.expression.operations, expected_rpn)


# Проверка фоновых задач
def test_compile_background_task():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ bg () (
    )

    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЗАДАТЬ bg_var = В ФОНЕ bg();
    )
    """
    compiled_proc = compile_string(code)
    proc_obj = compiled_proc.compiled_code.get("test")

    expr_bg = proc_obj.body.commands[0]
    assert isinstance(expr_bg, AssignField)
    assert expr_bg.name == "bg_var"
    assert expr_bg.expression.raw_expr == "В ФОНЕ bg ( )"
    assert expr_bg.expression.raw_operations == [ServiceTokens.in_background, "bg", "(", ")"]
    assert expr_bg.meta_info == expr_bg.expression.meta_info

    expected_ops = [
        Operator(ServiceTokens.void_arg),
        ProcedureContextName(Operator("bg")),
        Operator(ServiceTokens.in_background),
    ]
    _assert_background_operations_match(expr_bg.expression.operations, expected_ops)


# Проверка мета-информации для первого выражения
def test_compile_expression_meta_info():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЗАДАТЬ var = 1 + 2 * 3;
    )
    """
    compiled_proc = compile_string(code)
    proc_obj = compiled_proc.compiled_code.get("test")

    expr_var = proc_obj.body.commands[0]
    assert expr_var.expression.meta_info.num == 3
    assert expr_var.expression.meta_info.raw_line == "ЗАДАТЬ var = 1 + 2 * 3;"


# Вспомогательные функции для проверки операций
def _assert_operations_match(actual_ops, expected_ops):
    """Проверяет соответствие операций в выражениях (арифметика, булевы)"""
    assert len(actual_ops) == len(expected_ops), \
        f"Operations count mismatch: {len(actual_ops)} != {len(expected_ops)}"

    for actual, expected in zip(actual_ops, expected_ops):
        if isinstance(expected, Operator):
            assert isinstance(actual, Operator), \
                f"Expected Operator, got {type(actual).__name__}"
            assert actual.operator == expected.operator, \
                f"Expected operator '{expected.operator}', got '{actual.operator}'"
        elif isinstance(expected, BaseAtomicType):
            assert isinstance(actual, BaseAtomicType), \
                f"Expected {type(expected).__name__}, got {type(actual).__name__}"
            assert actual.value == expected.value, \
                f"Expected value {expected.value!r}, got {actual.value!r}"
        else:
            raise AssertionError(f"Unexpected expected type: {type(expected)}")


def _assert_background_operations_match(actual_ops, expected_ops):
    """Проверяет соответствие операций для фоновых задач"""
    assert len(actual_ops) == len(expected_ops), \
        f"Operations count mismatch: {len(actual_ops)} != {len(expected_ops)}"

    for actual, expected in zip(actual_ops, expected_ops):
        if isinstance(expected, Operator):
            assert isinstance(actual, Operator), \
                f"Expected Operator, got {type(actual).__name__}"
            assert actual.operator == expected.operator, \
                f"Expected operator '{expected.operator}', got '{actual.operator}'"
        elif isinstance(expected, ProcedureContextName):
            assert isinstance(actual, ProcedureContextName), \
                f"Expected ProcedureContextName, got {type(actual).__name__}"
            assert actual.operator.operator == expected.operator.operator, \
                f"Expected procedure name '{expected.operator.operator}', " \
                f"got '{actual.operator.operator}'"
        else:
            raise AssertionError(f"Unexpected expected type: {type(expected)}")


def test_compile_proc():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test (arg1, arg2) (
        test;
        test;
        test;
    )
    """
    compiled_proc = compile_string(code)

    proc_obj = compiled_proc.compiled_code.get("test")

    assert isinstance(proc_obj, Procedure)
    assert proc_obj.name == "test"
    assert proc_obj.arguments_names == ["arg1", "arg2"]
    assert len(proc_obj.body.commands) == 3


def test_compile_when():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЕСЛИ ИСТИНА ТО (
            test;
            test;
            test;
        )
        ИНАЧЕ ЕСЛИ ИСТИНА ТО (
            test;
            test;
            test;
        )
        ИНАЧЕ (
            test;
            test;
            test;
        )
    )
    """
    compiled_proc = compile_string(code)

    proc_obj = compiled_proc.compiled_code.get("test")
    assert isinstance(proc_obj, Procedure)
    when = proc_obj.body.commands[0]

    assert isinstance(when, When)
    assert when.expression.operations is not None
    assert len(when.expression.operations) == 1
    assert when.expression.operations[0].value == Boolean(True).value
    assert len(when.body.commands) == 3

    assert isinstance(when.else_whens, list)
    assert len(when.else_whens) == 1
    assert when.else_whens[0].expression.operations[0].value == Boolean(True).value
    assert len(when.else_whens[0].body.commands) == 3

    assert isinstance(when.else_, Else)
    assert len(when.else_.body.commands) == 3


def test_compile_loop():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЦИКЛ ОТ 1 ДО 100 (
            test;
            test;
            test;
        )
        ЦИКЛ счет ОТ 1 ДО 100 (
            test;
            test;
            test;
        )
    )
    """
    compiled_proc = compile_string(code)

    proc_obj = compiled_proc.compiled_code.get("test")
    assert isinstance(proc_obj, Procedure)
    loop = proc_obj.body.commands[0]

    assert isinstance(loop, Loop)
    assert loop.name_loop_var is None
    assert loop.expression_from.operations[0].value == Number(1).value
    assert loop.expression_to.operations[0].value == Number(100).value
    assert len(loop.body.commands) == 3

    loop_2 = proc_obj.body.commands[1]

    assert isinstance(loop_2, Loop)
    assert loop_2.name_loop_var == "счет"
    assert loop_2.expression_from.operations[0].value == Number(1).value
    assert loop_2.expression_to.operations[0].value == Number(100).value
    assert len(loop_2.body.commands) == 3


def test_compile_while():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ПОКА ИСТИНА (
            test;
            test;
            test;
        )
    )
    """
    compiled_proc = compile_string(code)

    proc_obj = compiled_proc.compiled_code.get("test")
    assert isinstance(proc_obj, Procedure)
    while_ = proc_obj.body.commands[0]

    assert isinstance(while_, While)
    assert len(while_.expression.operations) == 1
    assert while_.expression.operations[0].value == Boolean(True).value
    assert len(while_.body.commands) == 3


def test_compile_context():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        КОНТЕКСТ (
            1 / 0;
            1 / 0;
            1 / 0;
        )
        ОБРАБОТЧИК БазоваяОшибка КАК err (
            test;
            test;
            test;
        )
        ОБРАБОТЧИК БазоваяОшибка КАК err (
            test;
            test;
            test;
        )
    )
    """
    compiled_proc = compile_string(code)

    proc_obj = compiled_proc.compiled_code.get("test")
    assert isinstance(proc_obj, Procedure)
    context = proc_obj.body.commands[0]

    assert isinstance(context, Context)
    assert len(context.body.commands) == 3
    assert len(context.handlers) == 2

    for handler in context.handlers:
        assert isinstance(handler, ExceptionHandler)
        assert len(handler.body.commands) == 3
        assert handler.exception_class_name == "БазоваяОшибка"
        assert handler.exception_inst_name == "err"
