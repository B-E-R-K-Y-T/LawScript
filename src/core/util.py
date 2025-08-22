import sys

from src.core.tokens import Tokens
from src.util.build_tools.compile import Compiled
from src.util.console_worker import printer


def is_ignore_line(line: str) -> bool:
    if isinstance(line, Compiled):
        return True

    if line.startswith(Tokens.comment):
        return True

    if not line:
        return True

    return False


def kill_process(exception: str):
    printer.print_error(exception)
    sys.exit(1)


def success_process(text: str):
    printer.print_success(text)
    sys.exit(0)


def yellow_print(text: str):
    printer.print_yellow(text)
