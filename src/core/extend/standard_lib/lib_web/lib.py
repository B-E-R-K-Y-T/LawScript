from typing import Optional

from pathlib import Path

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/"
MOD_NAME = "интернет"


@builder.collect(func_name='запрос_в_интернет')
class Request(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.offset_required_args = 3
        self.count_args = 5

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        import json

        import requests

        from src.core.types.atomic import Table, String, Number, Boolean, convert_py_type_to_atomic_type
        from src.core.exceptions import ErrorType, ErrorValue, HttpError

        headers = Table()
        cookies = Table()

        if len(args) == self.offset_required_args:
            method, url, data = args
        else:
            method, url, data, *tail = args

            headers = tail[0]

            if len(tail) == 2:
                cookies = tail[1]

        if not isinstance(method, String):
            raise ErrorType(f"Первый аргумент должен иметь тип '{String.type_name()}'!")

        if not isinstance(url, String):
            raise ErrorType(f"Второй аргумент должен иметь тип '{String.type_name()}'!")

        if not isinstance(data, Table):
            raise ErrorType(f"Третий аргумент должен иметь тип '{Table.type_name()}'!")

        if not isinstance(headers, Table):
            raise ErrorType(f"Четвертый аргумент должен иметь тип '{Table.type_name()}'!")

        if not isinstance(cookies, Table):
            raise ErrorType(f"Пятый аргумент должен иметь тип '{Table.type_name()}'!")

        method, url, data, *_ = self.parse_args(args)
        headers, cookies = self.parse_args([headers, cookies])

        methods_map = {
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "HEAD",
            "OPTIONS",
            "PATCH",
        }

        if method not in methods_map:
           raise ErrorValue(
               f"Первый аргумент принимает только одно из этих значений: {list(methods_map)}, но не '{method}'"
           )

        try:
            resp = requests.request(method, url, data=data, headers=headers, cookies=cookies)
        except requests.exceptions.RequestException as e:
            raise HttpError(msg=f"При запросе произошла ошибка. Детали: '{e}'")

        try:
            json_data = resp.json()
        except json.JSONDecodeError:
            json_data = {}

        text_data = resp.text

        result = Table({
            String("статус_код"): Number(resp.status_code),
            String("заголовки"): convert_py_type_to_atomic_type(resp.headers),
            String("cookies"): convert_py_type_to_atomic_type(resp.cookies),
            String("json"): convert_py_type_to_atomic_type(json_data),
            String("текст"): String(text_data),
            String("успешно"): Boolean(resp.status_code < 400),
        })

        return result


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
