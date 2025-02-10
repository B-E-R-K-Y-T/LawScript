from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from core.exceptions import NameNotDefine
from core.executors.procedure import ProcedureExecutor
from core.types.basetype import BaseType
from core.types.criteria import Criteria
from core.types.procedure import Procedure
from core.types.variable import Variable, ScopeStack

if TYPE_CHECKING:
    from util.build_tools.compile import Compiled


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
        return f"Равно {self.value}"


class LessThan(Modify):
    def calculate(self, other: Any) -> bool:
        return other < self.value

    def __repr__(self):
        return f"Меньше чем {self.value}"


class GreaterThan(Modify):
    def calculate(self, other: Any) -> bool:
        return other > self.value

    def __repr__(self):
        return f"Больше чем {self.value}"


class Between(Modify):
    def __init__(self, lower_bound: Any, upper_bound: Any):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def calculate(self, other: Any) -> bool:
        return self.lower_bound < other < self.upper_bound

    def __repr__(self):
        return f"{self.lower_bound} Между {self.upper_bound}"


class NotEqual(Modify):
    def calculate(self, other: Any) -> bool:
        return self.value != other

    def __repr__(self):
        return f"Исключая {self.value}"


class ProcedureModifyWrapper(Modify):
    def __init__(self, modify: Modify):
        super().__init__(modify)
        self.nested_modify = modify

    def calculate(self, other: Any) -> bool:
        return self.nested_modify.calculate(other)

    def __repr__(self):
        return self.nested_modify.__repr__()

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

    def execute(self, fact_data: dict[str, Any], compiled: "Compiled") -> dict[str, ResultCondition]:
        result = {}

        for name_fact_data, value_fact_data in fact_data.items():
            if name_fact_data not in self.criteria.modify:
                continue

            modify = self.criteria.modify.get(name_fact_data)

            if isinstance(self.criteria.modify[name_fact_data], ProcedureModifyWrapper):
                name = modify.nested_modify.value

                if name not in compiled.compiled_code:
                    raise NameNotDefine(name=name)

                procedure: Procedure = compiled.compiled_code[name]

                arg = Variable(procedure.arguments_names[0], value_fact_data)

                procedure.tree_variables = ScopeStack()
                procedure.tree_variables.set(arg)

                executor = ProcedureExecutor(procedure, compiled)

                modify.nested_modify.value = executor.execute()

            try:
                result[name_fact_data] = ResultCondition(
                    name_criteria=name_fact_data,
                    result=modify.calculate(value_fact_data),
                    modify=modify
                )
            except TypeError:
                raise TypeError(f"Произошла ошибка при проверке критерия: '{name_fact_data}'. Не верный тип!\n")

        return result
