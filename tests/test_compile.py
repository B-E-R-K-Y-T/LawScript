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


def test_compile_expr():
    code = """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ bg () (
    )
    
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЗАДАТЬ var = 1 + 2 * 3;
        ЗАДАТЬ bg_var = В ФОНЕ bg();
        ЗАДАТЬ expr1 = (1 + 2) * 3;
        ЗАДАТЬ expr2 = 10 - 5 + 2;
        ЗАДАТЬ expr3 = 2 ^ 3 + 1;
        ЗАДАТЬ expr4 = 10 / 2 * 3;
        ЗАДАТЬ expr5 = -5 + 3;
        ЗАДАТЬ expr6 = ИСТИНА И ЛОЖЬ;
        ЗАДАТЬ expr7 = 5 БОЛЬШЕ 3;
        ЗАДАТЬ expr8 = НЕ ИСТИНА;
        ЗАДАТЬ expr9 = 10 - 3 + 1;
        ЗАДАТЬ expr10 = 2 + 3 * 4 ^ 2;
        ЗАДАТЬ expr11 = (5 - 2) * (3 + 1);
    )
    """
    compiled_proc = compile_string(code)

    proc_obj = compiled_proc.compiled_code.get("test")
    assert isinstance(proc_obj, Procedure)
    expr_var = proc_obj.body.commands[0]

    assert isinstance(expr_var, AssignField)
    assert expr_var.name == "var"
    assert expr_var.expression.raw_expr == "1 + 2 * 3"
    assert expr_var.expression.raw_operations == ["1", "+", "2", "*", "3"]
    assert expr_var.expression.meta_info.num == 6
    assert expr_var.expression.meta_info.raw_line == "ЗАДАТЬ var = 1 + 2 * 3;"
    assert expr_var.meta_info == expr_var.expression.meta_info
    for source_op, test_op in zip(
            expr_var.expression.operations, [Number(1), Number(2), Number(3), Operator("*"), Operator("+")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError

    expr_bg = proc_obj.body.commands[1]

    assert isinstance(expr_bg, AssignField)
    assert expr_bg.name == "bg_var"
    assert expr_bg.expression.raw_expr == "В ФОНЕ bg ( )"
    assert expr_bg.expression.raw_operations == [ServiceTokens.in_background, "bg", "(", ")"]
    assert expr_bg.expression.meta_info.num == 7
    assert expr_bg.expression.meta_info.raw_line == "ЗАДАТЬ bg_var = В ФОНЕ bg();"
    assert expr_bg.meta_info == expr_bg.expression.meta_info
    for source_op, test_op in zip(
            expr_bg.expression.operations,
            [
                Operator(ServiceTokens.void_arg),
                ProcedureContextName(Operator("bg")),
                Operator(ServiceTokens.in_background)
            ]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, ProcedureContextName):
            assert source_op.operator.operator == test_op.operator.operator
        else:
            raise AssertionError
    

    # --- expr1: (1 + 2) * 3 ---
    expr1 = proc_obj.body.commands[2]
    assert isinstance(expr1, AssignField)
    assert expr1.name == "expr1"
    assert expr1.expression.raw_expr == "( 1 + 2 ) * 3"
    assert expr1.expression.raw_operations == ["(", "1", "+", "2", ")", "*", "3"]
    # RPN: 1 2 + 3 *
    for source_op, test_op in zip(
            expr1.expression.operations,
            [Number(1), Number(2), Operator("+"), Number(3), Operator("*")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr2: 10 - 5 + 2 ---
    expr2 = proc_obj.body.commands[3]
    assert isinstance(expr2, AssignField)
    assert expr2.name == "expr2"
    assert expr2.expression.raw_expr == "10 - 5 + 2"
    assert expr2.expression.raw_operations == ["10", "-", "5", "+", "2"]
    # RPN: 10 5 - 2 +
    for source_op, test_op in zip(
            expr2.expression.operations,
            [Number(10), Number(5), Operator("-"), Number(2), Operator("+")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr3: 2 ^ 3 + 1 ---
    expr3 = proc_obj.body.commands[4]
    assert isinstance(expr3, AssignField)
    assert expr3.name == "expr3"
    assert expr3.expression.raw_expr == "2 ^ 3 + 1"
    assert expr3.expression.raw_operations == ["2", "^", "3", "+", "1"]
    # RPN: 2 3 ^ 1 + (возведение в степень имеет высший приоритет)
    for source_op, test_op in zip(
            expr3.expression.operations,
            [Number(2), Number(3), Operator("^"), Number(1), Operator("+")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr4: 10 / 2 * 3 ---
    expr4 = proc_obj.body.commands[5]
    assert isinstance(expr4, AssignField)
    assert expr4.name == "expr4"
    assert expr4.expression.raw_expr == "10 / 2 * 3"
    assert expr4.expression.raw_operations == ["10", "/", "2", "*", "3"]
    # RPN: 10 2 / 3 *
    for source_op, test_op in zip(
            expr4.expression.operations,
            [Number(10), Number(2), Operator("/"), Number(3), Operator("*")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr5: -5 + 3 (унарный минус) ---
    expr5 = proc_obj.body.commands[6]
    assert isinstance(expr5, AssignField)
    assert expr5.name == "expr5"
    assert expr5.expression.raw_expr == "- 5 + 3"
    # RPN: 5 unary_minus 3 +
    for source_op, test_op in zip(
            expr5.expression.operations,
            [Number(5), Operator("-"), Number(3), Operator("+")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr6: ИСТИНА И ЛОЖЬ ---
    expr6 = proc_obj.body.commands[7]
    assert isinstance(expr6, AssignField)
    assert expr6.name == "expr6"
    assert expr6.expression.raw_expr == "ИСТИНА И ЛОЖЬ"
    assert expr6.expression.raw_operations == ["ИСТИНА", "И", "ЛОЖЬ"]
    # RPN: true false and
    for source_op, test_op in zip(
            expr6.expression.operations,
            [Boolean(True), Boolean(False), Operator("И")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr7: 5 БОЛЬШЕ 3 ---
    expr7 = proc_obj.body.commands[8]
    assert isinstance(expr7, AssignField)
    assert expr7.name == "expr7"
    assert expr7.expression.raw_expr == "5 БОЛЬШЕ 3"
    assert expr7.expression.raw_operations == ["5", "БОЛЬШЕ", "3"]
    # RPN: 5 3 >
    for source_op, test_op in zip(
            expr7.expression.operations,
            [Number(5), Number(3), Operator("БОЛЬШЕ")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr8: НЕ ИСТИНА ---
    expr8 = proc_obj.body.commands[9]
    assert isinstance(expr8, AssignField)
    assert expr8.name == "expr8"
    assert expr8.expression.raw_expr == "НЕ ИСТИНА"
    assert expr8.expression.raw_operations == ["НЕ", "ИСТИНА"]
    # RPN: true not
    for source_op, test_op in zip(
            expr8.expression.operations,
            [Boolean(True), Operator("НЕ")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr9: 10 - 3 + 1 ---
    expr9 = proc_obj.body.commands[10]
    assert isinstance(expr9, AssignField)
    assert expr9.name == "expr9"
    assert expr9.expression.raw_expr == "10 - 3 + 1"
    assert expr9.expression.raw_operations == ["10", "-", "3", "+", "1"]
    # RPN: 10 3 - 1 +
    for source_op, test_op in zip(
            expr9.expression.operations,
            [Number(10), Number(3), Operator("-"), Number(1), Operator("+")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr10: 2 + 3 * 4 ^ 2 ---
    expr10 = proc_obj.body.commands[11]
    assert isinstance(expr10, AssignField)
    assert expr10.name == "expr10"
    assert expr10.expression.raw_expr == "2 + 3 * 4 ^ 2"
    assert expr10.expression.raw_operations == ["2", "+", "3", "*", "4", "^", "2"]
    # RPN: 2 3 4 2 ^ * +
    for source_op, test_op in zip(
            expr10.expression.operations,
            [Number(2), Number(3), Number(4), Number(2), Operator("^"), Operator("*"), Operator("+")]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")

    # --- expr11: (5 - 2) * (3 + 1) ---
    expr11 = proc_obj.body.commands[12]
    assert isinstance(expr11, AssignField)
    assert expr11.name == "expr11"
    assert expr11.expression.raw_expr == "( 5 - 2 ) * ( 3 + 1 )"
    assert expr11.expression.raw_operations == ["(", "5", "-", "2", ")", "*", "(", "3", "+", "1", ")"]
    # RPN: 5 2 - 3 1 + *
    for source_op, test_op in zip(
            expr11.expression.operations,
            [
                Number(5), Number(2), Operator("-"),
                Number(3), Number(1), Operator("+"),
                Operator("*")
            ]
    ):
        if isinstance(source_op, Operator):
            assert source_op.operator == test_op.operator
        elif isinstance(source_op, BaseAtomicType):
            assert source_op.value == test_op.value
        else:
            raise AssertionError(f"Unexpected type: {type(source_op)}")


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
