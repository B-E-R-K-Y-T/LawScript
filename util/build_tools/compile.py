from typing import Type, Union

from core.exceptions import (
    NameNotDefine,
    InvalidType,
    UnknownType,
    NameAlreadyExist,
    FieldNotDefine, InvalidSyntaxError, InvalidExpression,
)
from core.extend.function_wrap import PyExtendWrapper
from core.parse.base import MetaObject, is_integer
from core.parse.util.rpn import build_rpn_stack
from core.tokens import Tokens, NOT_ALLOWED_TOKENS
from core.types.atomic import String, Number
from core.types.basetype import BaseType
from core.types.checkers import CheckerSituation
from core.types.conditions import Condition
from core.types.criteria import Criteria
from core.types.dispositions import Disposition
from core.types.documents import FactSituation, Document
from core.types.hypothesis import Hypothesis
from core.types.objects import Object
from core.types.obligations import Obligation
from core.types.laws import Law
from core.types.procedure import (
    Procedure,
    CodeBlock,
    AssignField,
    Return,
    Print,
    Loop,
    Continue,
    Body,
    Break,
    Expression,
    LinkedProcedure,
    AssignOverrideVariable,
    When,
    While
)
from core.types.rules import Rule
from core.types.sanction_types import SanctionType
from core.types.sanctions import Sanction
from core.types.severitys import Severity
from core.types.subjects import Subject
from core.types.table import TableFactory, Table
from util.console_worker import printer


class Compiled:
    def __init__(self, compiled: dict[str, BaseType]):
        self.compiled_code = compiled


class Compiler:
    def __init__(self, ast: list[MetaObject]):
        self.ast = ast
        self.compiled: dict[str, BaseType] = {}
        printer.logging("Инициализация Compiler", level="INFO")

    def get_obj_by_name(self, name: str) -> BaseType:
        for obj_name, obj in self.compiled.items():
            if name == obj.name:
                printer.logging(f"Найден объект по имени: {name}", level="INFO")
                return obj

        printer.logging(f"Объект с именем {name} не определен", level="ERROR")
        raise NameNotDefine(name=name)

    def __check_none_type(
            self, obj: Union[BaseType, MetaObject], field_name: str, object_name: str
    ) -> Union[str, BaseType]:
        compiled_obj = self.execute_compile(obj)

        if compiled_obj is None:
            printer.logging(f"Поле {field_name} не определено для {object_name}", level="ERROR")
            raise FieldNotDefine(field_name, object_name)

        return compiled_obj

    def process_literal_field(
            self,
            obj: Union[BaseType, MetaObject],
            field_name: str,
            object_name: str,
            type_check: Type[BaseType]
    ) -> BaseType:
        compiled_obj = self.__check_none_type(obj, field_name, object_name)
        compiled_obj = self.get_obj_by_name(compiled_obj)

        if not isinstance(compiled_obj, type_check):
            printer.logging(f"Ошибка типа: {compiled_obj.name} не является {type_check.__name__} для {field_name}",
                            level="ERROR")
            raise InvalidType(compiled_obj.name, field_name)

        printer.logging(f"Поле {field_name} успешно обработано как {type_check.__name__}", level="INFO")
        return compiled_obj

    def process_object_field(
            self,
            obj: Union[BaseType, MetaObject],
            field_name: str,
            object_name: str,
            type_check: Type[BaseType]
    ) -> BaseType:
        compiled_obj: BaseType = self.__check_none_type(obj, field_name, object_name)

        if not isinstance(compiled_obj, type_check):
            printer.logging(f"Ошибка типа: {compiled_obj.name} не является {type_check.__name__} для {field_name}",
                            level="ERROR")
            raise InvalidType(compiled_obj.name, field_name)

        printer.logging(f"Поле {field_name} успешно обработано как {type_check.__name__}", level="INFO")
        return compiled_obj

    def check_code_body(self, body: Body):
        for statement in body.commands:
            if isinstance(statement, (Loop, While)):
                try:
                    self.check_code_body(statement.body)
                except InvalidSyntaxError:
                    continue

            elif isinstance(statement, Continue):
                raise InvalidSyntaxError(
                    f"Оператор {Tokens.continue_} встретился вне цикла.", info=statement.meta_info
                )

            elif isinstance(statement, Break):
                raise InvalidSyntaxError(
                    f"Оператор {Tokens.break_} встретился вне цикла.", info=statement.meta_info
                )

            elif isinstance(statement, CodeBlock):
                self.check_code_body(statement.body)

    def get_all_uses_names(self, obj_: Union[CodeBlock, BaseType]) -> list[tuple[BaseType, str]]:
        names = []

        if isinstance(obj_, AssignField):
            return [(obj_, obj_.name)]

        elif isinstance(obj_, (CodeBlock, Procedure)):
            for nested_obj in obj_.body.commands:
                names.extend(self.get_all_uses_names(nested_obj))

        filtered_names = []

        for item in names:
            _, name_ = item

            if isinstance(name_, str):
                filtered_names.append(item)

        return filtered_names

    def body_compile(self, body: Body) -> None:
        self.check_code_body(body)

        for offset, command in enumerate(body.commands):
            body.commands[offset] = self.execute_compile(command)

    def procedure_compile(self, compiled_obj: Procedure) -> None:
            self.body_compile(compiled_obj.body)

            uses_names = self.get_all_uses_names(compiled_obj)
            check_seq = set()

            for obj, name in uses_names:
                if isinstance(obj, AssignField):
                    check_seq.add(name)
                    continue

                if name in compiled_obj.arguments_names:
                    check_seq.add(name)
                    continue

                if name not in check_seq:
                    msg = (
                        f"Объект '{name}' используется до определения в процедуре '{compiled_obj.name}'. "
                        f"Файл: {compiled_obj.meta_info.file}"
                    )

                    printer.logging(msg, level="ERROR")
                    raise NameNotDefine(msg=msg)



    def execute_compile(self, meta: Union[BaseType, MetaObject, Compiled]) -> Union[str, BaseType, Compiled]:
        if isinstance(meta, Compiled):
            return meta

        if not isinstance(meta, MetaObject):
            printer.logging("Объект не является метаданными, возвращаем его", level="INFO")
            return meta

        compiled_obj = meta.create_image().build()
        printer.logging(f"Команда скомпилирована: {compiled_obj}", level="INFO")

        if isinstance(compiled_obj, (SanctionType, Rule, Law, Obligation, Severity, Criteria)):
            return compiled_obj

        if isinstance(compiled_obj, Criteria):
            return compiled_obj

        elif isinstance(compiled_obj, CheckerSituation):
            compiled_obj.document = self.process_literal_field(
                compiled_obj.document, Tokens.document, Tokens.check, Document
            )
            compiled_obj.fact_situation = self.process_literal_field(
                compiled_obj.fact_situation,
                f"{Tokens.actual} {Tokens.situation}", Tokens.check, FactSituation
            )

        elif isinstance(compiled_obj, Sanction):
            compiled_obj.type = self.execute_compile(compiled_obj.type)
            compiled_obj.severity = self.execute_compile(compiled_obj.severity)

        elif isinstance(compiled_obj, Disposition):
            compiled_obj.law = self.process_literal_field(
                compiled_obj.law, Tokens.law, Tokens.disposition, Law
            )
            compiled_obj.obligation = self.process_literal_field(
                compiled_obj.obligation, Tokens.duty, Tokens.disposition, Obligation
            )
            compiled_obj.rule = self.process_literal_field(
                compiled_obj.rule, Tokens.rule, Tokens.disposition, Rule
            )

        elif isinstance(compiled_obj, Subject):
            return compiled_obj


        elif isinstance(compiled_obj, TableFactory):
            self.body_compile(compiled_obj.table_image.body)

            return compiled_obj

        elif isinstance(compiled_obj, Procedure):
            self.procedure_compile(compiled_obj)

            return compiled_obj

        elif isinstance(compiled_obj, Object):
            return compiled_obj

        elif isinstance(compiled_obj, Hypothesis):
            compiled_obj.subject = self.process_literal_field(
                compiled_obj.subject, Tokens.subject, Tokens.hypothesis, Subject
            )
            compiled_obj.object = self.process_literal_field(
                compiled_obj.object, Tokens.object, Tokens.hypothesis, Object
            )
            compiled_obj.condition = self.process_literal_field(
                compiled_obj.condition, Tokens.condition, Tokens.hypothesis, Condition
            )

        elif isinstance(compiled_obj, Condition):
            compiled_obj.criteria = self.process_object_field(
                compiled_obj.criteria,
                Tokens.criteria,
                Tokens.condition,
                Criteria
            )

        elif isinstance(compiled_obj, FactSituation):
            compiled_obj.object_ = self.process_literal_field(
                compiled_obj.object_, Tokens.object, f"{Tokens.actual} {Tokens.situation}", Object
            )
            compiled_obj.subject = self.process_literal_field(
                compiled_obj.subject, Tokens.subject, f"{Tokens.actual} {Tokens.situation}", Subject
            )

        elif isinstance(compiled_obj, Document):
            compiled_obj.sanction = self.process_object_field(
                compiled_obj.sanction,
                Tokens.sanction,
                Tokens.document,
                Sanction
            )
            compiled_obj.disposition = self.process_object_field(
                compiled_obj.disposition,
                Tokens.disposition,
                Tokens.document,
                Disposition
            )
            compiled_obj.hypothesis = self.process_object_field(
                compiled_obj.hypothesis,
                Tokens.hypothesis,
                Tokens.document,
                Hypothesis
            )

        else:
            printer.logging(f"Невозможно скомпилировать: {compiled_obj}", level="ERROR")
            raise UnknownType(f"Невозможно скомпилировать {compiled_obj}")

        return compiled_obj

    def expr_compile(self, body: Body):
        def _compile(expr_: Expression):
            raw = expr_.raw_operations

            for op in raw:
                if op in NOT_ALLOWED_TOKENS:
                    raise InvalidSyntaxError(
                        f"Неверный синтаксис. Нельзя использовать операторы в выражениях: {op}",
                        info=expr_.meta_info
                    )

            for offset, op in enumerate(raw):
                if op == Tokens.dot:
                    if offset < len(raw) - 1:
                        if is_integer(raw[offset - 1]) and is_integer(raw[offset + 1]):
                            num = Number(float(f"{raw[offset - 1]}{Tokens.dot}{raw[offset + 1]}"))

                            del raw[offset - 1: offset + 2]
                            raw.insert(offset-1, num)

            for offset, op in enumerate(raw):
                if op == Tokens.quotation:
                    step = offset
                    res_op = ""

                    while step < len(raw) - 1:
                        step += 1
                        next_op = raw[step]

                        if next_op == Tokens.quotation:
                            jump = step + 1
                            break

                        res_op += next_op
                    else:
                        raise InvalidExpression(
                            f"В выражении: '{' '.join(raw)}' не хватает закрывающей кавычки: '{Tokens.quotation}'"
                        )

                    del raw[offset: jump]
                    raw.insert(offset, String(res_op))

                    continue

            for offset, op in enumerate(raw):
                if not (op not in Tokens and op in self.compiled):
                    continue

                command = self.compiled[op]

                if isinstance(command, (Procedure, PyExtendWrapper)):
                    if offset < len(raw) - 1:
                        if raw[offset + 1] != Tokens.left_bracket:
                            raw[offset] = LinkedProcedure(name=command.name, func=command)
                        continue

                    raw[offset] = LinkedProcedure(name=command.name, func=command)

            expr_.operations = build_rpn_stack(raw, expr_.meta_info)

        for statement in body.commands:
            if isinstance(statement, Expression):
                _compile(statement)

            elif isinstance(statement, While):
                _compile(statement.expression)

            elif isinstance(statement, Loop):
                _compile(statement.expression_from)
                _compile(statement.expression_to)

            elif isinstance(statement, AssignOverrideVariable):
                _compile(statement.target_expr)
                _compile(statement.override_expr)

            elif isinstance(statement, Print):
                _compile(statement.expression)

            elif isinstance(statement, AssignField):
                _compile(statement.expression)

            elif isinstance(statement, When):
                _compile(statement.expression)

                if statement.else_ is not None:
                    self.expr_compile(statement.else_.body)

            elif isinstance(statement, Return):
                _compile(statement.expression)

            if isinstance(statement, CodeBlock):
                self.expr_compile(statement.body)

    def compile(self) -> Compiled:
        compiled_modules = {}

        for idx, meta in enumerate(self.ast):
            compiled = self.execute_compile(meta)

            if isinstance(compiled, Compiled):
                compiled_modules = {**compiled_modules, **compiled.compiled_code}
                continue

            printer.logging(f"Команда компиляции №{idx + 1}", level="INFO")

            if compiled.name in self.compiled:
                printer.logging(f"Ошибка: {compiled.name} уже существует", level="ERROR")
                raise NameAlreadyExist(compiled.name)

            self.compiled[compiled.name] = compiled
            printer.logging(f"Скомпилировано: {compiled.name}", level="INFO")

        compiled_without_build_modules = self.compiled
        self.compiled = {**compiled_modules, **self.compiled}

        for name, compiled in compiled_without_build_modules.items():
            if isinstance(compiled, Procedure):
                self.expr_compile(compiled.body)

            elif isinstance(compiled, TableFactory):
                self.expr_compile(compiled.table_image.body)

                for cmd in compiled.table_image.body.commands:
                    if isinstance(cmd, Procedure):
                        self.expr_compile(cmd.body)

        return Compiled(self.compiled)
