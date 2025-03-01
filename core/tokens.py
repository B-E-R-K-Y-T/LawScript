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
    bool_not_equal = "НЕРАВНО"
    less = "МЕНЬШЕ"
    greater = "БОЛЬШЕ"
    between = "МЕЖДУ"
    data = "ДАННЫЕ"
    procedure = "ПРОЦЕДУРА"
    a_procedure = "ПРОЦЕДУРУ"
    extends = "РАСШИРИТЬ"
    table = "ТАБЛИЦА"
    a_table = "ТАБЛИЦУ"
    assign = "ЗАДАТЬ"
    when = "ЕСЛИ"
    then = "ТО"
    else_ = "ИНАЧЕ"
    loop = "ЦИКЛ"
    from_ = "ОТ"
    to = "ДО"
    while_ = "ПОКА"
    return_ = "ВЕРНУТЬ"
    true = "ИСТИНА"
    false = "ЛОЖЬ"
    continue_ = "ПРОПУСТИТЬ"
    break_ = "ПРЕРВАТЬ"


class ServiceTokens(StrEnum):
    unary_minus = "{{%unary_minus%}}"
    unary_plus = "{{%unary_plus%}}"
    void_arg = "{{%void_arg%}}"


ALL_TOKENS = list(ServiceTokens) + list(Tokens)
NOT_ALLOWED_TOKENS = set(Tokens) - {
    Tokens.comment, Tokens.star, Tokens.left_bracket, Tokens.right_bracket,
    Tokens.left_square_bracket, Tokens.right_square_bracket, Tokens.comma, Tokens.dot,
    Tokens.equal, Tokens.plus, Tokens.minus, Tokens.exponentiation, Tokens.percent,
    Tokens.div, Tokens.end_expr, Tokens.quotation, Tokens.not_,Tokens.and_, Tokens.or_,
    Tokens.bool_equal, Tokens.bool_not_equal, Tokens.less, Tokens.greater, Tokens.true, Tokens.false,
}
