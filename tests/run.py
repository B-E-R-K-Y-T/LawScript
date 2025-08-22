import re
import time
import os

from src.util.build_tools.starter import run_file

def extract_number(filename):
    match = re.search(r'test_(\d+)\.raw', filename)
    return int(match.group(1)) if match else 0


path = os.path.join(os.getcwd(), "")
test_num = 0

files = [f for f in os.listdir(".") if f.startswith("test_") and f.endswith(".raw")]
files.sort(key=extract_number)  # Сортируем по числовому значению

for file in files:
    if file.startswith("test") and file.endswith(".raw"):
        test_num += 1

        time.sleep(0.5)
        print(f"#{test_num}: Запуск файла: {file}")

        st0 = time.perf_counter()
        run_file(f"{path}{file}")
        st1 = time.perf_counter()

        print(f"Тест #{test_num}: Время выполнения: {st1 - st0}")
        print(f"Тест #{test_num} успешно завершен")
        time.sleep(0.5)
