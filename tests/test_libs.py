import pytest

from src.core.types.atomic import convert_atomic_type_to_py_type, Boolean
from tests.conftest import run_procedure_for_test


code_template = """
ВКЛЮЧИТЬ стандартная_библиотека.*


ОПРЕДЕЛИТЬ ПРОЦЕДУРУ test () (
    ЗАДАТЬ знач = {value};

    ВЕРНУТЬ в_логический(знач);
)
"""

test_data = [
    # --- Булевы значения (прямое преобразование) ---
    ("ИСТИНА", Boolean, True),
    ("ЛОЖЬ", Boolean, False),

    # --- Числа ---
    ("1", Boolean, True),
    ("0", Boolean, False),
    ("42", Boolean, True),
    ("-1", Boolean, True),
    ("0.0", Boolean, False),
    ("3.14", Boolean, True),

    # --- Строки ---
    ('"текст"', Boolean, True),
    ('""', Boolean, False),
    ('" "', Boolean, True),
    ('"False"', Boolean, True),
    ('"0"', Boolean, True),

    # --- Массивы ---
    ("массив()", Boolean, False),
    ("массив(1, 2, 3)", Boolean, True),
    ("массив(0)", Boolean, True),
    ("массив(массив())", Boolean, True),

    # --- Таблицы ---
    ("таблица()", Boolean, False),
    ('таблица(массив("ключ"), массив(42))', Boolean, True),
    ('таблица(массив("ключ"), массив(0))', Boolean, True),

    # --- Выражения ---
    ("5 БОЛЬШЕ 3", Boolean, True),
    ("1 + 1 РАВНО 2", Boolean, True),
    ("ИСТИНА И ЛОЖЬ", Boolean, False),
    ("НЕ ИСТИНА", Boolean, False),
    ("НЕ 0", Boolean, True),
    ("НЕ \"\"", Boolean, True),
]


@pytest.mark.parametrize("value,expected_type,expected_value", test_data)
def test_cast_to_bool(value, expected_type, expected_value):
    code = code_template.format(value=value)
    result = run_procedure_for_test(code, "test")

    assert isinstance(result, expected_type), \
        f"Expected type Boolean, got {type(result).__name__}"

    result_py = convert_atomic_type_to_py_type(result)
    expected_py = convert_atomic_type_to_py_type(expected_type(expected_value))

    assert result_py == expected_py, \
        f"Expected value {expected_py!r}, got {result_py!r}"
