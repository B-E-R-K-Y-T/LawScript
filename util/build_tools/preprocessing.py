import os
import re
from typing import Optional, Union

from pathlib import Path
import dill

from config import settings
from core.tokens import Tokens
from core.types.line import Line
from core.util import kill_process
from util.build_tools.compile import Compiled


STANDARD_LIB_PATH = Path(__file__).resolve().parent.parent.parent
STANDARD_LIB_PATH = f"{STANDARD_LIB_PATH}{settings.standard_lib_path_postfix}"
STD_NAME = settings.std_name


def _standard_lib_alias(path: str) -> str:
    if _is_std(path):
        return path.replace(STD_NAME, STANDARD_LIB_PATH)

    return path


def _is_std(path: str) -> bool:
    return STD_NAME in path


def import_preprocess(path, byte_mode: Optional[bool] = True) -> Union[Compiled, str]:
    try:
        if byte_mode:
            with open(path, "rb") as file:
                compiled = dill.load(file)
                return compiled

        with open(path, "r", encoding="utf-8") as file:
            raw_code = file.read()
            return raw_code

    except FileNotFoundError:
        raise FileNotFoundError
    except RecursionError as e:
        raise e


def preprocess(raw_code, path: str) -> list:
    folder = os.path.dirname(path)

    prepared_code = [line.strip() for line in raw_code.split("\n")]
    imports = set()

    code = []

    for offset, line in enumerate(prepared_code):
        code.append(Line(line.strip(), num=offset+1, file=path))

    preprocessed = []

    for offset, line in enumerate(code):
        match line.split(" "):
            case [Tokens.include, package] if package.endswith(Tokens.star):
                is_std_path = _is_std(package)
                package = _standard_lib_alias(package)

                if package in imports:
                    continue

                imports.add(package)

                # Удаляем * из пути и получаем директорию
                package = package[:-1].replace(Tokens.dot, "/")

                dir_path = os.path.dirname(package)

                if not is_std_path:
                    dir_path = os.path.join(os.getcwd(), f"{folder}/{package}")
                try:
                    files = os.listdir(dir_path)
                except FileNotFoundError:
                    kill_process(f"Модуль для включения не найден: '{dir_path}'")

                try:
                    checked_files = []

                    for filename in files: # noqa
                        file_without_ext = os.path.splitext(filename)[0]

                        if file_without_ext in checked_files:
                            continue

                        if filename.endswith(f".{settings.compiled_postfix}"):  # Проверка на нужное расширение
                            file_path = os.path.join(dir_path, filename)
                            preprocessed.append(import_preprocess(file_path))
                            checked_files.append(file_without_ext)
                        elif filename.endswith(f".{settings.py_extend_postfix}"):  # Проверка на нужное расширение
                            file_path = os.path.join(dir_path, filename)
                            preprocessed.append(import_preprocess(file_path))
                            checked_files.append(file_without_ext)
                        elif filename.endswith(f".{settings.raw_postfix}"):  # Проверка на нужное расширение
                            file_path = os.path.join(dir_path, filename)
                            preprocessed.extend(preprocess(import_preprocess(file_path, byte_mode=False), file_path))
                            checked_files.append(file_without_ext)

                except RecursionError:
                    kill_process(
                        f"Обнаружен циклический импорт '{path}', {line}"
                    )

            case [Tokens.include, module] if re.search(r'\.\S+$', module):
                is_std_path = _is_std(module)
                module = _standard_lib_alias(module)

                if module in imports:
                    continue

                imports.add(module)

                module = module.replace(".", "/", module.count("."))
                path = module

                if not is_std_path:
                    path = os.path.join(os.getcwd(), f"{folder}/{module}")

                law_path = (f"{path}.{settings.compiled_postfix}", True)
                pyl_path = (f"{path}.{settings.py_extend_postfix}", True)
                raw_path = (f"{path}.{settings.raw_postfix}", False)

                for path_data in [law_path, pyl_path, raw_path]:
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

            case [Tokens.include, module]:
                if module in imports:
                    continue

                imports.add(module)

                module = module.replace(Tokens.dot, "/")
                path = os.path.join(os.getcwd(), f"{folder}/{module}")

                law_path = (f"{path}.{settings.compiled_postfix}", True)
                pyl_path = (f"{path}.{settings.py_extend_postfix}", True)
                raw_path = (f"{path}.{settings.raw_postfix}", False)

                for path_data in [law_path, pyl_path, raw_path]:
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
