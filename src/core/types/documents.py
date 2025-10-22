from src.core.types.atomic import Table, String
from src.core.types.base_declarative_type import BaseDeclarativeType
from src.core.types.basetype import BaseAtomicType
from src.core.types.dispositions import Disposition
from src.core.types.hypothesis import Hypothesis
from src.core.types.objects import Object
from src.core.types.sanctions import Sanction
from src.core.types.subjects import Subject


class Document(BaseDeclarativeType):
    def __init__(self, name: str, hypothesis: Hypothesis, disposition: Disposition, sanction: Sanction):
        super().__init__(name)
        self.hypothesis = hypothesis  # Гипотеза
        self.disposition = disposition  # Диспозиция
        self.sanction = sanction  # Санкция

        self.fields["__санкция__"] = self.sanction

    def __repr__(self) -> str:
        return (f"Document(\n"
                f"\thypothesis={self.hypothesis}, \n"
                f"\tdisposition={self.disposition}, \n"
                f"\tsanction={self.sanction}\n"
                f")")


class FactSituation(BaseDeclarativeType):
    def __init__(self, name: str, object_: Object, subject: Subject, data: dict[str, BaseAtomicType]):
        super().__init__(name)
        self.object_ = object_
        self.subject = subject
        self.data = data

        self.fields["__данные__"] = Table(
            {String(k): v for k, v in self.data.items()}
        )

    def __repr__(self):
        return f"{FactSituation.__name__}(__данные__={self.data})"
