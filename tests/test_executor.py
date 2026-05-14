import pytest

from src.core.background_task.task import ProcedureBackgroundTask
from src.core.types.atomic import (
    convert_atomic_type_to_py_type,
    Number,
    Boolean,
    Array,
    String,
    Table,
)
from tests.conftest import run_procedure_for_test

code_template = """
ВКЛЮЧИТЬ стандартная_библиотека.*


ОПРЕДЕЛИТЬ ПРОЦЕДУРУ bg () (
    ВЕРНУТЬ 2;
)

ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
    ВЕРНУТЬ {expression};
)
"""

test_data = [
    # --- Арифметика ---
    ("1 + 2 * 3", Number, 7),
    ("10 - 5 + 2", Number, 7),
    ("2 ^ 3 + 1", Number, 9),
    ("10 / 2 * 3", Number, 15),
    ("-5 + 3", Number, -2),
    ("(5 - 2) * (3 + 1)", Number, 12),
    ("2 + 3 * 4 ^ 2", Number, 50),

    # --- Логика и сравнения ---
    ("(ИСТИНА ИЛИ ИСТИНА) РАВНО ИСТИНА", Boolean, True),
    ("ИСТИНА И ЛОЖЬ", Boolean, False),
    ("5 БОЛЬШЕ 3", Boolean, True),
    ("НЕ ИСТИНА", Boolean, False),
    ("1 + 1 РАВНО 2", Boolean, True),
    ("5 НЕРАВНО 3", Boolean, True),
    ("НЕ \"\" И 0", Boolean, False),
    ("НЕ (НЕ \"\" И 0)", Boolean, True),

    # --- Вложенные массивы ---
    ("массив(массив(массив(1), массив(2)))", Array, [[[1], [2]]]),
    ("массив(1, 2, 3)", Array, [1, 2, 3]),
    ("массив(массив(), массив(), массив())", Array, [[], [], []]),

    # --- Таблицы (словари) ---
    ("таблица()", Table, {}),
    ("таблица(массив(\"ключ\"), массив(42))", Table, {"ключ": 42}),
    ("таблица(массив(\"ключ\"), массив(массив(массив(массив(1), массив(2)))))", Table, {"ключ": [[[1], [2]]]}),

    # --- Строки ---
    ("\"Привет, Мир!\"", String, "Привет, Мир!"),
    ("форматировать_строку(\"{}, {}!\", \"Привет\", \"Мир\")", String, "Привет, Мир!"),

    # --- Сложные выражения ---
    (
        "таблица("
        "массив(форматировать_строку(\"{}-{}\", 1, 2) * 2), "
        "массив(массив(массив(массив(2 + 2 * ЖДАТЬ В ФОНЕ bg()), массив(таблица(массив(\"ключ\"), массив(массив(массив(массив(1), массив(НЕ ((ИСТИНА ИЛИ ИСТИНА) РАВНО ИСТИНА))))))))))"
        ")",
        Table, {"1-21-2": [[[6], [{"ключ": [[[1], [False]]]}]]]}
    ),
    (
        """таблица(
        массив(
            форматировать_строку(
                "{}-{}",
                1,
                2,
            ) * 2,
        ),
        массив(
            массив(
                массив(
                    массив(
                        2 + 2 * ЖДАТЬ В ФОНЕ bg(),
                    ),
                    массив(
                        таблица(
                            массив("ключ"),
                            массив(
                                массив(
                                    массив(
                                        массив(1),
                                        массив(
                                            НЕ ((ИСТИНА ИЛИ ИСТИНА) РАВНО ИСТИНА),
                                        )
                                    ),
                                )
                            ),
                        )
                    ),
                )
            ),
        )
    )""",
        Table, {"1-21-2": [[[6], [{"ключ": [[[1], [False]]]}]]]}
    ),
    (
        """массив(
            массив(
                (10 + 10) * 0,
            ),
            массив(
                (10 + 10) * 0,
            ),
            массив(
                массив(
                    массив(
                        (10 + 10) * 0,
                    ),
                    массив(
                        (10 + 10) * 0,
                    ),
                    массив(
                        (10 + 10) * 0,
                    ),
                )
            ),
        )""",
        Array, [[0], [0], [[[0], [0], [0]]]]
    ),
]


@pytest.mark.parametrize("expression,expected_type,expected_value", test_data)
def test_execute_expr(expression, expected_type, expected_value):
    code = code_template.format(expression=expression)
    result = run_procedure_for_test(code, "test")

    assert isinstance(result, expected_type), \
        f"Expected type {expected_type.__name__}, got {type(result).__name__}"

    result_py = convert_atomic_type_to_py_type(result)
    expected_py = convert_atomic_type_to_py_type(expected_type(expected_value))

    assert result_py == expected_py, \
        f"Expected value {expected_py!r}, got {result_py!r}"


def test_background_task_execution():
    code = """
    ВКЛЮЧИТЬ стандартная_библиотека.*

    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ bg () (
    )

    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ВЕРНУТЬ В ФОНЕ bg();
    )
    """

    result = run_procedure_for_test(code, "test")

    assert isinstance(result, ProcedureBackgroundTask), \
        f"Expected ProcedureBackgroundTask, got {type(result).__name__}"

    assert result.name == "bg", \
        f"Expected task name 'bg', got '{result.name}'"

    assert not result.done, \
        "Background task should not be done immediately without waiting"


def test_classes_execution():
    code = """
    ВКЛЮЧИТЬ стандартная_библиотека.*

    ОПРЕДЕЛИТЬ КЛАСС Базовый (
        ОПРЕДЕЛИТЬ КОНСТРУКТОР (ссылка) () (
            ссылка:а = 1;
        )
        ОПРЕДЕЛИТЬ МЕТОД (ссылка) метод (а, б) (
            НАПЕЧАТАТЬ форматировать_строку("{}, {}, {}", ссылка:а, а, б);
            ВЕРНУТЬ ссылка:а + а + б;
        )
    )
    
    ОПРЕДЕЛИТЬ КЛАСС Наследник НАСЛЕДОВАТЬ ОТ  Базовый(
        ОПРЕДЕЛИТЬ КОНСТРУКТОР (ссылка) () (
            ссылка:__родитель__:__конструктор__();
        )
    )
    
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
        ЗАДАТЬ н = Наследник();
        
        ВЕРНУТЬ ЖДАТЬ В ФОНЕ н:метод(1, 2);
    )
    """

    result = run_procedure_for_test(code, "test")


    assert isinstance(result, Number), \
        f"Expected type Number, got {type(result).__name__}"

    result_py = convert_atomic_type_to_py_type(result)
    expected_py = 4

    assert result_py == expected_py, \
        f"Expected value {expected_py!r}, got {result_py!r}"
