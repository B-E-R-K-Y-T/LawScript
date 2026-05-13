from src.core.executors.procedure import ProcedureExecutor

from src.core.types.procedure import Procedure
from src.core.types.variable import ScopeStack
from src.util.build_tools.starter import compile_string



def run_procedure_for_test(code: str, name_proc: str = "test"):
    compiled_code = compile_string(code)
    procedure: Procedure = compiled_code.compiled_code.get(name_proc)
    procedure.tree_variables = ScopeStack()
    return ProcedureExecutor(procedure, compiled_code).execute()
