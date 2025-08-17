from core.types.atomic import Void, String
from core.types.basetype import BaseType, BaseAtomicType
from core.types.classes import ClassField


class BaseDeclarativeType(BaseType):
    def __init__(self, name: str):
        super().__init__(name)
        self.fields: dict[str, BaseAtomicType] = {"__имя__": String(self.name)}

    def get_attribute(self, name: str) -> BaseAtomicType:
        return ClassField(self.fields.get(name, Void()))
