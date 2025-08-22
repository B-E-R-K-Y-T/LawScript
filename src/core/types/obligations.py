from src.core.types.atomic import String
from src.core.types.base_declarative_type import BaseDeclarativeType


class Obligation(BaseDeclarativeType):
    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = description  # Описание обязанности

        self.fields["__описание__"] = String(self.description)

    def __repr__(self) -> str:
        return f"Obligation(description='{self.description}')"
