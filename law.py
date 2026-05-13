import sys
import time
from pathlib import Path

from config import settings, WORKING_DIR, global_storage
from src.core.background_task.schedule import get_task_scheduler
from src.core.call_func_stack import get_stack_pretty_str
from src.core.exceptions import BaseError
from src.core.tokens import Tokens
from src.core.types.execute_block import ExecuteBlock
from src.core.util import kill_process, success_process, yellow_print
from src.util.build_tools.build import build, generate_docs
from src.util.build_tools.compile import Compiled
from src.util.console_worker import printer
from src.util.build_tools.starter import run_file, compile_string, run_compiled_code

printer.debug = settings.debug


def create_absolute_path_to_file(filename: str) -> Path:
    """Создает абсолютный путь к файлу относительно рабочей директории."""
    return (WORKING_DIR / filename).resolve()


class Law:
    def run(self):
        start = time.perf_counter()

        try:
            if len(sys.argv) == 1:
                self.run_interactive()

            if len(sys.argv) < 3:
                kill_process("Используйте --build <название файла> или --run <название файла>")

            command = sys.argv[1]
            filename = sys.argv[2]
            global_storage.SYS_ARGS = sys.argv[3:]
            absolute_file_path = create_absolute_path_to_file(filename)
            global_storage.LW_SCRIPT_DIR = absolute_file_path.parent

            if command == '--build':
                printer.debug = True

                if not filename.endswith(f'.{settings.raw_postfix}'):
                    kill_process(f"Файл для сборки должен иметь расширение '.{settings.raw_postfix}'.")

                compiled = build(str(absolute_file_path))

                generate_docs(str(absolute_file_path), compiled)

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
            yellow_print(f"Затрачено времени: {working_time:.5f}s")

    @staticmethod
    def run_interactive():
        printer.print_info(settings.repl_title)
        start_str = ">>>"
        shift_str = " "
        all_code = Compiled({})

        while True:
            code = input(start_str)

            if code == "выход":
                success_process(f"Операция '{code}' завершена успешно.")

            if code.endswith(Tokens.left_bracket):
                count_left_brackets = 1
                code_storage = [code]
                next_command = ""

                while not next_command.endswith(Tokens.right_bracket) or count_left_brackets != 0:
                    next_command = input(shift_str * 4 * count_left_brackets)

                    if next_command.endswith(Tokens.left_bracket):
                        count_left_brackets += 1
                    elif next_command.endswith(Tokens.right_bracket):
                        count_left_brackets -= 1

                    code_storage.append(next_command)

                code = "\n".join(code_storage)

            compiled_code = compile_string(code)
            last_command = list(compiled_code.compiled_code.values())[-1]

            if isinstance(last_command, ExecuteBlock):
                run_compiled_code(Compiled({**all_code.compiled_code, **compiled_code.compiled_code}))
                continue

            all_code.compiled_code.update(compiled_code.compiled_code)
            run_compiled_code(all_code)


if __name__ == '__main__':
    law = Law()
    law.run()
    # file = "tests\\test_73.raw"
    # run_file(file)
    # build(file)
