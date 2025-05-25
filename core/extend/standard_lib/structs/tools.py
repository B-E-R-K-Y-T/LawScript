from core.exceptions import ErrorType
from core.types.atomic import Array, BaseAtomicType


def parse_arr_args_two(args):
    array = args[0]

    if not isinstance(array, Array):
        raise ErrorType("Аргумент должен быть массивом!")

    item = args[1]

    if not isinstance(item, BaseAtomicType):
        raise ErrorType("В массив можно добавить только типы данных!")

    return array, item


def parse_arr_args_inf(args):
    array = args[0]

    if not isinstance(array, Array):
        raise ErrorType("Аргумент должен быть массивом!")

    item = args[1:]

    for i in item:
        if not isinstance(i, BaseAtomicType):
            raise ErrorType("В массив можно добавить только типы данных!")

    return array, item
