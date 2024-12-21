import os
import pickle

from core.parse.base import Metadata
from core.token import Token
from core.util import kill_process
from util.ast import AbstractSyntaxTreeBuilder
from util.compile import Compiler, Compiled
from util.interpreter import Interpreter


def import_preprocess(path) -> Compiled:
    try:
        with open(path, "rb") as file:
            compiled = pickle.load(file)
            return compiled
    except FileNotFoundError:
        kill_process(f"Модуль для включения не найден: {path}")
    except RecursionError:
        kill_process(f"Обнаружен циклический импорт {path}")


def preprocess(raw_code) -> list:
    raw_code = [line.strip() for line in raw_code.split("\n")]
    preprocessed = []

    for line in raw_code:
        match line.split(" "):
            case [Token.include, path] if path.endswith(Token.star):
                # Удаляем * из пути и получаем директорию
                dir_path = path[:-1].replace(Token.dot, "/")
                try:
                    files = os.listdir(dir_path)
                except FileNotFoundError:
                    kill_process(f"Модуль для включения не найден: {path}")
                    return

                for filename in files:
                    if filename.endswith(".law"):  # Проверка на нужное расширение
                        file_path = os.path.join(dir_path, filename)
                        preprocessed.append(import_preprocess(file_path))

            case [Token.include, path]:
                path = path.replace(Token.dot, "/")
                path = f"{path}.law"
                preprocessed.append(import_preprocess(path))
            case _:
                preprocessed.append(line)

    return [line for line in preprocessed if line]


def preprocess_file(file) -> list:
    return preprocess(file.read())


def run_compiled_code(compiled: Compiled):
    interpreter = Interpreter(compiled)
    interpreter.run()


def run(raw_code: str):
    code = preprocess(raw_code)

    ast_builder = AbstractSyntaxTreeBuilder(code)
    ast: list[Metadata] = ast_builder.build()

    compiler = Compiler(ast)
    run_compiled_code(compiler.compile())


def run_file(path: str):
    if path.endswith('.law'):
        with open(path, "rb") as file:
            compiled = pickle.load(file)
            run_compiled_code(compiled)
    else:
        with open(path, "r", encoding="utf-8") as file:
            run(file.read())
