from typing import Optional

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.atomic import Array
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()


@builder.collect(func_name='массив')
class ArrayInit(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = -1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Array

        return Array(args if args else [])


@builder.collect(func_name='добавить_в_массив')
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


@builder.collect(func_name='удалить_из_массива')
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


@builder.collect(func_name='достать_из_массива')
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


@builder.collect(func_name='изменить_в_массиве')
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


@builder.collect(func_name='длина_массива')
class ArrayLen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[Array]] = None):
        from core.types.atomic import Number
        arr = self.parse_args(args)[0]

        return Number(len(arr))


@builder.collect(func_name='таблица')
class TableInit(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Table, Array
        from core.exceptions import ErrorValue

        if not args:
            return Table({})

        keys, values = args

        if not isinstance(keys, Array) or not isinstance(values, Array):
            raise ErrorValue("Таблица должна быть инициализирована массивами ключей и значений.")

        if len(keys) != len(values):
            raise ErrorValue("Количество ключей и значений не совпадает.")

        return Table({k: v for k, v in zip(keys.value, values.value)})


@builder.collect(func_name='добавить_в_таблицу')
class TableAppend(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 3

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Table, Void, String
        from core.exceptions import ErrorValue

        table, key, value = args

        if not isinstance(key, String):
            raise ErrorValue("Ключ должен быть строкой.")

        if not isinstance(table, Table):
            raise ErrorValue("Первый аргумент должен быть таблицей.")

        table[key] = value

        return Void()


@builder.collect(func_name='извлечь_из_таблицы')
class TableGetValue(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Table, String
        from core.exceptions import ErrorValue

        table, key = args

        if not isinstance(key, String):
            raise ErrorValue("Ключ должен быть строкой.")

        if not isinstance(table, Table):
            raise ErrorValue("Первый аргумент должен быть таблицей.")

        if key not in table:
            raise ErrorValue("Ключ не найден.")

        return table[key]


@builder.collect(func_name='удалить_из_таблицы')
class TableRemove(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Table, String, Void
        from core.exceptions import ErrorValue

        table, key = args

        if not isinstance(key, String):
            raise ErrorValue("Ключ должен быть строкой.")

        if not isinstance(table, Table):
            raise ErrorValue("Первый аргумент должен быть таблицей.")

        if key in table:
            table.del_(key)

        return Void()


@builder.collect(func_name='длина_таблицы')
class TableLen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number, Table
        from core.exceptions import ErrorValue

        table = args[0]

        if not isinstance(table, Table):
            raise ErrorValue("Первый аргумент должен быть таблицей.")

        return Number(len(table))


if __name__ == '__main__':
    builder.build_python_extend("структуры")
