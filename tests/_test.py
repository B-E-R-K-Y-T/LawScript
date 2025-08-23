import time

from src.util.build_tools.starter import compile_string, run_compiled_code

code = compile_string(
    """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ сум() (
        ЗАДАТЬ с = 0;
        ЦИКЛ ОТ 1 ДО 1000000 (
            с = с + 1;
            !НАПЕЧАТАТЬ с;
        )
        НАПЕЧАТАТЬ с;
    )
    ВЫПОЛНИТЬ (
        сум();
    )
    """
)


s = time.perf_counter()
run_compiled_code(code)
print(time.perf_counter() - s)
