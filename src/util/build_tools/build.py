import os

import dill

from config import settings
from src.core.docs_generate.generator import DocsGenerator
from src.util.build_tools.ast import AbstractSyntaxTreeBuilder
from src.util.build_tools.compile import Compiler
from src.core.parse.base import MetaObject
from src.util.build_tools.starter import preprocess


def build(path: str):
    with open(path, "r", encoding="utf-8") as read_file:
        code = preprocess(read_file.read(), path)

        ast_builder = AbstractSyntaxTreeBuilder(code)
        ast: list[MetaObject] = ast_builder.build()

        compiler = Compiler(ast)
        compiled = compiler.compile()

    new_path = f"{os.path.splitext(path)[0]}.{settings.compiled_postfix}"

    with open(f"{new_path}", 'wb') as write_file:
        dill.dump(compiled, write_file)

    generate_docs(path, compiled)


def generate_docs(path: str, compiled):
    docs_gen = DocsGenerator()
    docs_gen.prepare_code(compiled)
    docs_path = f"{os.path.splitext(path)[0]}_docs.html"
    docs_gen.generate(docs_path, module=os.path.basename(path).split('.')[0])
