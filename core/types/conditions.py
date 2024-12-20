from abc import ABC, abstractmethod
from typing import Any

from core.types.basetype import BaseType
from core.types.criteria import Criteria


class Modify(ABC):
    def __init__(self, value: Any):
        self.value = value

    @abstractmethod
    def calculate(self, other: Any) -> bool: ...

    def __repr__(self):
        return f"{self.__class__.__name__}"


class Only(Modify):
    def calculate(self, other: Any) -> bool:
        return self.value == other

    def __repr__(self):
        return "Равно"


class LessThan(Modify):
    def calculate(self, other: Any) -> bool:
        return self.value < other

    def __repr__(self):
        return "Меньше чем"


class GreaterThan(Modify):
    def calculate(self, other: Any) -> bool:
        return self.value > other

    def __repr__(self):
        return "Больше чем"


class Between(Modify):
    def __init__(self, lower_bound: Any, upper_bound: Any):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def calculate(self, other: Any) -> bool:
        return self.lower_bound < other < self.upper_bound

    def __repr__(self):
        return "Между"


class NotOnly(Modify):
    def calculate(self, other: Any) -> bool:
        return self.value != other

    def __repr__(self):
        return "Не равно"


class ResultCondition:
    def __init__(self, name_criteria: str, result: bool, modify: Modify):
        self.name_criteria = name_criteria
        self.result = result
        self.modify = modify


class Condition(BaseType):
    def __init__(self, name: str, description: str, criteria: Criteria):
        super().__init__(name)
        self.description = description
        self.criteria = criteria

    def __repr__(self) -> str:
        return f"Condition(description='{self.description}')"

    def execute(self, fact_data: dict[str, Any]) -> dict[str, ResultCondition]:
        result = {}

        for name_fact_data, value_fact_data in fact_data.items():
            if name_fact_data not in self.criteria.modify:
                continue

            modify = self.criteria.modify[name_fact_data]

            try:
                result[name_fact_data] = ResultCondition(
                    name_criteria=name_fact_data,
                    result=modify.calculate(value_fact_data),
                    modify=modify

                )
            except TypeError:
                raise TypeError(f"Произошла ошибка при проверке критерия: '{name_fact_data}'. Не верный тип!\n")

        return result
