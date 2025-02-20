import os
import pickle

from util.build_tools.ast import AbstractSyntaxTreeBuilder
from util.build_tools.compile import Compiler
from core.parse.base import MetaObject
from util.build_tools.starter import preprocess


def build(path: str):
    with open(path, "r", encoding="utf-8") as read_file:
        code = preprocess(read_file.read(), path)

        ast_builder = AbstractSyntaxTreeBuilder(code)
        ast: list[MetaObject] = ast_builder.build()

        compiler = Compiler(ast)

        new_path = os.path.splitext(path)[0] + ".law"

        with open(f"{new_path}", 'wb') as write_file:
            pickle.dump(compiler.compile(), write_file)
