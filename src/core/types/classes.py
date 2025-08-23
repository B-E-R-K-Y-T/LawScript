from typing import Optional, TypeVar, Generic, TYPE_CHECKING

from src.core.types.atomic import Void
from src.core.types.basetype import BaseType, BaseAtomicType
from src.core.types.procedure import Procedure, Body, Expression

if TYPE_CHECKING:
    from src.core.exceptions import BaseError


class Method(Procedure):
    def __init__(
            self, name: str, body: Body, arguments_names: list[Optional[str]],
            default_arguments: Optional[dict[str, Expression]] = None, this_name: Optional[str] = None
    ):
        super().__init__(name, body, arguments_names, default_arguments)
        self.this_name = this_name
        self.this: Optional['ClassInstance'] = None

    def __str__(self):
        return f"Метод('{self.this_name}:{self.name}') кол-во аргументов: {len(self.arguments_names)}"


class Constructor(Method):
    def __init__(
            self, _, body: Body, arguments_names: list[Optional[str]],
            default_arguments: Optional[dict[str, Expression]] = None, this_name: Optional[str] = None
    ):
        super().__init__("", body, arguments_names, default_arguments, this_name)

    def __str__(self):
        return f"Класс('{self.name}') кол-во аргументов: {len(self.arguments_names)}"


_T = TypeVar('_T', bound=BaseAtomicType)


class ClassField(BaseAtomicType, Generic[_T]):
    def __init__(
            self, value: _T = Void()
    ):
        super().__init__(value)


class ClassDefinition(BaseType):
    def __init__(
            self, name, parent: Optional['ClassDefinition'] = None,
            methods: Optional[dict[str, ClassField[Method]]] = None, constructor: Optional[Constructor] = None
    ):
        super().__init__(name)

        if methods is None:
            methods = {}

        self.parent = parent
        self.constructor = constructor
        self.constructor_name = "__конструктор__"
        self.methods = methods

    def create_instance(self, children: Optional['ClassInstance'] = None) -> 'ClassInstance':
        return ClassInstance(
            class_name=self.name,
            metadata=self,
            children=children
        )

    def __repr__(self):
        return f"Класс('{self.name}')"


class ClassExceptionDefinition(ClassDefinition):
    def __init__(
            self, name, *, base_ex, parent: Optional['ClassDefinition'] = None,
            methods: Optional[dict[str, ClassField[Method]]] = None, constructor: Optional[Constructor] = None
    ):
        super().__init__(name, parent, methods, constructor)
        self.base_ex = base_ex

    def create_instance(
            self, exception_instance: Optional['BaseError'] = None, children: Optional['ClassInstance'] = None
    ) -> 'ClassInstance':
        from src.core.types.atomic import String, Void

        if exception_instance is None:
            exception_instance = Void()

        ex_inst = super().create_instance(children)
        ex_inst.fields = {
            "информация": ClassField(String(str(exception_instance))),
            "__ошибка__": ClassField(BaseAtomicType(exception_instance)),
        }
        return ex_inst


class ClassInstance(BaseAtomicType):
    def __init__(
            self,
            class_name: str,
            metadata: ClassDefinition,
            children: Optional['ClassInstance'] = None
    ):
        super().__init__("")
        self.metadata = metadata
        self.class_name = class_name
        self.value = self
        self.children = children
        self.parent_attr_name = "__родитель__" if self.metadata.parent is not None else None

        if self.metadata.parent is not None:
            self.fields[self.parent_attr_name] = ClassField(self.metadata.parent.create_instance(self))

            for name, method in self.metadata.parent.methods.items():
                if name not in self.metadata.methods and name != self.metadata.constructor_name:
                    self.metadata.methods[name] = method

    def get_attribute(self, name: str) -> ClassField:
        if name in self.metadata.methods:
            return self.metadata.methods[name]

        return super().get_attribute(name)

    def __str__(self):
        return f"Экземпляр('{self.class_name}')"
