from typing import Optional

from pathlib import Path

from src.core.extend.function_wrap import PyExtendWrapper, PyExtendBuilder
from src.core.types.basetype import BaseAtomicType
from src.core.types.code_block import CodeBlock

builder = PyExtendBuilder()
standard_lib_path = f"{Path(__file__).resolve().parent.parent}/modules/_/"
MOD_NAME = "util"


@builder.collect(func_name='_глубокое_копирование')
class DeepCopy(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from copy import deepcopy

        return deepcopy(args[0])


@builder.collect(func_name='_поверхностное_копирование')
class Copy(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from copy import copy

        return copy(args[0])


@builder.collect(func_name='_словарь_в_таблицу')
class PrintPrettyTable(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from rich.table import Table as RichTable
        from rich import print as rich_print
        from rich.box import SQUARE

        from src.core.types.atomic import Table, VOID
        from src.core.exceptions import ErrorValue

        if not isinstance(args[0], Table):
            raise ErrorValue("Аргумент должен быть таблицей!")

        # Получаем словарь из таблицы
        table_data: dict = self.parse_args(args)[0]

        # Создаем красивую таблицу
        rich_table = RichTable(box=SQUARE, header_style="bold magenta")

        # Добавляем колонки
        if table_data:
            # Предполагаем, что это словарь {ключ: значение}
            rich_table.add_column("Ключ", style="cyan")
            rich_table.add_column("Значение", style="green")

            # Добавляем строки
            for key, value in table_data.items():
                rich_table.add_row(str(key), str(value))
        else:
            # Пустая таблица
            rich_table.add_column("Пустая таблица", justify="center")
            rich_table.add_row("Нет данных")

        # Выводим таблицу
        rich_print(rich_table)

        return VOID


@builder.collect(func_name='показать_атрибуты_сущности')
class ViewObjectFields(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def call(self, args: Optional[list[BaseAtomicType]] = None):
        from src.core.types.atomic import Table, String
        from src.core.types.classes import ClassInstance

        obj = args[0]

        attrs = {}

        if hasattr(obj, "fields"):
            attrs.update({String(k): v for k, v in obj.fields.items()})

        if isinstance(obj, ClassInstance):
            attrs.update({String(k): v for k, v in obj.metadata.methods.items()})

        return Table(attrs)


@builder.collect(func_name='показать_узлы_сущности')
class ViewNodesEntity(PyExtendWrapper):
    def __init__(self, func_name: str):
        super().__init__(func_name)
        self.empty_args = False
        self.count_args = 1

    def _view(self, entity: CodeBlock, nodes: list) -> list:
        from src.core.types.code_block import CodeBlock
        from src.core.types.procedure import (
            Loop, Print, When, While, ElseWhen,
            Else, Break, Continue, Context, Expression,
            AssignField, AssignOverrideVariable, ExceptionHandler, ErrorThrow,
            Return, Defer,
        )

        if not isinstance(entity, CodeBlock):
            return nodes

        for cmd in entity.body.commands:
            value = ""

            if isinstance(cmd, Loop):
                value = ["Loop", "FROM_EXPR", cmd.expression_from.operations, "TO_EXPR", cmd.expression_to.operations]

            elif isinstance(cmd, Print):
                value = ["Print", "EXPR", cmd.expression.operations]

            elif isinstance(cmd, Return):
                value = ["Return", "EXPR", cmd.expression.operations]

            elif isinstance(cmd, Defer):
                value = ["Defer", "EXPR", cmd.expression.operations]

            elif isinstance(cmd, ErrorThrow):
                value = ["ErrorThrow", "EXPR", cmd.expression.operations]

            elif isinstance(cmd, When):
                value = ["When", "EXPR", cmd.expression.operations]

            elif isinstance(cmd, ElseWhen):
                value = ["ElseWhen", "EXPR", cmd.expression.operations]

            elif isinstance(cmd, Else):
                value = "Else"

            elif isinstance(cmd, While):
                value = ["While", "EXPR", cmd.expression.operations]

            elif isinstance(cmd, Break):
                value = f"Break"

            elif isinstance(cmd, Continue):
                value = f"Continue"

            elif isinstance(cmd, Context):
                value = f"Context"

            elif isinstance(cmd, ExceptionHandler):
                value = [
                    "ExceptionHandler", "EX_CLS_NAME", cmd.exception_class_name, "EX_INST", cmd.exception_inst_name
                ]

            elif isinstance(cmd, AssignField):
                value = ["AssignField", "TARGET", cmd.name, "EXPR", cmd.expression.operations]

            elif isinstance(cmd, AssignOverrideVariable):
                value = [
                    "AssignOverrideVariable", "TARGET_EXPR", cmd.target_expr.operations,
                    "OVERRIDE_EXPR", cmd.override_expr.operations
                ]

            elif isinstance(cmd, Expression):
                value = cmd.operations

            nodes.append(value)

            if isinstance(cmd, CodeBlock):
                nodes.append(self._view(cmd, []))

        return nodes

    def call(self, args: Optional[list[CodeBlock]] = None):
        from pprint import pprint
        from src.core.types.atomic import VOID

        nodes = self._view(args[0], [])
        pprint(nodes)

        return VOID


def build_module():
    builder.build_python_extend(f"{standard_lib_path}{MOD_NAME}")


if __name__ == '__main__':
    build_module()
