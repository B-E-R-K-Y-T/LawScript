from enum import StrEnum


class Token(StrEnum):
    comment = "#"
    start_body = "("
    end_body = ")"
    comma = ","
    quotation = "\""
    define = "ОПРЕДЕЛИТЬ"
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
    criteria = "КРИЕТРИИ"
    only = "ТОЛЬКО"
    not_ = "НЕ"
    may = "МОЖЕТ"
    be = "БЫТЬ"
    and_ = "И"
    less = "МЕНЬШЕ"
    greater = "БОЛЬШЕ"
    between = "МЕЖДУ"
    data = "ДАННЫЕ"
