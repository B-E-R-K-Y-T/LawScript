"""
    Individual: Для физических лиц.
    LegalEntity: Для юридических лиц.
    StateAuthority: Для государственных органов.
    PublicOrganization: Для общественных организаций.
    Municipality: Для муниципальных образований.
    ForeignEntity: Для иностранных субъектов.
"""
from core.types.basetype import BaseType


class Subject(BaseType):
    def __init__(self, name: str, subject_name: str):
        super().__init__(name)
        self.subject_name = subject_name  # Имя субъекта

    def __repr__(self) -> str:
        return f"Subject(name='{self.name}')"
