from src.core.types.base_declarative_type import BaseDeclarativeType
from src.core.types.conditions import Condition
from src.core.types.objects import Object
from src.core.types.subjects import Subject


class Hypothesis(BaseDeclarativeType):
    def __init__(self, name: str, subject: Subject, object_: Object, condition: Condition):
        super().__init__(name)
        self.subject = subject
        self.object = object_
        self.condition = condition

    def __repr__(self) -> str:
        return f"Hypothesis(subjects={self.subject}, objects={self.object}, conditions={self.condition})"
