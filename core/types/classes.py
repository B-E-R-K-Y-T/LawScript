from importlib.metadata import metadata
from typing import Optional, Any

from core.types.atomic import Void
from core.types.basetype import BaseType, BaseAtomicType
from core.types.procedure import Procedure, Body, Expression


class Method(Procedure):
    __slots__ = ('this',)

    def __init__(
            self, name: str, body: Body, arguments_names: list[Optional[str]],
            default_arguments: Optional[dict[str, Expression]] = None, this: Optional[str] = None
    ):
        super().__init__(name, body, arguments_names, default_arguments)
        self.this = this
        
        
class Constructor(Method):
    def __init__(
            self, _, body: Body, arguments_names: list[Optional[str]],
            default_arguments: Optional[dict[str, Expression]] = None, this: Optional[str] = None
    ):
        super().__init__("", body, arguments_names, default_arguments, this)

    def __str__(self):
        return f"Класс('{self.name}') кол-во аргументов: {len(self.arguments_names)}"


class ClassField(BaseAtomicType):
    def __init__(
            self, value: Any = Void()
    ):
        super().__init__(value)


class ClassDefinition(BaseType):
    __slots__ = ('methods', 'constructor', 'parent')

    def __init__(
            self, name, parent: Optional['ClassDefinition'] = None,
            methods: Optional[dict[str, Method]] = None, constructor: Optional[Constructor] = None
    ):
        super().__init__(name)
        self.parent = parent
        self.methods = methods
        self.constructor = constructor

    def create_instance(self) -> 'ClassInstance':
        return ClassInstance(
            class_name=self.name,
            metadata=self
        )


class ClassInstance(BaseAtomicType):
    __slots__ = ('this',)

    def __init__(
            self,
            class_name: str,
            metadata: ClassDefinition,
    ):
        super().__init__("")
        self.metadata = metadata
        self.class_name = class_name
        self.value = self

        if self.metadata.methods is not None:
            self.fields.update(self.metadata.methods)

    def get_attribute(self, name: str) -> ClassField:
        return super().get_attribute(name)


    def __str__(self):
        return f"Экземпляр класса '{self.class_name}'"
