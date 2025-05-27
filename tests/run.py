import time
import os

from util.build_tools.starter import run_file

path = os.path.join(os.getcwd(), ".")
test_num = 0

for file in os.listdir("."):
    if file.startswith("test") and file.endswith(".raw"):
        test_num += 1

        time.sleep(0.5)
        print(f"#{test_num}: Запуск файла: {file}")

        run_file(f"{path}/{file}")

        print(f"Тест #{test_num} успешно завершен")
        time.sleep(0.5)
