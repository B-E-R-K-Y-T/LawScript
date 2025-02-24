import os
import pickle
import re
from typing import Optional, Union

from config import settings
from core.parse.base import MetaObject
from core.tokens import Tokens
from core.types.line import Line
from core.util import kill_process
from util.build_tools.ast import AbstractSyntaxTreeBuilder
from util.build_tools.compile import Compiler, Compiled
from util.build_tools.interpreter import Interpreter


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
        raise FileNotFoundError
    except RecursionError as e:
        raise e


def preprocess(raw_code, path: str) -> list:
    prepared_code = [line.strip() for line in raw_code.split("\n")]
    imports = set()

    code = []

    for offset, line in enumerate(prepared_code):
        code.append(Line(line.strip(), num=offset+1, file=path))

    preprocessed = []

    for offset, line in enumerate(code):
        match line.split(" "):
            case [Tokens.include, path] if path.endswith(Tokens.star):
                if path in imports:
                    continue

                imports.add(path)

                # Удаляем * из пути и получаем директорию
                dir_path = path[:-1].replace(Tokens.dot, "/")
                try:
                    files = os.listdir(dir_path)
                except FileNotFoundError:
                    kill_process(f"Модуль для включения не найден: '{path}'")

                try:
                    checked_files = []

                    for filename in files: # noqa
                        file_without_ext = os.path.splitext(filename)[0]

                        if file_without_ext in checked_files:
                            continue

                        if filename.endswith(f".{settings.compiled_prefix}"):  # Проверка на нужное расширение
                            file_path = os.path.join(dir_path, filename)
                            preprocessed.append(import_preprocess(file_path))
                            checked_files.append(file_without_ext)
                        elif filename.endswith(f".{settings.raw_prefix}"):  # Проверка на нужное расширение
                            file_path = os.path.join(dir_path, filename)
                            preprocessed.extend(preprocess(import_preprocess(file_path, byte_mode=False), file_path))
                            checked_files.append(file_without_ext)

                except RecursionError:
                    kill_process(
                        f"Обнаружен циклический импорт '{path}', {line}"
                    )

            case [Tokens.include, path] if re.search(r'\.\S+$', path):
                if path in imports:
                    continue

                imports.add(path)

                path = path.replace(".", "/", path.count("."))
                law_path = (f"{path}.{settings.compiled_prefix}", True)
                raw_path = (f"{path}.{settings.raw_prefix}", False)

                for path_data in [law_path, raw_path]:
                    path_, byte_mode = path_data

                    try:
                        if not byte_mode:
                            preprocessed.extend(preprocess(import_preprocess(path_, byte_mode=byte_mode), path_))
                        else:
                            preprocessed.append(import_preprocess(path_, byte_mode=byte_mode))
                    except FileNotFoundError:
                        continue
                    except RecursionError:
                        kill_process(
                            f"Обнаружен циклический импорт '{path}', {line}"
                        )
                    else:
                        break

                else:
                    kill_process(f"Невозможно включить модуль. Модуль '{path}' не найден.")

            case [Tokens.include, path]:
                if path in imports:
                    continue

                imports.add(path)

                path = path.replace(Tokens.dot, "/")

                law_path = (f"{path}.{settings.compiled_prefix}", True)
                raw_path = (f"{path}.{settings.raw_prefix}", False)

                for path_data in [law_path, raw_path]:
                    path_, byte_mode = path_data

                    try:
                        if not byte_mode:
                            preprocessed.extend(preprocess(import_preprocess(path_, byte_mode=byte_mode), path_))
                        else:
                            preprocessed.append(import_preprocess(path_, byte_mode=byte_mode))
                    except FileNotFoundError:
                        continue
                    except RecursionError:
                        kill_process(
                            f"Обнаружен циклический импорт '{path}', {line}"
                        )
                    else:
                        break

                else:
                    kill_process(f"Невозможно включить модуль. Модуль '{path}' не найден.")

            case _:
                preprocessed.append(line)

                imports.add(path)

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
    try:
        if path.endswith(f'.{settings.compiled_prefix}'):
            with open(path, "rb") as file:
                compiled = pickle.load(file)
                run_compiled_code(compiled)
        elif path.endswith(f'.{settings.raw_prefix}'):
            with open(path, "r", encoding="utf-8") as file:
                run(file.read(), path)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        kill_process(f"Файл '{path}' не найден.")
