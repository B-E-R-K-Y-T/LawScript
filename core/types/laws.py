from core.types.atomic import String
from core.types.base_declarative_type import BaseDeclarativeType


class Law(BaseDeclarativeType):
    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = description  # Описание права

        self.fields["__описание__"] = String(self.description)


    def __repr__(self) -> str:
        return f"Law(description='{self.description}')"
