import cProfile
import pstats
import io

from src.util.build_tools.starter import compile_string, run_compiled_code

raw_code = """
ВКЛЮЧИТЬ стандартная_библиотека.*

ОПРЕДЕЛИТЬ ПРОЦЕДУРУ проц(значение) (
   ВЕРНУТЬ значение + 3;
)

ОПРЕДЕЛИТЬ ПРОЦЕДУРУ главная() (
    ЗАДАТЬ с = Список();

    ЦИКЛ i ОТ 1 ДО 100 (
        с:добавить(1);
    )

    с:для_каждого(проц);

    !НАПЕЧАТАТЬ с:в_массив();
)

ВЫПОЛНИТЬ (
    главная();
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