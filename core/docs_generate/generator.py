from jinja2 import Environment, FileSystemLoader
from typing import Type
from dataclasses import dataclass
import os

from core.types.checkers import CheckerSituation
from core.types.conditions import Condition
from core.types.documents import Document, FactSituation
from core.types.laws import Law
from core.types.objects import Object
from core.types.obligations import Obligation
from core.types.procedure import Procedure, CodeBlock, Body, When, Else, ElseWhen, Loop, While
from core.types.rules import Rule
from core.types.sanction_types import SanctionType
from core.types.sanctions import Sanction
from core.types.subjects import Subject
from util.build_tools.compile import Compiled


@dataclass
class FunctionDoc:
    name: str
    docs: str
    args: list[dict[str, str]]
    blocks: list[dict[str, str]]


@dataclass
class SanctionDoc:
    name: str
    article : str


@dataclass
class LawDoc:
    name: str
    desc: str


@dataclass
class RuleDoc:
    name: str
    desc: str


@dataclass
class DutyDoc:
    name: str
    desc: str


@dataclass
class SubjectDoc:
    name: str
    subject_name: str


@dataclass
class ObjectDoc:
    name: str
    name_object: str


@dataclass
class ConditionDoc:
    name: str
    desc: str
    criteria: list[str]


@dataclass
class DocumentDoc:
    name: str
    hypothesis: str
    disposition: str
    sanction: str


@dataclass
class FactSituationDoc:
    name: str
    object_name: str
    subject_name: str
    data: dict[str, str]


@dataclass
class CheckerSituationDoc:
    name: str
    document_name: str
    fact_situation_name: str


class DocsGenerator:
    def __init__(self):
        self.fact_situations = None
        self.verifications = None
        self.documents = None
        self.functions = None
        self.sanctions = None
        self.laws = None
        self.rules = None
        self.duties = None
        self.subjects = None
        self.objects = None
        self.conditions = None

        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def prepare_code(self, compiled_code: Compiled):
        self.functions = self._parse_functions(compiled_code)
        self.sanctions = self._parse_sanctions(compiled_code)
        self.laws = self._parse_laws(compiled_code)
        self.rules = self._parse_rules(compiled_code)
        self.duties = self._parse_duties(compiled_code)
        self.subjects = self._parse_subjects(compiled_code)
        self.objects = self._parse_objects(compiled_code)
        self.conditions = self._parse_conditions(compiled_code)
        self.documents = self._parse_documents(compiled_code)
        self.fact_situations = self._parse_fact_situations(compiled_code)
        self.verifications = self._parse_verifications(compiled_code)

    def _parse_body(self, block: CodeBlock, body: Body, wrap: bool = False) -> list[dict[str, str]]:
        if body.docs is None:
            return []

        translate_block_map: dict[Type[CodeBlock], str] = {
            When: "Если",
            ElseWhen: "Иначе если",
            Else: "Иначе",
            Loop: "Цикл со счетчиком",
            While: "Цикл с условием"
        }
        blocks = [
            {
                "type": translate_block_map[type(block)], "docs": block.body.docs.docs_text, "wrap": wrap
            }
        ]

        for command in body.commands:
            if isinstance(command, CodeBlock):
                blocks.extend(self._parse_body(command, command.body, wrap=True))

        return blocks

    def _parse_functions(self, code: Compiled) -> list[FunctionDoc]:
        functions = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, Procedure):
                default_arguments = obj.default_arguments if obj.default_arguments is not None else {}
                args = [
                    {"name": arg, "docs": "Обязательный" if arg not in default_arguments else "Необязательный"}
                    for arg in obj.arguments_names
                ]
                blocks = []
                main_docs = ""

                if obj.body.docs is not None:
                    main_docs = obj.body.docs.docs_text

                for block in obj.body.commands:
                    if isinstance(block, CodeBlock):
                        blocks.extend(self._parse_body(block, block.body))

                        if isinstance(block, When):
                            for else_when in block.else_whens:
                                blocks.extend(self._parse_body(else_when, else_when.body))

                            if block.else_ is not None:
                                blocks.extend(self._parse_body(block.else_, block.else_.body))

                func = FunctionDoc(name=name, docs=main_docs, args=args, blocks=blocks)

                functions.append(func)

        return functions

    @staticmethod
    def _parse_sanctions(code: Compiled) -> list[SanctionDoc]:
        sanctions = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, SanctionType):
                sanctions.append(
                    SanctionDoc(
                        name=name,
                        article=obj.article
                    )
                )

        return sanctions

    @staticmethod
    def _parse_laws(code: Compiled) -> list[LawDoc]:
        laws = []
        for name, obj in code.compiled_code.items():
            if isinstance(obj, Law):
                laws.append(
                    LawDoc(
                        name=name,
                        desc=obj.description
                    )
                )

        return laws

    @staticmethod
    def _parse_rules(code: Compiled) -> list[RuleDoc]:
        rules = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, Rule):
                rules.append(
                    RuleDoc(
                        name=name,
                        desc=obj.description
                    )
                )

        return rules

    @staticmethod
    def _parse_duties(code: Compiled) -> list[DutyDoc]:
        duties = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, Obligation):
                duties.append(
                    DutyDoc(
                        name=name,
                        desc=obj.description
                    )
                )

        return duties

    @staticmethod
    def _parse_subjects(code: Compiled) -> list[SubjectDoc]:
        subjects = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, Subject):
                subjects.append(
                    SubjectDoc(
                        name=name,
                        subject_name=obj.subject_name
                    )
                )

        return subjects

    @staticmethod
    def _parse_objects(code: Compiled) -> list[ObjectDoc]:
        objects = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, Object):
                objects.append(
                    ObjectDoc(
                        name=name,
                        name_object=obj.name_object
                    )
                )

        return objects

    @staticmethod
    def _parse_conditions(code: Compiled) -> list[ConditionDoc]:
        conditions = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, Condition):
                list_criteria = []

                for name_criteria, modify in obj.criteria.modify.items():
                    list_criteria.append(f"Модификатор: {modify}  Имя критерия: {name_criteria}")

                conditions.append(
                    ConditionDoc(
                        name=name,
                        desc=obj.description,
                        criteria=list_criteria
                    )
                )

        return conditions

    @staticmethod
    def _parse_documents(code: Compiled) -> list[DocumentDoc]:
        documents = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, Document):
                hypothesis = (
                    f"СУБЪЕКТ: {obj.hypothesis.subject.name}\n"
                    f"УСЛОВИЕ: {obj.hypothesis.condition.name}\n"
                    f"ОБЪЕКТ: {obj.hypothesis.object.name}\n"
                )
                disposition = (
                    f"ПРАВО: {obj.disposition.law.name}\n"
                    f"ОБЯЗАННОСТЬ: {obj.disposition.obligation.name}\n"
                    f"ПРАВИЛО: {obj.disposition.rule.name}\n"
                )
                sanction = (
                    f"ТИП САНКЦИИ: {obj.sanction.type}\n"
                    f"СТЕПЕНЬ СТРОГОСТИ: {obj.sanction.severity}\n"
                    f"ПРОЦЕССУАЛЬНЫЙ АСПЕКТ: {obj.sanction.procedural_aspect}\n"
                )

                documents.append(
                    DocumentDoc(
                        name=name,
                        hypothesis=hypothesis,
                        disposition=disposition,
                        sanction=sanction,
                    )
                )

        return documents

    @staticmethod
    def _parse_fact_situations(code: Compiled) -> list[FactSituationDoc]:
        fact_situations = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, FactSituation):
                data = ""

                for key, value in obj.data.items():
                    data += f"{key}: {value}\n"

                fact_situations.append(
                    FactSituationDoc(
                        name=name,
                        object_name=obj.object_.name,
                        subject_name=obj.subject.name,
                        data=data,
                    )
                )

        return fact_situations

    @staticmethod
    def _parse_verifications(code: Compiled) -> list[CheckerSituationDoc]:
        verifications = []

        for name, obj in code.compiled_code.items():
            if isinstance(obj, CheckerSituation):
                verifications.append(
                    CheckerSituationDoc(
                        name=name,
                        document_name=obj.document.name,
                        fact_situation_name=obj.fact_situation.name
                    )
                )

        return verifications

    def generate(self, output_path: str, module: str):
        template = self.env.get_template('base.html')

        context = {
            'title': 'Документация модуля',
            'filename': module,
            'functions': self.functions,
            'sanctions': self.sanctions,
            'laws': self.laws,
            'rules': self.rules,
            'duties': self.duties,
            'subjects': self.subjects,
            'objects': self.objects,
            'conditions': self.conditions,
            'documents': self.documents,
            'fact_situations': self.fact_situations,
            'verifications': self.verifications,
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template.render(context))
