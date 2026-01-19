from typing import Type, Union

from src.core.exceptions import (
    NameNotDefine,
    InvalidType,
    UnknownType,
    NameAlreadyExist,
    FieldNotDefine,
    InvalidSyntaxError,
    ErrorType, EXCEPTIONS, create_define_class_wrap, BaseError, is_def_err,
)
from src.core.extend.function_wrap import PyExtendWrapper
from src.core.parse.base import MetaObject
from src.core.parse.util.rpn import build_rpn_stack
from src.core.tokens import Tokens, NOT_ALLOWED_TOKENS
from src.core.types.atomic import Array, String, Table
from src.core.types.basetype import BaseType
from src.core.types.checkers import CheckerSituation
from src.core.types.classes import Method, Constructor, ClassDefinition, ClassExceptionDefinition
from src.core.types.conditions import Condition
from src.core.types.criteria import Criteria
from src.core.types.dispositions import Disposition
from src.core.types.docs import Docs
from src.core.types.documents import FactSituation, Document
from src.core.types.execute_block import ExecuteBlock
from src.core.types.hypothesis import Hypothesis
from src.core.types.objects import Object
from src.core.types.obligations import Obligation
from src.core.types.laws import Law
from src.core.types.operation import Operator
from src.core.types.procedure import (
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
    While,
    Context, ErrorThrow
)
from src.core.types.rules import Rule
from src.core.types.sanction_types import SanctionType
from src.core.types.sanctions import Sanction
from src.core.types.severitys import Severity
from src.core.types.subjects import Subject
from src.util.console_worker import printer


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
                    f"Оператор '{Tokens.continue_}' встретился вне цикла.", info=statement.meta_info
                )

            elif isinstance(statement, Break):
                raise InvalidSyntaxError(
                    f"Оператор '{Tokens.break_}' встретился вне цикла.", info=statement.meta_info
                )

            elif isinstance(statement, CodeBlock):
                if isinstance(statement, When):
                    self.check_code_body(statement.body)

                    if statement.else_whens is not None:
                        for else_when in statement.else_whens:
                            self.check_code_body(else_when.body)

                    if statement.else_ is not None:
                        self.check_code_body(statement.else_.body)

                elif isinstance(statement, Context):
                    self.check_code_body(statement.body)

                    for handler in statement.handlers:
                        self.check_code_body(handler.body)

                else:
                    self.check_code_body(statement.body)

    def compile_procedure(self, compiled_obj: Union[Procedure, Method, Constructor]) -> Union[Procedure, Method, Constructor]:
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

        if compiled_obj.body.docs is not None:
            compiled_obj.body.docs = self.execute_compile(compiled_obj.body.docs)

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

                for op in expression.operations:
                    if isinstance(op, Operator) and op.operator == Tokens.wait:
                        raise InvalidSyntaxError(
                            f"Оператор '{Tokens.wait}' не разрешен в блоке '{Tokens.execute}'",
                            info=expression.meta_info
                        )

            return compiled_obj

        elif isinstance(compiled_obj, CheckerSituation):
            compiled_obj.document = self.process_literal_field(
                compiled_obj.document, Tokens.document, Tokens.check, Document
            )
            compiled_obj.fields["__документ__"] = compiled_obj.document # noqa
            compiled_obj.fact_situation = self.process_literal_field(
                compiled_obj.fact_situation,
                f"{Tokens.actual} {Tokens.situation}", Tokens.check, FactSituation
            )
            compiled_obj.fields["__фактическая_ситуация__"] = compiled_obj.fact_situation # noqa

        elif isinstance(compiled_obj, Sanction):
            sanctions = []

            for sanction_type in compiled_obj.type:
                if sanction_type not in self.compiled:
                    raise NameNotDefine(
                        name=sanction_type,
                        info=compiled_obj.meta_info
                    )

                sanction = self.compiled[sanction_type]

                if not isinstance(sanction, SanctionType):
                    raise ErrorType(f"Поле '{sanction_type}' должно иметь тип: {SanctionType}")

                sanctions.append(sanction)

            compiled_obj.type = self.execute_compile(sanctions)
            compiled_obj.fields["__типы__"] = Array(compiled_obj.type)
            compiled_obj.severity = self.execute_compile(compiled_obj.severity)

        elif isinstance(compiled_obj, Disposition):
            compiled_obj.law = self.process_literal_field(
                compiled_obj.law, Tokens.law, Tokens.disposition, Law
            )
            compiled_obj.fields["__право__"] = compiled_obj.law
            compiled_obj.obligation = self.process_literal_field(
                compiled_obj.obligation, Tokens.duty, Tokens.disposition, Obligation
            )
            compiled_obj.fields["__обязанность__"] = compiled_obj.obligation
            compiled_obj.rule = self.process_literal_field(
                compiled_obj.rule, Tokens.rule, Tokens.disposition, Rule
            )
            compiled_obj.fields["__правило__"] = compiled_obj.rule

        elif isinstance(compiled_obj, Subject):
            return compiled_obj

        elif isinstance(compiled_obj, Docs):
            return compiled_obj

        elif isinstance(compiled_obj, ClassDefinition):
            if isinstance(self.compiled.get(compiled_obj.parent), ClassExceptionDefinition):
                parent = self.compiled.get(compiled_obj.parent)

                compiled_obj = ClassExceptionDefinition(
                    name=compiled_obj.name,
                    base_ex=parent.base_ex,
                    parent=compiled_obj.parent,
                    methods=compiled_obj.methods,
                    constructor=compiled_obj.constructor
                )

            compiled_obj.constructor = self.execute_compile(compiled_obj.constructor)

            for method_name, method in compiled_obj.methods.items():
                method: Method = self.execute_compile(method)
                method.name = method_name
                compiled_obj.methods[method_name] = method

            if compiled_obj.methods is None:
                compiled_obj.methods = {}

            if compiled_obj.parent is not None:
                if compiled_obj.parent not in self.compiled:
                    printer.logging(
                        f"Класс {compiled_obj.name} ссылается на несуществующий класс {compiled_obj.parent}",
                        level="ERROR"
                    )
                    raise NameNotDefine(
                        f"Класс '{compiled_obj.name}' ссылается на несуществующий класс '{compiled_obj.parent}'",
                        info=compiled_obj.meta_info
                    )

                compiled_obj.parent = self.compiled[compiled_obj.parent]

            if compiled_obj.constructor is None:
                raise InvalidSyntaxError(
                    f"У класса '{compiled_obj.name}' не определен конструктор!",
                    info=compiled_obj.meta_info
                )

            return compiled_obj

        elif isinstance(compiled_obj, Constructor):
            constructor: Constructor = self.compile_procedure(compiled_obj)

            return constructor

        elif isinstance(compiled_obj, Method):
            method: Method = self.compile_procedure(compiled_obj)

            return method

        elif isinstance(compiled_obj, Procedure):
            return self.compile_procedure(compiled_obj)

        elif isinstance(compiled_obj, Object):
            return compiled_obj

        elif isinstance(compiled_obj, Hypothesis):
            compiled_obj.subject = self.process_literal_field(
                compiled_obj.subject, Tokens.subject, Tokens.hypothesis, Subject
            )
            compiled_obj.fields["__субъект__"] = compiled_obj.subject
            compiled_obj.object = self.process_literal_field(
                compiled_obj.object, Tokens.object, Tokens.hypothesis, Object
            )
            compiled_obj.fields["__объект__"] = compiled_obj.object
            compiled_obj.condition = self.process_literal_field(
                compiled_obj.condition, Tokens.condition, Tokens.hypothesis, Condition
            )
            compiled_obj.fields["__условие__"] = compiled_obj.condition

        elif isinstance(compiled_obj, Condition):
            compiled_obj.criteria = self.process_object_field(
                compiled_obj.criteria,
                Tokens.criteria,
                Tokens.condition,
                Criteria
            )
            compiled_obj.fields["__критерии__"] = Table(
                {String(k): v.value for k, v in compiled_obj.criteria.modify.items()}
            )

        elif isinstance(compiled_obj, FactSituation):
            compiled_obj.object_ = self.process_literal_field(
                compiled_obj.object_, Tokens.object, f"{Tokens.actual} {Tokens.situation}", Object
            )
            compiled_obj.fields["__объект__"] = compiled_obj.object_ # noqa
            compiled_obj.subject = self.process_literal_field(
                compiled_obj.subject, Tokens.subject, f"{Tokens.actual} {Tokens.situation}", Subject
            )
            compiled_obj.fields["__субъект__"] = compiled_obj.subject # noqa

        elif isinstance(compiled_obj, Document):
            compiled_obj.sanction = self.process_object_field(
                compiled_obj.sanction,
                Tokens.sanction,
                Tokens.document,
                Sanction
            )
            compiled_obj.fields["__санкция__"] = compiled_obj.sanction # noqa
            compiled_obj.disposition = self.process_object_field(
                compiled_obj.disposition,
                Tokens.disposition,
                Tokens.document,
                Disposition
            )
            compiled_obj.fields["__диспозиция__"] = compiled_obj.disposition # noqa
            compiled_obj.hypothesis = self.process_object_field(
                compiled_obj.hypothesis,
                Tokens.hypothesis,
                Tokens.document,
                Hypothesis
            )
            compiled_obj.fields["__гипотеза__"] = compiled_obj.hypothesis # noqa

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
                error_msg = f"Неверный синтаксис. Нельзя использовать операторы в выражениях: '{op}'"
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

            elif isinstance(statement, Context):
                printer.logging("Компиляция Context", level="DEBUG")
                if not statement.handlers:
                    raise InvalidSyntaxError(
                        f"У блока '{Tokens.context}' должен быть хотя бы один '{Tokens.handler}'",
                        info=statement.meta_info
                    )

                for handler in statement.handlers:
                    printer.logging(f"Компиляция Handler '{handler}'", level="DEBUG")
                    if handler.exception_class_name not in self.compiled:
                        raise NameNotDefine(
                            name=handler.exception_class_name,
                            info=handler.meta_info
                        )

                    ex = self.compiled[handler.exception_class_name]

                    if not is_def_err(ex):
                        raise ErrorType(
                            f"Ошибки '{handler.exception_class_name}' не существует!",
                            info=handler.meta_info
                        )

                    self.body_compile(handler.body)

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

            elif isinstance(statement, ErrorThrow):
                printer.logging("Компиляция ErrorThrow выражения", level="DEBUG")
                self.expr_compile(statement.expression, statements)

            if isinstance(statement, CodeBlock):
                printer.logging("Рекурсивная компиляция CodeBlock", level="DEBUG")
                self.body_compile(statement.body)

            statements.append(statement)
            printer.logging(f"Statement добавлен в контекст: {statement}", level="DEBUG")

        printer.logging(f"Компиляция тела кода завершена (всего statements: {len(statements)})", level="INFO")

    def compile_default_args(self, default_arguments: dict[str, Expression]):
        for expr in default_arguments.values():
            self.expr_compile(expr)

    def compile(self) -> Compiled:
        compiled_modules = {}

        for name, ex in EXCEPTIONS.items():
            ex_def = create_define_class_wrap(ex)

            self.compiled[ex_def.name] = ex_def

        for idx, meta in enumerate(self.ast):
            compiled = self.execute_compile(meta)

            if isinstance(compiled, Compiled):
                compiled_modules = {**compiled_modules, **compiled.compiled_code}
                continue

            printer.logging(f"Команда компиляции №{idx + 1}", level="INFO")

            if compiled.name in self.compiled:
                printer.logging(f"Ошибка: {compiled.name} уже существует", level="ERROR")
                raise NameAlreadyExist(compiled.name, info=compiled.meta_info)

            self.compiled[compiled.name] = compiled
            printer.logging(f"Скомпилировано: {compiled.name}", level="INFO")

        compiled_without_build_modules = self.compiled
        self.compiled = {**compiled_modules, **self.compiled}

        for name, compiled in compiled_without_build_modules.items():
            if isinstance(compiled, Procedure):
                self.body_compile(compiled.body)

                if compiled.default_arguments is not None:
                    self.compile_default_args(compiled.default_arguments)

            elif isinstance(compiled, ClassDefinition):
                self.body_compile(compiled.constructor.body)
                compiled.constructor.name = compiled.name

                for method in compiled.methods.values():
                    if method.default_arguments is not None:
                        self.compile_default_args(method.default_arguments)
                    self.body_compile(method.body)

                if compiled.methods is None:
                    compiled.methods = {}

                compiled.methods[compiled.constructor_name] = compiled.constructor

                if compiled.constructor.default_arguments is not None:
                    self.compile_default_args(compiled.constructor.default_arguments)

                for cmd in compiled.constructor.body.commands:
                    if isinstance(cmd, Return):
                        raise InvalidSyntaxError(
                            f"Конструктор класса '{compiled.name}' не может содержать '{Tokens.return_}'",
                            info=cmd.expression.meta_info
                        )

        return Compiled(self.compiled)
