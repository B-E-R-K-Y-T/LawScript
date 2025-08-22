from src.core.types.atomic import Void, String
from src.core.types.basetype import BaseType, BaseAtomicType
from src.core.types.classes import ClassField


class BaseDeclarativeType(BaseType):
    def __init__(self, name: str):
        super().__init__(name)
        self.fields: dict[str, BaseAtomicType] = {"__имя__": String(self.name)}

    def get_attribute(self, name: str) -> BaseAtomicType:
        return ClassField(self.fields.get(name, Void()))
