import os
import pickle
import re
from typing import Optional, Union

from core.parse.base import MetaObject
from core.tokens import Tokens
from core.types.line import Line
from core.util import kill_process
from util.ast import AbstractSyntaxTreeBuilder
from util.compile import Compiler, Compiled
from util.interpreter import Interpreter


def import_preprocess(path, byte_mode: Optional[bool] = True) -> Union[Compiled, str]:
    try:
        if byte_mode:
            with open(path, "rb") as file:
                compiled = pickle.load(file)
                return compiled

        with open(path, "r", encoding="utf-8") as file:
            raw_code = file.read()
            return raw_code

    except FileNotFoundError:
        kill_process(f"Модуль для включения не найден: {path}")
    except RecursionError:
        kill_process(f"Обнаружен циклический импорт {path}")


def preprocess(raw_code, path: str) -> list:
    prepared_code = [line.strip() for line in raw_code.split("\n")]

    code = []

    for offset, line in enumerate(prepared_code):
        code.append(Line(line.strip(), num=offset+1, file=path))

    preprocessed = []

    for line in code:
        match line.split(" "):
            case [Tokens.include, path] if path.endswith(Tokens.star):
                # Удаляем * из пути и получаем директорию
                dir_path = path[:-1].replace(Tokens.dot, "/")
                try:
                    files = os.listdir(dir_path)
                except FileNotFoundError:
                    kill_process(f"Модуль для включения не найден: {path}")
                    return

                for filename in files:
                    if filename.endswith(".law"):  # Проверка на нужное расширение
                        file_path = os.path.join(dir_path, filename)
                        preprocessed.append(import_preprocess(file_path))

            case [Tokens.include, path] if re.search(r'\.\S+$', path):
                path = path.replace(".", "/", path.count(".") - 1)
                try:
                    preprocessed.extend(preprocess(import_preprocess(path, byte_mode=False)))
                except RecursionError:
                    kill_process(f"Обнаружен циклический импорт {path}")

            case [Tokens.include, path]:
                path = path.replace(Tokens.dot, "/")
                path = f"{path}.law"
                preprocessed.append(import_preprocess(path))

            case _:
                preprocessed.append(line)

    return [line for line in preprocessed if line]


def run_compiled_code(compiled: Compiled):
    interpreter = Interpreter(compiled)
    interpreter.run()


def run(raw_code: str, path: str):
    code = preprocess(raw_code, path)

    ast_builder = AbstractSyntaxTreeBuilder(code)
    ast: list[MetaObject] = ast_builder.build()

    compiler = Compiler(ast)
    run_compiled_code(compiler.compile())


def run_file(path: str):
    if path.endswith('.law'):
        with open(path, "rb") as file:
            compiled = pickle.load(file)
            run_compiled_code(compiled)
    else:
        with open(path, "r", encoding="utf-8") as file:
            run(file.read(), path)
