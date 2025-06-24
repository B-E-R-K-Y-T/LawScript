from typing import TypeVar, Generic, Iterable, Dict, Optional, List
from core.exceptions import NameNotDefine
from core.types.basetype import BaseType

_T = TypeVar("_T")


class Variable(BaseType, Generic[_T]):
    __slots__ = ('value',)

    def __init__(self, name: str, val: _T):
        super().__init__(name)
        self.value = val

    def get_value(self) -> _T:
        return self.value

    def set_value(self, val: _T) -> None:
        self.value = val

    def __repr__(self) -> str:
        return f"{Variable.__name__}(name={self.name}, value={self.value})"

    def __str__(self) -> str:
        return str(self.value)


class Scope:
    __slots__ = ('variables', 'parent')

    def __init__(self, parent: Optional['Scope'] = None):
        self.variables: Dict[str, Variable] = {}
        self.parent: Optional['Scope'] = parent

    def set(self, variable: Variable) -> None:
        self.variables[variable.name] = variable

    def get(self, name: str) -> Variable:
        if name in self.variables:
            return self.variables[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameNotDefine(f"Переменная '{name}' не определена")


class ScopeStack:
    __slots__ = ('scopes',)

    def __init__(self):
        self.scopes: List[Scope] = [Scope()]

    def push(self) -> None:
        self.scopes.append(Scope(self.scopes[-1]))

    def pop(self) -> None:
        self.scopes.pop()

    def set(self, variable: Variable) -> None:
        self.scopes[-1].set(variable)

    def get(self, name: str) -> Variable:
        return self.scopes[-1].get(name)


class VariableContextCreator:
    __slots__ = ('tree_variables',)

    def __init__(self, tree_variables: ScopeStack):
        self.tree_variables: ScopeStack = tree_variables

    def __enter__(self) -> None:
        self.tree_variables.push()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.tree_variables.pop()


def traverse_scope(scope: Scope) -> Iterable[Variable]:
    for variable in scope.variables.values():
        yield variable

    if scope.parent is not None:
        yield from traverse_scope(scope.parent)


if __name__ == '__main__':
    # Пример использования
    scope_stack = ScopeStack()

    # Создание переменной и добавление в область видимости
    my_variable = Variable('my_var', 42)
    scope_stack.set(my_variable)

    # Получение значения переменной из области видимости
    value = scope_stack.get('my_var')
    print(f"Значение переменной 'my_var': {value}")  # Выведет: 42

    # Изменение значения переменной
    my_variable.set_value(100)
    scope_stack.get(my_variable.name).set_value(12200)  # Обновление в области видимости

    # Получение обновленного значения
    new_value = scope_stack.get('my_var')
    print(f"Обновленное значение переменной 'my_var': {new_value}")  # Выведет: 100
    scope_stack.push()

    print(scope_stack.scopes)
    scope_stack.push()

    scope_stack.set(Variable("var1", []))
    scope_stack.set(Variable("my_var", [1, 1]))

    print(scope_stack.get("my_var"))
    scope_stack.pop()
    print(scope_stack.get("my_var"))

    for scope_ in scope_stack.scopes:
        print(scope_.variables)
