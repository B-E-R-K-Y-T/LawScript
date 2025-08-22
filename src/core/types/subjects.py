from src.core.types.atomic import String
from src.core.types.base_declarative_type import BaseDeclarativeType


class Subject(BaseDeclarativeType):
    def __init__(self, name: str, subject_name: str):
        super().__init__(name)
        self.subject_name = String(subject_name)

        self.fields["__имя_субъекта__"] = self.subject_name

    def __repr__(self) -> str:
        return f"Subject(name='{self.name}')"
