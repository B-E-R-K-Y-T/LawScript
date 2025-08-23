from pathlib import Path
from typing import Optional

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.atomic import Array
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/структуры/"
MOD_NAME = "примитивные_структуры"


@builder.collect(func_name='массив')
class ArrayInit(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = -1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import Array

        return Array(args if args else [])


@builder.collect(func_name='добавить_в_массив')
class ArrayAppend(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 2

    def call(self, args: Optional[list[Array]] = None):
        from src.core.extend.standard_lib.lib_structs.tools import parse_arr_args_two
        from src.core.types.atomic import Void

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
        from src.core.extend.standard_lib.lib_structs.tools import parse_arr_args_two
        from src.core.types.atomic import Void, Number
        from src.core.exceptions import ErrorType, ErrorIndex

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
        from src.core.extend.standard_lib.lib_structs.tools import parse_arr_args_two
        from src.core.types.atomic import Number
        from src.core.exceptions import ErrorType, ErrorIndex

        array, item = parse_arr_args_two(args)

        if isinstance(item, Number) and not item.is_int():
            raise ErrorType("Индекс должен быть целым числом.")

        if not isinstance(item, Number):
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
        from src.core.extend.standard_lib.lib_structs.tools import parse_arr_args_inf
        from src.core.types.atomic import Number, BaseAtomicType
        from src.core.exceptions import ErrorType, ErrorIndex
        from src.core.types.atomic import Void

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
        from src.core.types.atomic import Number, Array
        from src.core.exceptions import ErrorValue

        arr = args[0]

        if not isinstance(arr, Array):
            raise ErrorValue("Аргумент должен быть массивом.")

        return Number(len(arr.value))

@builder.collect(func_name='сортировать_массив')
class ArrayLen(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[Array]] = None):
        from src.core.types.atomic import Array, BaseAtomicType
        from src.core.exceptions import ErrorValue

        arr = args[0]

        if not isinstance(arr, Array):
            raise ErrorValue("Аргумент должен быть массивом.")

        for item in arr.value:
            if isinstance(item, Array):
                raise ErrorValue("Невозможно отсортировать массив в массиве.")

            if not isinstance(item, BaseAtomicType):
                raise ErrorValue("Аргументы массива должны быть атомарными типами.")

        arr.value = sorted(arr.value, key=lambda i: i.value)

        return arr


@builder.collect(func_name='очистить_массив')
class ArrayClear(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[Array]] = None):
        from src.core.types.atomic import Array, Void
        from src.core.exceptions import ErrorValue

        arr = args[0]

        if not isinstance(arr, Array):
            raise ErrorValue("Аргумент должен быть массивом.")

        arr = arr.value
        arr.clear()

        return Void()


@builder.collect(func_name='таблица')
class TableInit(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 2

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import Table, Array
        from src.core.exceptions import ErrorValue

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
        from src.core.types.atomic import Table, Void, String
        from src.core.exceptions import ErrorValue

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
        from src.core.types.atomic import Table, String
        from src.core.exceptions import ErrorValue

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
        from src.core.types.atomic import Table, String, Void
        from src.core.exceptions import ErrorValue

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
        from src.core.types.atomic import Number, Table
        from src.core.exceptions import ErrorValue

        table = args[0]

        if not isinstance(table, Table):
            raise ErrorValue("Первый аргумент должен быть таблицей.")

        return Number(len(table))


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
