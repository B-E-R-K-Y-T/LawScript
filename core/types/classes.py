from typing import Optional

from core.types.basetype import BaseType, BaseAtomicType
from core.types.procedure import Procedure, Body, Expression


class Method(Procedure):
    __slots__ = ('this',)

    def __init__(
            self, name: str, body: Body, arguments_names: list[Optional[str]],
            default_arguments: Optional[dict[str, Expression]] = None
    ):
        super().__init__(name, body, arguments_names, default_arguments)
        self.this: Optional['ClassDefinition'] = None
        
        
class Constructor(Method):
    def __init__(
            self, body: Body, arguments_names: list[Optional[str]],
            default_arguments: Optional[dict[str, Expression]] = None
    ):
        super().__init__("", body, arguments_names, default_arguments)


class ClassDefinition(BaseType):
    __slots__ = ('methods', 'constructor', 'parent')

    def __init__(self, name, parent: Optional['ClassDefinition'] = None):
        super().__init__(name)
        self.name = name
        self.parent = parent
        self.methods: dict[str, Method] = {}
        self.constructor: Optional[Constructor] = None

    def create_instance(self, name_class_instance: str) -> 'ClassInstance':
        return ClassInstance(
            name=name_class_instance,
            this=self,
        )


class ClassInstance(BaseType):
    __slots__ = ('this',)

    def __init__(
            self,
            name: str,
            this: ClassDefinition
    ):
        super().__init__(name)
        self.fields: dict[str, BaseAtomicType] = {}
        self.this = this
