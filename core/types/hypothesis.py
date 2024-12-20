from typing import List

from core.types.basetype import BaseType
from core.types.conditions import Condition
from core.types.objects import Object
from core.types.subjects import Subject


class Hypothesis(BaseType):
    def __init__(self, name: str, subject: Subject, object_: Object, condition: Condition):
        super().__init__(name)
        self.subject = subject  # Список субъектов
        self.object = object_  # Список объектов
        self.condition = condition  # Условия применения нормы

    def __repr__(self) -> str:
        return f"Hypothesis(subjects={self.subject}, objects={self.object}, conditions={self.condition})"
