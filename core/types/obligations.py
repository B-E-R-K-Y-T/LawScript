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
