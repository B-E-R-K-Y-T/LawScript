from core.types.atomic import String
from core.types.base_declarative_type import BaseDeclarativeType


class Object(BaseDeclarativeType):
    def __init__(self, name: str, name_object: str):
        super().__init__(name)
        self.name_object = name_object  # Имя объекта

        self.fields["__имя_объекта__"] = String(self.name_object)

    def __repr__(self) -> str:
        return f"Object(name_object='{self.name_object}')"

