from abc import ABC, abstractmethod
from typing import Optional, Type

import dill

from config import settings
from core.exceptions import BaseError
from core.types.basetype import BaseAtomicType, BaseType


class PyExtendWrapper(BaseType, ABC):
    def __init__(self, func_name: str, ):
        super().__init__(func_name)
        self.func_name = func_name

    @abstractmethod
    def call(self, args: Optional[list[BaseAtomicType]] = None) -> BaseAtomicType: ...

    @staticmethod
    def parse_args(args: Optional[list[BaseAtomicType]] = None) -> list:
        if args is None:
            return []

        result = []

        for arg in args:
            result.append(arg.value)

        return result


class CallableWrapper:
    def __init__(self):
        self.mod_name: Optional[str] = None

    def callable_py_wrap(self, func, func_name: str):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if settings.debug:
                    raise Exception(repr(e))

                raise BaseError(
                    f"При выполнении функции '{func_name}' в модуле: '{self.mod_name}' произошла ошибка: '{e}'"
                )

        return wrapper


class PyExtendBuilder:
    def __init__(self):
        self.wrappers: list[PyExtendWrapper] = []
        self.callable_wrapper: CallableWrapper = CallableWrapper()

    def collect(self, func_name: str):
        def decorator(py_wrapper: Type[PyExtendWrapper]):
            py_wrapper.call = self.callable_wrapper.callable_py_wrap(py_wrapper.call, func_name)

            self.wrappers.append(py_wrapper(func_name))

            return py_wrapper

        return decorator

    def build_python_extend(self, extend_path: str):
        from util.build_tools.compile import Compiled

        extend_path = f"{extend_path}.{settings.py_extend_postfix}"
        self.callable_wrapper.mod_name = extend_path

        compiled = Compiled({wrapper.func_name: wrapper for wrapper in self.wrappers})

        with open(extend_path, 'wb') as write_file:
            dill.dump(compiled, write_file)
