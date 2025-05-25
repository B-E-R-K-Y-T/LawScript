from typing import Optional

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.atomic import Array
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()


@builder.collect(func_name='array')
class ArrayInit(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = -1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Array

        return Array(args if args else [])


@builder.collect(func_name='arr_append')
class ArrayAppend(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[Array]] = None):
        from core.extend.standard_lib.structs.tools import parse_arr_args_two
        from core.types.atomic import Void

        array, item = parse_arr_args_two(args)
        array.append(item)

        return Void()


@builder.collect(func_name='arr_remove')
class ArrayRemove(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[Array]] = None):
        from core.extend.standard_lib.structs.tools import parse_arr_args_two
        from core.types.atomic import Void, Number
        from core.exceptions import ErrorType, ErrorIndex

        array, item = parse_arr_args_two(args)

        if not isinstance(item, Number) and item.is_int():
            raise ErrorType("Индекс должен быть целым числом.")

        try:
            array.remove(item)
        except IndexError:
            raise ErrorIndex("Выход за границы массива.")

        return Void()


@builder.collect(func_name='arr_get_item')
class ArrayGetItem(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[Array]] = None):
        from core.extend.standard_lib.structs.tools import parse_arr_args_two
        from core.types.atomic import Number
        from core.exceptions import ErrorType, ErrorIndex

        array, item = parse_arr_args_two(args)

        if not isinstance(item, Number) and item.is_int():
            raise ErrorType("Индекс должен быть целым числом.")

        try:
            return array[item.value]
        except IndexError:
            raise ErrorIndex("Выход за границы массива.")


@builder.collect(func_name='arr_set_item')
class ArraySetItem(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 3

    def call(self, args: Optional[list[Array]] = None):
        from core.extend.standard_lib.structs.tools import parse_arr_args_inf
        from core.types.atomic import Number, BaseAtomicType
        from core.exceptions import ErrorType, ErrorIndex
        from core.types.atomic import Void

        array, arr_args = parse_arr_args_inf(args)
        index, value = arr_args

        if not isinstance(index, Number) and index.is_int():
            raise ErrorType("Индекс должен быть целым числом.")

        if not isinstance(value, BaseAtomicType):
            raise ErrorType("Значение должно быть атомарного типа.")

        try:
            array[index.value] = value
        except IndexError:
            raise ErrorIndex("Выход за границы массива.")

        return Void()


@builder.collect(func_name='arr_len')
class ArrayLen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[Array]] = None):
        from core.types.atomic import Number
        arr = self.parse_args(args)[0]

        return Number(len(arr))


if __name__ == '__main__':
    builder.build_python_extend("structs")
