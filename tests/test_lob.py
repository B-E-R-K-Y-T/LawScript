from typing import Optional

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"./"
MOD_NAME = "тест_run_procedure"


@builder.collect(func_name='test_run_procedure')
class Input(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = -1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.procedure import Procedure
        proc, *lw_args = args

        if not isinstance(proc, Procedure):
            raise Exception

        return self.run_procedure(proc, list(lw_args))


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
