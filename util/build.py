import os
import pickle

from util.ast import AbstractSyntaxTreeBuilder
from util.compile import Compiler
from core.parse.base import MetaObject
from util.starter import preprocess


def build(path: str):
    with open(path, "r", encoding="utf-8") as file:
        code = preprocess(file.read())

        ast_builder = AbstractSyntaxTreeBuilder(code)
        ast: list[MetaObject] = ast_builder.build()

        compiler = Compiler(ast)

        new_path = os.path.splitext(path)[0] + ".law"

        with open(f"{new_path}", 'wb') as f:
            pickle.dump(compiler.compile(), f)
