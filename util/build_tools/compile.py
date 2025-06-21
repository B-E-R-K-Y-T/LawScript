from typing import Type, Union, Optional

from core.exceptions import (
    NameNotDefine,
    InvalidType,
    UnknownType,
    NameAlreadyExist,
    FieldNotDefine, InvalidSyntaxError,
)
from core.extend.function_wrap import PyExtendWrapper
from core.parse.base import MetaObject
from core.parse.util.rpn import build_rpn_stack
from core.tokens import Tokens, NOT_ALLOWED_TOKENS
from core.types.basetype import BaseType
from core.types.checkers import CheckerSituation
from core.types.conditions import Condition
from core.types.criteria import Criteria
from core.types.dispositions import Disposition
from core.types.documents import FactSituation, Document
from core.types.execute_block import ExecuteBlock
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

        if isinstance(compiled_obj, ExecuteBlock):
            for expression in compiled_obj.expressions:
                self.expr_compile(expression, [])

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

        elif isinstance(compiled_obj, Procedure):
            self.check_code_body(compiled_obj.body)

            def get_all_uses_names(obj_: Union[CodeBlock, BaseType]) -> list[tuple[BaseType, str]]:
                names = []

                if isinstance(obj_, AssignField):
                    return [(obj_, obj_.name)]

                elif isinstance(obj_, (CodeBlock, Procedure)):
                    for nested_obj in obj_.body.commands:
                        names.extend(get_all_uses_names(nested_obj))

                filtered_names = []

                for item in names:
                    _, name_ = item

                    if isinstance(name_, str):
                        filtered_names.append(item)

                return filtered_names


            for offset, command in enumerate(compiled_obj.body.commands):
                compiled_obj.body.commands[offset] = self.execute_compile(command)

            uses_names = get_all_uses_names(compiled_obj)
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
    def expr_compile(self, expr_: Expression, previous_statements: list[BaseType] = None):
        printer.logging(f"Компиляция выражения в файле {expr_.meta_info.file}", level="INFO")
        raw = expr_.raw_operations

        is_str_flag = False

        # Проверка на недопустимые токены
        for op in raw:
            if op == Tokens.quotation:
                is_str_flag = not is_str_flag

            if is_str_flag:
                continue

            if op in NOT_ALLOWED_TOKENS:
                error_msg = f"Неверный синтаксис. Нельзя использовать операторы в выражениях: {op}"
                printer.logging(error_msg, level="ERROR")
                raise InvalidSyntaxError(
                    error_msg,
                    info=expr_.meta_info
                )

        # Обработка операторов и процедур
        for offset, op in enumerate(raw):
            if not (op not in Tokens and op in self.compiled):
                continue

            command = self.compiled[op]
            printer.logging(f"Обработка оператора '{op}' как команды типа {type(command).__name__}", level="DEBUG")

            if isinstance(command, (Procedure, PyExtendWrapper)):
                if offset < len(raw) - 1:
                    if raw[offset + 1] != Tokens.left_bracket:
                        printer.logging(f"Преобразование '{op}' в LinkedProcedure (без скобок)", level="DEBUG")
                        raw[offset] = LinkedProcedure(name=command.name, func=command)
                    continue

                printer.logging(f"Преобразование '{op}' в LinkedProcedure", level="DEBUG")
                raw[offset] = LinkedProcedure(name=command.name, func=command)

        # Обработка предыдущих statements
        if previous_statements is not None:
            printer.logging("Проверка предыдущих statements для связывания процедур", level="DEBUG")
            for command in reversed(previous_statements):
                if isinstance(command, AssignField) and len(command.expression.operations) == 1:
                    for offset, op in enumerate(raw):
                        if op == command.name and isinstance(command.expression.operations[0], LinkedProcedure):
                            func: Procedure = command.expression.operations[0].func
                            printer.logging(f"Связывание переменной '{op}' с процедурой '{func.name}'", level="DEBUG")
                            raw[offset] = func
                            continue

        # Построение RPN стека
        printer.logging("Построение RPN стека для выражения", level="DEBUG")
        expr_.operations = build_rpn_stack(raw, expr_.meta_info)
        printer.logging(f"Выражение успешно скомпилировано. Операции: {expr_.operations}", level="INFO")

    def body_compile(self, body: Body):
        printer.logging(f"Компиляция тела кода (начало)", level="INFO")
        statements = []

        for statement in body.commands:
            printer.logging(f"Обработка statement типа {type(statement).__name__}", level="DEBUG")

            if isinstance(statement, Expression):
                printer.logging("Компиляция Expression", level="DEBUG")
                self.expr_compile(statement, statements)

            elif isinstance(statement, While):
                printer.logging("Компиляция While условия", level="DEBUG")
                self.expr_compile(statement.expression, statements)

            elif isinstance(statement, Loop):
                printer.logging("Компиляция Loop выражений (from/to)", level="DEBUG")
                self.expr_compile(statement.expression_from, statements)
                self.expr_compile(statement.expression_to, statements)

            elif isinstance(statement, AssignOverrideVariable):
                printer.logging("Компиляция AssignOverrideVariable выражений", level="DEBUG")
                self.expr_compile(statement.target_expr, statements)
                self.expr_compile(statement.override_expr, statements)

            elif isinstance(statement, Print):
                printer.logging("Компиляция Print выражения", level="DEBUG")
                self.expr_compile(statement.expression, statements)

            elif isinstance(statement, AssignField):
                printer.logging("Компиляция AssignField выражения", level="DEBUG")
                self.expr_compile(statement.expression, statements)

            elif isinstance(statement, When):
                printer.logging("Компиляция When условия", level="DEBUG")
                self.expr_compile(statement.expression, statements)

                if statement.else_ is not None:
                    printer.logging("Компиляция else ветки When", level="DEBUG")
                    self.body_compile(statement.else_.body)

                if statement.else_whens:
                    printer.logging("Компиляция else_when веток When", level="DEBUG")
                    for else_when in statement.else_whens:
                        self.expr_compile(else_when.expression, statements)
                        self.body_compile(else_when.body)

            elif isinstance(statement, Return):
                printer.logging("Компиляция Return выражения", level="DEBUG")
                self.expr_compile(statement.expression, statements)

            if isinstance(statement, CodeBlock):
                printer.logging("Рекурсивная компиляция CodeBlock", level="DEBUG")
                self.body_compile(statement.body)

            statements.append(statement)
            printer.logging(f"Statement добавлен в контекст: {statement}", level="DEBUG")

        printer.logging(f"Компиляция тела кода завершена (всего statements: {len(statements)})", level="INFO")
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
                self.body_compile(compiled.body)

                if compiled.default_arguments is not None:
                    for expr in compiled.default_arguments.values():
                        self.expr_compile(expr)

        return Compiled(self.compiled)
