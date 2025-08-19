from core.exceptions import ErrorType
from core.extend.function_wrap import PyExtendWrapper
from core.types.atomic import Array, BaseAtomicType
from core.types.base_declarative_type import BaseDeclarativeType
from core.types.procedure import Procedure, LinkedProcedure


_ALLOW_TYPES = (BaseAtomicType, BaseDeclarativeType, Procedure, PyExtendWrapper, LinkedProcedure)

def parse_arr_args_two(args):
    array = args[0]

    if not isinstance(array, Array):
        raise ErrorType("Аргумент должен быть массивом!")

    item = args[1]

    if not isinstance(item, _ALLOW_TYPES):
        raise ErrorType("В массив можно добавить только типы данных!")

    return array, item


def parse_arr_args_inf(args):
    array = args[0]

    if not isinstance(array, Array):
        raise ErrorType("Аргумент должен быть массивом!")

    item = args[1:]

    for i in item:
        if not isinstance(i, _ALLOW_TYPES):
            raise ErrorType("В массив можно добавить только типы данных!")

    return array, item
