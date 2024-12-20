"""
    AdministrativeSanction: Санкции, применяемые за административные правонарушения.
    CriminalSanction: Санкции в сфере уголовного права.
    CivilSanction: Санкции в области гражданского права.
    EconomicSanction: Экономические санкции.
    DisciplinarySanction: Дисциплинарные санкции.
    TaxSanction: Налоги и санкции в налоговом праве.
    EnvironmentalSanction: Санкции за нарушение экологического законодательства.
"""
from core.types.basetype import BaseType


class SanctionType(BaseType):
    def __init__(self, name: str, type_name: str, article: str):
        super().__init__(name)
        self.type_name = type_name  # Имя вида санкции
        self.article = article  # Имя вида санкции

    def __repr__(self) -> str:
        return f"SanctionType(type_name='{self.type_name}')"


class AdministrativeSanction(SanctionType):
    def __init__(self, penalty: float, article_number: str):
        super().__init__("Административная санкция")
        self.penalty = penalty  # Размер штрафа
        self.article_number = article_number  # Номер статьи Кодекса об административных правонарушениях

    def __repr__(self) -> str:
        return (f"AdministrativeSanction(penalty={self.penalty}, "
                f"article_number='{self.article_number}')")


class CriminalSanction(SanctionType):
    def __init__(self, imprisonment_years: int, fine_amount: float, article_number: str):
        super().__init__("Уголовная санкция")
        self.imprisonment_years = imprisonment_years  # Уголовное лишение свободы
        self.fine_amount = fine_amount  # Штраф
        self.article_number = article_number  # Номер статьи Уголовного кодекса

    def __repr__(self) -> str:
        return (f"CriminalSanction(imprisonment_years={self.imprisonment_years}, "
                f"fine_amount={self.fine_amount}, article_number='{self.article_number}')")


class CivilSanction(SanctionType):
    def __init__(self, compensation_amount: float, article_number: str):
        super().__init__("Гражданская санкция")
        self.compensation_amount = compensation_amount  # Сумма компенсации
        self.article_number = article_number  # Номер статьи Гражданского кодекса

    def __repr__(self) -> str:
        return (f"CivilSanction(compensation_amount={self.compensation_amount}, "
                f"article_number='{self.article_number}')")


class EconomicSanction(SanctionType):
    def __init__(self, type_of_economic_measure: str, details: str):
        super().__init__("Экономическая санкция")
        self.type_of_economic_measure = type_of_economic_measure  # Тип экономической меры
        self.details = details  # Подробности о санкции

    def __repr__(self) -> str:
        return (f"EconomicSanction(type_of_economic_measure='{self.type_of_economic_measure}', "
                f"details='{self.details}')")


class DisciplinarySanction(SanctionType):
    def __init__(self, punishment: str, position: str):
        super().__init__("Дисциплинарная санкция")
        self.punishment = punishment  # Вид дисциплинарного наказания
        self.position = position  # Должность нарушителя

    def __repr__(self) -> str:
        return (f"DisciplinarySanction(punishment='{self.punishment}', "
                f"position='{self.position}')")


class TaxSanction(SanctionType):
    def __init__(self, tax_amount: float, penalty: float):
        super().__init__("Налоговая санкция")
        self.tax_amount = tax_amount  # Размер налога
        self.penalty = penalty  # Размер штрафа за неуплату

    def __repr__(self) -> str:
        return (f"TaxSanction(tax_amount={self.tax_amount}, "
                f"penalty={self.penalty})")


class EnvironmentalSanction(SanctionType):
    def __init__(self, fine_amount: float, article_number: str):
        super().__init__("Экологическая санкция")
        self.fine_amount = fine_amount  # Размер штрафа за экопреступление
        self.article_number = article_number  # Номер статьи экологического законодательства

    def __repr__(self) -> str:
        return (f"EnvironmentalSanction(fine_amount={self.fine_amount}, "
                f"article_number='{self.article_number}')")
