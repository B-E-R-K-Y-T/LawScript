import sys

from core.token import Token

from colorama import init
from colorama import Fore

init()


def is_ignore_line(line: str) -> bool:
    if line.startswith(Token.comment):
        return True

    if not line:
        return True

    return False


def kill_process(exception: str):
    print(Fore.RED + exception)
    sys.exit(1)


def success_process(text: str):
    print(Fore.GREEN + text)
    sys.exit(0)


def yellow_print(text: str):
    print(Fore.YELLOW + text)
