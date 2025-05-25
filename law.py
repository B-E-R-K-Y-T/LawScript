import sys
import time

from config import settings
from core.call_func_stack import get_stack_pretty_str
from core.exceptions import BaseError
from core.util import kill_process, success_process, yellow_print
from util.build_tools.build import build
from util.console_worker import printer
from util.build_tools.starter import run_file

printer.debug = settings.debug


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

                if not filename.endswith(f'.{settings.raw_postfix}'):
                    kill_process(f"Файл для сборки должен иметь расширение '.{settings.raw_postfix}'.")

                build(filename)
            elif command == '--run':
                run_file(filename)
            else:
                kill_process("Неизвестная команда. Используйте --build или --run.")

        except BaseError as e:
            if settings.debug:
                raise

            kill_process(f"{get_stack_pretty_str()}\n{str(e)}")
        except Exception as e:
            if settings.debug:
                raise

            printer.print_error(f"{get_stack_pretty_str()}\n{str(e)}")
        else:
            success_process(f"Операция {command} завершена успешно.")
        finally:
            working_time = time.perf_counter() - start
            yellow_print(f"Затрачено времени: {working_time:.5f}ms")


if __name__ == '__main__':
    law = Law()
    # law.run()
    file = "new_4.raw"
    run_file(file)
