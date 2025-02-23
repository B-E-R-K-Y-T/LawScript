from enum import StrEnum


class Tokens(StrEnum):
    comment = "#"
    star = "*"
    left_bracket = "("
    right_bracket = ")"
    left_square_bracket = "["
    right_square_bracket = "]"
    comma = ","
    dot = "."
    equal = "="
    plus = "+"
    minus = "-"
    exponentiation = "^"
    percent = "%"
    div = "/"
    end_expr = ";"
    quotation = "\""
    define = "ОПРЕДЕЛИТЬ"
    print_ = "НАПЕЧАТАТЬ"
    types = "ТИПЫ"
    degree = "СТЕПЕНЬ"
    of_rigor = "СТРОГОСТИ"
    of_sanction = "САНКЦИЮ"
    sanction = "САНКЦИЯ"
    procedural = "ПРОЦЕССУАЛЬНЫЙ"
    aspect = "АСПЕКТ"
    hypothesis = "ГИПОТЕЗА"
    subject = "СУБЪЕКТ"
    object = "ОБЪЕКТ"
    condition = "УСЛОВИЕ"
    article = "СТАТЬЯ"
    create = "СОЗДАТЬ"
    document = "ДОКУМЕНТ"
    disposition = "ДИСПОЗИЦИЯ"
    law = "ПРАВО"
    duty = "ОБЯЗАННОСТЬ"
    rule = "ПРАВИЛО"
    include = "ВКЛЮЧИТЬ"
    the_actual = "ФАКТИЧЕСКУЮ"
    the_situation = "СИТУАЦИЮ"
    actual = "ФАКТИЧЕСКАЯ"
    situation = "СИТУАЦИЯ"
    check = "ПРОВЕРКА"
    description = "ОПИСАНИЕ"
    name = "ИМЯ"
    criteria = "КРИТЕРИИ"
    only = "ТОЛЬКО"
    not_ = "НЕ"
    may = "МОЖЕТ"
    be = "БЫТЬ"
    and_ = "И"
    or_ = "ИЛИ"
    bool_equal = "РАВНО"
    less = "МЕНЬШЕ"
    greater = "БОЛЬШЕ"
    between = "МЕЖДУ"
    data = "ДАННЫЕ"
    procedure = "ПРОЦЕДУРА"
    a_procedure = "ПРОЦЕДУРУ"
    assign = "ЗАДАТЬ"
    when = "ЕСЛИ"
    then = "TO"
    else_ = "ИНАЧЕ"
    loop = "ЦИКЛ"
    from_ = "ОТ"
    to = "ДО"
    a_condition = "УСЛОВИЕМ"
    with_ = "С"
    return_ = "ВЕРНУТЬ"
    true = "ИСТИНА"
    false = "ЛОЖЬ"

    _unary_minus = "{{%unary_minus%}}"
    _unary_plus = "{{%unary_plus%}}"
