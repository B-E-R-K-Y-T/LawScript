from src.core.types.atomic import String
from src.core.types.base_declarative_type import BaseDeclarativeType


class Rule(BaseDeclarativeType):
    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = String(description)  # Описание правила

        self.fields["__описание__"] = self.description

    def __repr__(self) -> str:
        return f"Rule(description='{self.description}')"
