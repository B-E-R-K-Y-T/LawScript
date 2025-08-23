import sys
import time
from pathlib import Path

from config import settings
from src.core.background_task.schedule import get_task_scheduler
from src.core.call_func_stack import get_stack_pretty_str
from src.core.exceptions import BaseError
from src.core.util import kill_process, success_process, yellow_print
from src.util.build_tools.build import build
from src.util.console_worker import printer
from src.util.build_tools.starter import run_file

printer.debug = settings.debug
SELF_DIR = Path(__file__).parent.resolve()


def create_absolute_path_to_file(filename: str) -> Path:
    """Создает абсолютный путь к файлу относительно директории скрипта."""
    return (SELF_DIR / filename).resolve()


class Law:
    @staticmethod
    def run():
        start = time.perf_counter()

        try:
            if len(sys.argv) < 3:
                kill_process("Используйте --build <название файла> или --run <название файла>")

            command = sys.argv[1]
            filename = sys.argv[2]
            absolute_file_path = create_absolute_path_to_file(filename)

            if command == '--build':
                printer.debug = True

                if not filename.endswith(f'.{settings.raw_postfix}'):
                    kill_process(f"Файл для сборки должен иметь расширение '.{settings.raw_postfix}'.")

                build(str(absolute_file_path))
            elif command == '--run':
                run_file(str(absolute_file_path))
            else:
                kill_process("Неизвестная команда. Используйте --build или --run.")

        except BaseError as e:
            if settings.debug:
                raise

            stack_trace = get_stack_pretty_str()

            if stack_trace:
                stack_trace += "\n"

            kill_process(f"{stack_trace}{str(e)}")

        except KeyboardInterrupt:
            get_task_scheduler().shutdown()

        except Exception as e:
            if settings.debug:
                raise

            stack_trace = get_stack_pretty_str()

            if stack_trace:
                stack_trace += "\n"

            printer.print_error(f"{stack_trace}{str(e)}")
        else:
            success_process(f"Операция {command} завершена успешно.")
        finally:
            get_task_scheduler().shutdown()
            working_time = time.perf_counter() - start
            yellow_print(f"Затрачено времени: {working_time:.5f}ms")


if __name__ == '__main__':
    law = Law()
    law.run()
    # file = "tests\\test_26.raw"
    # run_file(file)
    # build(file)
