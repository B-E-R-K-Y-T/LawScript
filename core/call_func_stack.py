from typing import NamedTuple

from core.types.line import Info


class CallFunc(NamedTuple):
    func_name: str
    meta_info: Info


class CallFuncStackBuilder:
    def __init__(self):
        self.stack: list[CallFunc] = []

    def push(self, func_name: str, meta_info: Info):
        self.stack.append(CallFunc(func_name, meta_info))

    def pop(self):
        return self.stack.pop(-1)

    def __iter__(self):
        return iter(self.stack)

    def __len__(self) -> int:
        return len(self.stack)


call_func_stack_builder = CallFuncStackBuilder()


def get_stack_pretty_str() -> str:
    if not call_func_stack_builder:
        return ""

    call_stack_str = "Стек вызова процедур:\n"

    for call_func in call_func_stack_builder:
        call_stack_str += (
            f"\t\nФайл: '{call_func.meta_info.file}'\n\tПроцедура: '{call_func.func_name}'\n\t"
            f"Номер строки: {call_func.meta_info.num}\n\tСтрока: '{call_func.meta_info.raw_line}'\n"
        )

    return call_stack_str
