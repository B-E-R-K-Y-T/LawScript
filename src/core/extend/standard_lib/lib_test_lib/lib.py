from typing import Optional

from pathlib import Path
from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.atomic import String, Number, Boolean, Array, Table
from src.core.types.basetype import BaseAtomicType
from src.core.types.procedure import Procedure

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/_/"
MOD_NAME = "test_lib"


@builder.collect(func_name='_test_extend_proc_signature')
class TestExtendProc(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.signature = (
            String,
            Number,
            Boolean,
            Array,
            Table,
            Procedure,
        )
        self.count_args = len(self.signature)

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import VOID

        return VOID


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
