from core.types.basetype import BaseType


class Object(BaseType):
    def __init__(self, name: str, name_object: str):
        super().__init__(name)
        self.name_object = name_object  # Имя объекта

    def __repr__(self) -> str:
        return f"Object(name_object='{self.name_object}')"

