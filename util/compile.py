from typing import Type, Union

from core.exceptions import NameNotDefine, InvalidType, UnknownType, NameAlreadyExist, \
    FieldNotDefine
from core.parse.base import Metadata
from core.token import Token
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
from core.types.rules import Rule
from core.types.sanction_types import SanctionType
from core.types.sanctions import Sanction
from core.types.severitys import Severity
from core.types.subjects import Subject


class Compiler:
    def __init__(self, ast: list[Metadata]):
        self.ast = ast
        self.compiled: dict[str, BaseType] = {}

    def get_obj_by_name(self, name: str) -> BaseType:
        for obj_name, obj in self.compiled.items():
            if name == obj.name:
                return obj

        raise NameNotDefine(name)

    def __check_none_type(
            self, obj: Union[BaseType, Metadata], field_name: str, object_name: str
    ) -> Union[str, BaseType]:
        compiled_obj = self.execute_compile(obj)

        if compiled_obj is None:
            raise FieldNotDefine(field_name, object_name)

        return compiled_obj

    def process_literal_field(
            self,
            obj: Union[BaseType, Metadata],
            field_name: str,
            object_name: str,
            type_check: Type[BaseType]
    ) -> BaseType:
        compiled_obj = self.__check_none_type(obj, field_name, object_name)
        compiled_obj = self.get_obj_by_name(compiled_obj)

        if not isinstance(compiled_obj, type_check):
            raise InvalidType(compiled_obj.name, field_name)

        return compiled_obj

    def process_object_field(
            self,
            obj: Union[BaseType, Metadata],
            field_name: str,
            object_name: str,
            type_check: Type[BaseType]
    ) -> BaseType:
        compiled_obj: BaseType = self.__check_none_type(obj, field_name, object_name)

        if not isinstance(compiled_obj, type_check):
            raise InvalidType(compiled_obj.name, field_name)

        return compiled_obj

    def execute_compile(self, meta: Union[BaseType, Metadata]) -> Union[str, BaseType]:
        if not isinstance(meta, Metadata):
            return meta

        compiled_obj = meta.create_image().build()

        if isinstance(compiled_obj, (SanctionType, Rule, Law, Obligation, Severity, Criteria)):
            return compiled_obj

        elif isinstance(compiled_obj, CheckerSituation):
            compiled_obj.document = self.process_literal_field(
                compiled_obj.document, Token.document, Token.check, Document
            )
            compiled_obj.fact_situation = self.process_literal_field(
                compiled_obj.fact_situation,
                f"{Token.actual} {Token.situation}", Token.check, FactSituation
            )

        elif isinstance(compiled_obj, Sanction):
            compiled_obj.type = self.execute_compile(compiled_obj.type)
            compiled_obj.severity = self.execute_compile(compiled_obj.severity)

        elif isinstance(compiled_obj, Disposition):
            compiled_obj.law = self.process_literal_field(
                compiled_obj.law, Token.law, Token.disposition, Law
            )
            compiled_obj.obligation = self.process_literal_field(
                compiled_obj.obligation, Token.duty, Token.disposition, Obligation
            )
            compiled_obj.rule = self.process_literal_field(
                compiled_obj.rule, Token.rule, Token.disposition, Rule
            )

        elif isinstance(compiled_obj, Subject):
            return compiled_obj

        elif isinstance(compiled_obj, Object):
            return compiled_obj

        elif isinstance(compiled_obj, Hypothesis):
            compiled_obj.subject = self.process_literal_field(
                compiled_obj.subject, Token.subject, Token.hypothesis, Subject
            )
            compiled_obj.object = self.process_literal_field(
                compiled_obj.object, Token.object, Token.hypothesis, Object
            )
            compiled_obj.condition = self.process_literal_field(
                compiled_obj.condition, Token.condition, Token.hypothesis, Condition
            )

        elif isinstance(compiled_obj, Condition):
            compiled_obj.criteria = self.process_object_field(
                compiled_obj.criteria,
                Token.criteria,
                Token.condition,
                Criteria
            )

        elif isinstance(compiled_obj, FactSituation):
            compiled_obj.object_ = self.process_literal_field(
                compiled_obj.object_, Token.object, f"{Token.actual} {Token.situation}", Object
            )
            compiled_obj.subject = self.process_literal_field(
                compiled_obj.subject, Token.subject, f"{Token.actual} {Token.situation}", Subject
            )

        elif isinstance(compiled_obj, Document):
            compiled_obj.sanction = self.process_object_field(
                compiled_obj.sanction,
                Token.sanction,
                Token.document,
                Sanction
            )
            compiled_obj.disposition = self.process_object_field(
                compiled_obj.disposition,
                Token.disposition,
                Token.document,
                Disposition
            )
            compiled_obj.hypothesis = self.process_object_field(
                compiled_obj.hypothesis,
                Token.hypothesis,
                Token.document,
                Hypothesis
            )

        else:
            raise UnknownType(f"Невозможно скомпилировать {compiled_obj}")

        return compiled_obj

    def compile(self) -> dict[str, BaseType]:
        for idx, meta in enumerate(self.ast):
            compiled = self.execute_compile(meta)

            if compiled.name in self.compiled:
                raise NameAlreadyExist(compiled.name)

            self.compiled[compiled.name] = compiled

        return self.compiled

