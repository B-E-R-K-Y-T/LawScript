from src.core.executors.procedure import ProcedureExecutor
from src.core.types.basetype import BaseAtomicType

from src.core.types.procedure import Procedure
from src.core.types.variable import ScopeStack, Variable
from src.util.build_tools.starter import compile_string


def run_procedure_for_test(code: str, name_proc: str = "test", args: dict[str, BaseAtomicType] = None) -> BaseAtomicType:
    compiled_code = compile_string(code)
    procedure: Procedure = compiled_code.compiled_code.get(name_proc)
    procedure.tree_variables = ScopeStack()

    if args is not None:
        for name, value in args.items():
            procedure.tree_variables.set(Variable(name, value))

    return ProcedureExecutor(procedure, compiled_code).execute()
