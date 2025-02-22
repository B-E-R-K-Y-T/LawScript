import sys
import time

from config import settings
from core.exceptions import BaseError
from core.util import kill_process, success_process, yellow_print
from util.build_tools.build import build
from util.console_worker import printer
from util.build_tools.starter import run_file


class Law:
    @staticmethod
    def run():
        start = time.perf_counter()

        try:
            if len(sys.argv) < 3:
                kill_process("Используйте --build <название файла> или --run <название файла>")

            command = sys.argv[1]
            filename = sys.argv[2]

            if command == '--build':
                printer.debug = True

                if not filename.endswith('.txt'):  # Предполагаем, что источник текстовый файл
                    kill_process("Файл для сборки должен иметь расширение .txt.")

                build(filename)
            elif command == '--run':
                run_file(filename)
            else:
                kill_process("Неизвестная команда. Используйте --build или --run.")

        except BaseError as e:
            kill_process(str(e))
        except Exception as e:
            if settings.debug:
                raise
            printer.print_error(str(e))
        else:
            success_process(f"Операция {command} завершена успешно.")
        finally:
            working_time = time.perf_counter() - start
            yellow_print(f"Затрачено времени: {working_time:.5f}ms")


if __name__ == '__main__':
    # law = Law()
    # law.run()
    file = "new_1.txt"
    # build(file)
    run_file(file)
