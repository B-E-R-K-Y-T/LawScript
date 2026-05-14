import time
from random import randint

from src.util.build_tools.starter import compile_string, run_compiled_code

s1 = time.perf_counter()
code = compile_string(
    f"""
    
ОПРЕДЕЛИТЬ ПРОЦЕДУРУ главная() (
    ЗАДАТЬ tmp = 0;

    ЦИКЛ i ОТ 1 ДО 10000 (
        tmp = 1 + i;
    )

    НАПЕЧАТАТЬ tmp;
)

ВЫПОЛНИТЬ (
    главная();
)
    """
)


s = time.perf_counter()
run_compiled_code(code)
print(time.perf_counter() - s)
print(time.perf_counter() - s1)
