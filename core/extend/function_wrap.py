from abc import ABC, abstractmethod
from typing import Optional, Type

import dill

from config import settings
from core.exceptions import BaseError, ArgumentError
from core.types.atomic import Array
from core.types.basetype import BaseAtomicType, BaseType
from core.types.line import Info


class PyExtendWrapper(BaseType, ABC):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.func_name = func_name
        self.empty_args = False
        self.count_args = -1
        self.offset_required_args = -1

    @abstractmethod
    def call(self, args: Optional[list[BaseAtomicType]] = None) -> BaseAtomicType: ...

    def check_args(self, args: Optional[list[BaseAtomicType]] = None):
        if not self.empty_args and args is None:
            raise ArgumentError(f"Необходимо передать аргументы в процедуру '{self.func_name}'")

        if self.count_args == 0 and args is None:
            return

        elif self.offset_required_args > 0:
            if len(args) < self.offset_required_args:
                raise ArgumentError(
                    f"Неверное количество аргументов процедуры '{self.func_name}'. "
                    f"Ожидалось минимум: {self.offset_required_args}, "
                    f"но передано: {len(args)}"
                )

            if len(args) > self.count_args != -1:
                raise ArgumentError(
                    f"Неверное количество аргументов процедуры '{self.func_name}'. Ожидалось максимум: {self.count_args}, "
                    f"но передано: {len(args)}"
                )

        elif self.count_args != -1:
            if len(args) != self.count_args:
                raise ArgumentError(
                    f"Неверное количество аргументов процедуры '{self.func_name}'. Ожидалось: {self.count_args}, "
                    f"но передано: {len(args)}"
                )

    def parse_args(self, args: Optional[list[BaseAtomicType]] = None) -> list:
        if args is None:
            return []

        result = []

        for arg in args:
            if not isinstance(arg, BaseAtomicType):
                raise ArgumentError(f"Аргумент '{arg}' не является экземпляром типа: '{BaseAtomicType.__name__}'")

            if isinstance(arg, Array):
                def _parse_array(array: Array) -> list:
                    new_array = []

                    for idx, item in enumerate(array.value):
                        if isinstance(item, Array):
                            new_array.append(_parse_array(item))

                        elif isinstance(item, BaseAtomicType):
                            new_array.append(item.value)

                        else:
                            new_array.append(item)

                    return new_array

                result.append(_parse_array(arg))
                continue

            result.append(arg.value)

        if self.offset_required_args != -1 and len(args) < self.count_args:
            for _ in range(len(args) - self.offset_required_args + 1):
                result.append(None)

        return result

    def __repr__(self):
        return (
            f"Процедура('{self.func_name}') "
            f"кол-во аргументов: {self.count_args if self.count_args != -1 else 'неограниченное'}"
        )


class CallableWrapper:
    def __init__(self):
        self.mod_name: Optional[str] = None
        self.meta_info: Optional[Info] = None

    def callable_py_wrap(self, func, func_name: str):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if settings.debug:
                    raise

                raise BaseError(
                    f"При выполнении процедуры '{func_name}' в модуле: '{self.mod_name}' произошла ошибка: '{e}'"
                )

        return wrapper


class PyExtendBuilder:
    def __init__(self):
        self.wrappers: list[PyExtendWrapper] = []
        self.callable_wrapper: CallableWrapper = CallableWrapper()

    def collect(self, func_name: str):
        def decorator(py_wrapper: Type[PyExtendWrapper]):
            py_wrapper.call = self.callable_wrapper.callable_py_wrap(py_wrapper.call, func_name)
            instance_py_wrapper = py_wrapper(func_name)

            self.wrappers.append(instance_py_wrapper)

            return instance_py_wrapper

        return decorator

    def build_python_extend(self, extend_path: str):
        from util.build_tools.compile import Compiled

        extend_path = f"{extend_path}.{settings.py_extend_postfix}"
        self.callable_wrapper.mod_name = extend_path

        compiled = Compiled({wrapper.func_name: wrapper for wrapper in self.wrappers})

        with open(extend_path, 'wb') as write_file:
            dill.dump(compiled, write_file)
