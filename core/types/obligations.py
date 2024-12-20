"""
    ContractualObligation: Обязанности по договорам.
    TortObligation: Обязанности, возникающие из деликтов (вреда).
    AdministrativeObligation: Обязанности, связанные с административным правом.
    CriminalObligation: Обязанности, возникающие в рамках уголовного права.
    LaborObligation: Обязанности по трудовому праву.
    FamilyObligation: Обязанности по семейному праву.
    TaxObligation: Налоговые обязательства.
"""
from core.types.basetype import BaseType


class Obligation(BaseType):
    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = description  # Описание обязанности

    def __repr__(self) -> str:
        return f"Obligation(description='{self.description}')"


class ContractualObligation(Obligation):
    def __init__(self, description: str, contract_type: str):
        super().__init__(description)
        self.contract_type = contract_type  # Тип договора

    def __repr__(self) -> str:
        return f"ContractualObligation(description='{self.description}', contract_type='{self.contract_type}')"


class TortObligation(Obligation):
    def __init__(self, description: str, damage_type: str):
        super().__init__(description)
        self.damage_type = damage_type  # Тип вреда (имущественный, моральный и т.д.)

    def __repr__(self) -> str:
        return f"TortObligation(description='{self.description}', damage_type='{self.damage_type}')"


class AdministrativeObligation(Obligation):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Кодекса об административных правонарушениях

    def __repr__(self) -> str:
        return f"AdministrativeObligation(description='{self.description}', article={self.article})"


class CriminalObligation(Obligation):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Уголовного кодекса

    def __repr__(self) -> str:
        return f"CriminalObligation(description='{self.description}', article={self.article})"


class LaborObligation(Obligation):
    def __init__(self, description: str, chapter: str):
        super().__init__(description)
        self.chapter = chapter  # Глава Трудового кодекса

    def __repr__(self) -> str:
        return f"LaborObligation(description='{self.description}', chapter='{self.chapter}')"


class FamilyObligation(Obligation):
    def __init__(self, description: str, article: int):
        super().__init__(description)
        self.article = article  # Номер статьи Семейного кодекса

    def __repr__(self) -> str:
        return f"FamilyObligation(description='{self.description}', article={self.article})"


class TaxObligation(Obligation):
    def __init__(self, description: str, tax_type: str):
        super().__init__(description)
        self.tax_type = tax_type  # Тип налога

    def __repr__(self) -> str:
        return f"TaxObligation(description='{self.description}', tax_type='{self.tax_type}')"
