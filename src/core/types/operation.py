from src.core.types.basetype import BaseType


class Operator(BaseType):
    def __init__(self, operator: str):
        super().__init__(operator)
        self.operator = operator
