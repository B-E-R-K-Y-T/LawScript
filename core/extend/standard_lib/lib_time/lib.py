from typing import Optional
import time

from core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()


@builder.collect(func_name='временная_метка')
class Time(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = True
        self.count_args = 0

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from core.types.atomic import Number

        return Number(time.time())


if __name__ == '__main__':
    builder.build_python_extend("время")
