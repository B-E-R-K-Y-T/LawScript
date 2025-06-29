import dill

from config import settings
from core.parse.base import MetaObject
from core.util import kill_process
from util.build_tools.ast import AbstractSyntaxTreeBuilder
from util.build_tools.compile import Compiler, Compiled
from util.build_tools.interpreter import Interpreter
from util.build_tools.preprocessing import preprocess


def compile_string(raw_code: str) -> Compiled:
    code = preprocess(raw_code, "")

    ast_builder = AbstractSyntaxTreeBuilder(code)
    ast: list[MetaObject] = ast_builder.build()

    compiler = Compiler(ast)
    return compiler.compile()


def run_compiled_code(compiled: Compiled):
    interpreter = Interpreter(compiled)
    interpreter.run()


def run(raw_code: str, path: str):
    code = preprocess(raw_code, path)

    ast_builder = AbstractSyntaxTreeBuilder(code)
    ast: list[MetaObject] = ast_builder.build()

    compiler = Compiler(ast)
    run_compiled_code(compiler.compile())


def run_string(raw_code: str):
    run(raw_code, "")


def run_file(path: str):
    try:
        if path.endswith(f'.{settings.compiled_postfix}'):
            with open(path, "rb") as file:
                compiled = dill.load(file)
                run_compiled_code(compiled)
        elif path.endswith(f'.{settings.py_extend_postfix}'):
            with open(path, "rb") as file:
                compiled = dill.load(file)
                run_compiled_code(compiled)
        elif path.endswith(f'.{settings.raw_postfix}'):
            with open(path, "r", encoding="utf-8") as file:
                run(file.read(), path)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        kill_process(f"Файл '{path}' не найден.")
