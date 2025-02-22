from typing import TypeVar, Generic, Iterable

from core.types.basetype import BaseType


_T = TypeVar("_T")


class Variable(BaseType, Generic[_T]):
    def __init__(self, name: str, val: _T):
        super().__init__(name)
        self.value = val

    def get_value(self):
        return self.value

    def set_value(self, val: _T):
        self.value = val

    def __repr__(self):
        return f"{Variable.__name__}({self.name=}, {self.value=})"

    def __str__(self):
        return str(self.value)


class Scope:
    def __init__(self, parent=None):
        self.variables: dict[str, Variable] = {}
        self.parent = parent

    def set(self, variable: Variable):
        self.variables[variable.name] = variable

    def get(self, name: str) -> Variable:
        if name in self.variables:
            return self.variables[name]
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' is not defined")


class ScopeStack:
    def __init__(self):
        self.scopes = [Scope()]

    def push(self):
        self.scopes.append(Scope(self.scopes[-1]))

    def pop(self):
        self.scopes.pop()

    def set(self, variable: Variable):
        self.scopes[-1].set(variable)

    def get(self, name) -> Variable:
        return self.scopes[-1].get(name)


class VariableContextCreator:
    def __init__(self, tree_variables: ScopeStack):
        self.tree_variables = tree_variables

    def __enter__(self):
        self.tree_variables.push()

    def __exit__(self, exc_type, exc_val, exc_tb):
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

    for scope in scope_stack.scopes:
        print(scope.variables)
