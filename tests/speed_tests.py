import time
from random import randint

from util.build_tools.compile import Compiled
from util.build_tools.starter import compile_string, run_compiled_code

PATH_TO_LIB = "Programs.JetBrains.Toolbox.apps.PyCharm-C.Projects.LawScript.tests.libs.*"

cases = {
    "Простой тест":
    """
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ ТЕСТ_0() (
        НАПЕЧАТАТЬ "ТЕСТ0";
    )
    ВЫПОЛНИТЬ (
        ТЕСТ_0();
    )
    """,
    "Поиск суммы":
    f"""
    ВКЛЮЧИТЬ {PATH_TO_LIB}
    
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ сум() (
        ЗАДАТЬ результат = 0;
        ЗАДАТЬ массив_чисел = массив({", ".join(map(str, range(100)))});
        ЗАДАТЬ длина = длина_массива(массив_чисел);
        
        ЦИКЛ текущий_индекс ОТ 0 ДО длина-1 (
            результат = результат + достать_из_массива(массив_чисел, текущий_индекс);
        )
        
        НАПЕЧАТАТЬ результат;
    )
    
    ВЫПОЛНИТЬ (
        сум();
    )
    """,
    "Сортировка массива":
    f"""
    ВКЛЮЧИТЬ {PATH_TO_LIB}
    
    ОПРЕДЕЛИТЬ ПРОЦЕДУРУ сортировка_массива(массив_чисел) (
        ЗАДАТЬ длина = длина_массива(массив_чисел);
        ЗАДАТЬ min_idx = 0;
        
        ЦИКЛ i ОТ 0 ДО длина-1 (
            # Находим минимальный элемент в оставшейся части массива
            min_idx = i;
            
            ЦИКЛ j ОТ i+1 ДО длина-1 (
                ЕСЛИ достать_из_массива(массив_чисел, j) МЕНЬШЕ достать_из_массива(массив_чисел, min_idx) ТО (
                    min_idx = j;
                )
            )
            
            # Меняем местами найденный минимальный элемент с текущим
            ЕСЛИ min_idx НЕРАВНО i ТО (
                ЗАДАТЬ temp = достать_из_массива(массив_чисел, i);
                изменить_в_массиве(массив_чисел, i, достать_из_массива(массив_чисел, min_idx));
                изменить_в_массиве(массив_чисел, min_idx, temp);
            )
        )
        
        НАПЕЧАТАТЬ массив_чисел;
    )
    
    ВЫПОЛНИТЬ (
        сортировка_массива(массив({", ".join([str(randint(0, 100)) for _ in range(100)])}));
    )
    """
}

compiled_cases: dict[str, Compiled] = {}

for name, code in cases.items():
    print(f"Компиляция тест-кейса: {name}")
    compiled_cases[name] = compile_string(code)
    print(f"Тест-кейс успешно скомпилирован: {name}")

results: list[str] = []

print("\nЗапуск тестов...")

for name, code in compiled_cases.items():
    print(f"Запуск тест-кейса: {name}")
    st0 = time.perf_counter()
    run_compiled_code(code)
    st1 = time.perf_counter()
    print(f"Тест-кейс успешно пройден: {name}")

    results.append(f"{name}: {st1 - st0}")

print("\nРезультаты:")
print("\n".join(results))
