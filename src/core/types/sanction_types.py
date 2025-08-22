from src.core.types.atomic import String
from src.core.types.base_declarative_type import BaseDeclarativeType


class SanctionType(BaseDeclarativeType):
    def __init__(self, name: str, type_name: str, article: str):
        super().__init__(name)
        self.type_name = type_name  # Имя вида санкции
        self.article = article  # Статья

        self.fields["__имя_типа__"] = String(self.type_name)
        self.fields["__статья__"] = String(self.article)

    def __repr__(self) -> str:
        return f"SanctionType(type_name='{self.type_name}')"
