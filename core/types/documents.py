from typing import Union, Any

from core.types.basetype import BaseType
from core.types.dispositions import Disposition
from core.types.hypothesis import Hypothesis
from core.types.objects import Object
from core.types.sanctions import Sanction
from core.types.subjects import Subject


class Document(BaseType):
    def __init__(self, name: str, hypothesis: Hypothesis, disposition: Disposition, sanction: Sanction):
        super().__init__(name)
        self.hypothesis = hypothesis  # Гипотеза
        self.disposition = disposition  # Диспозиция
        self.sanction = sanction  # Санкция

    def __repr__(self) -> str:
        return (f"Document(\n"
                f"\thypothesis={self.hypothesis}, \n"
                f"\tdisposition={self.disposition}, \n"
                f"\tsanction={self.sanction}\n"
                f")")

class FactSituation(BaseType):
    def __init__(self, name: str, object_: Object, subject: Subject, data: dict[str, Any]):
        super().__init__(name)
        self.object_ = object_
        self.subject = subject
        self.data = data
