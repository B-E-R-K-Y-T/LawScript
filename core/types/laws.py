"""
    ConstitutionalRight: Констиционные права.
    CivilRight: Гражданские права.
    CriminalRight: Уголовные права.
    AdministrativeRight: Административные права.
    LaborRight: Трудовые права.
    FamilyRight: Семейные права.
    PropertyRight: Права на собственность.
    InternationalRight: Международные права.
"""
from core.types.basetype import BaseType


class Law(BaseType):
    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = description  # Описание права

    def __repr__(self) -> str:
        return f"Law(description='{self.description}')"


class ConstitutionalLaw(Law):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Конституции

    def __repr__(self) -> str:
        return f"ConstitutionalRight(description='{self.description}', article={self.article})"


class CivilLaw(Law):
    def __init__(self, description: str, section: str):
        super().__init__(description)
        self.section = section  # Раздел Гражданского кодекса

    def __repr__(self) -> str:
        return f"CivilRight(description='{self.description}', section='{self.section}')"


class CriminalLaw(Law):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Уголовного кодекса

    def __repr__(self) -> str:
        return f"CriminalRight(description='{self.description}', article={self.article})"


class AdministrativeLaw(Law):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Кодекса об административных правонарушениях

    def __repr__(self) -> str:
        return f"AdministrativeRight(description='{self.description}', article={self.article})"


class LaborLaw(Law):
    def __init__(self, description: str, chapter: str):
        super().__init__(description)
        self.chapter = chapter  # Глава Трудового кодекса

    def __repr__(self) -> str:
        return f"LaborRight(description='{self.description}', chapter='{self.chapter}')"


class FamilyLaw(Law):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Семейного кодекса

    def __repr__(self) -> str:
        return f"FamilyRight(description='{self.description}', article={self.article})"


class PropertyLaw(Law):
    def __init__(self, description: str, property_type: str):
        super().__init__(description)
        self.property_type = property_type  # Тип собственности (частная, муниципальная, государственная)

    def __repr__(self) -> str:
        return f"PropertyRight(description='{self.description}', property_type='{self.property_type}')"


class InternationalLaw(Law):
    def __init__(self, description: str, treaty_name: str):
        super().__init__(description)
        self.treaty_name = treaty_name  # Название международного договора

    def __repr__(self) -> str:
        return f"InternationalRight(description='{self.description}', treaty_name='{self.treaty_name}')"
