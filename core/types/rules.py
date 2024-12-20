"""
    ConstitutionalRule: Конституционные нормы.
    CivilLawRule: Нормы гражданского права.
    CriminalLawRule: Уголовные нормы.
    AdministrativeRule: Административные нормы.
    LaborLawRule: Нормы трудового права.
    FamilyLawRule: Нормы семейного права.
    InternationalLawRule: Нормы международного права.
"""
from core.types.basetype import BaseType


class Rule(BaseType):
    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = description  # Описание правила

    def __repr__(self) -> str:
        return f"Rule(description='{self.description}')"


class ConstitutionalRule(Rule):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Конституции

    def __repr__(self) -> str:
        return f"ConstitutionalRule(description='{self.description}', article={self.article})"


class CivilLawRule(Rule):
    def __init__(self, description: str, section: str):
        super().__init__(description)
        self.section = section  # Раздел Гражданского кодекса

    def __repr__(self) -> str:
        return f"CivilLawRule(description='{self.description}', section='{self.section}')"


class CriminalLawRule(Rule):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Уголовного кодекса

    def __repr__(self) -> str:
        return f"CriminalLawRule(description='{self.description}', article={self.article})"


class AdministrativeRule(Rule):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Кодекса об административных правонарушениях

    def __repr__(self) -> str:
        return f"AdministrativeRule(description='{self.description}', article={self.article})"


class LaborLawRule(Rule):
    def __init__(self, description: str, chapter: str):
        super().__init__(description)
        self.chapter = chapter  # Глава Трудового кодекса

    def __repr__(self) -> str:
        return f"LaborLawRule(description='{self.description}', chapter='{self.chapter}')"


class FamilyLawRule(Rule):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Семейного кодекса

    def __repr__(self) -> str:
        return f"FamilyLawRule(description='{self.description}', article={self.article})"


class InternationalLawRule(Rule):
    def __init__(self, description: str, treaty_name: str):
        super().__init__(description)
        self.treaty_name = treaty_name  # Название международного договора

    def __repr__(self) -> str:
        return f"InternationalLawRule(description='{self.description}', treaty_name='{self.treaty_name}')"
