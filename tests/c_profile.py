import cProfile
import pstats
import io

from src.util.build_tools.starter import compile_string, run_compiled_code

raw_code = """
ВКЛЮЧИТЬ стандартная_библиотека.*


ОПРЕДЕЛИТЬ ПРОЦЕДУРУ тест_математики() (
    ЗАДАТЬ результат = 0;
    
    ЦИКЛ ОТ 0 ДО 1000 (
        результат = (корень(144) + синус(пи()/2)) * косинус(0) ^ 2 + (2+2)*2;
    )
    
    НАПЕЧАТАТЬ результат;  ! Должно быть ~21.0
)

ВЫПОЛНИТЬ (
    тест_математики();
)
"""
code = compile_string(raw_code)

# Профилируем
profiler = cProfile.Profile()
profiler.enable()

result = run_compiled_code(code)

profiler.disable()

# Выводим результаты
s = io.StringIO()
ps = pstats.Stats(profiler, stream=s).sort_stats('cumtime')
ps.print_stats(20)  # Топ-20 самых медленных функций
print(s.getvalue())