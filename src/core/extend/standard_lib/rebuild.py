import os
from typing import Iterable, Callable, Generator, Union

from config import settings
from src.util.build_tools.build import build
from src.util.console_worker import printer

try:
    from rich.progress import track
except ImportError:
    def track(seq: Iterable[Union[Callable, str]], *, description=None) -> Generator[Union[Callable, str], None, None]:
        yield from seq
        print("Done!")

from src.core.extend.standard_lib.lib_math.lib import build_module as _math_build
from src.core.extend.standard_lib.lib_str.lib import build_module as _str_build
from src.core.extend.standard_lib.lib_time.lib import build_module as _time_build
from src.core.extend.standard_lib.lib_util.lib import build_module as _util_build
from src.core.extend.standard_lib.lib_structs.lib import build_module as _structs_build
from src.core.extend.standard_lib.lib_web.lib import build_module as _web_build
from src.core.extend.standard_lib.lib_types.lib import build_module as _types_build
from src.core.extend.standard_lib.lib_io.lib import build_module as _io_build
from src.core.extend.standard_lib.lib_sys_args.lib import build_module as _sys_args_build
from src.core.extend.standard_lib.lib_game.lib import build_module as _game_build
from src.core.extend.standard_lib.lib_os.lib import build_module as _os_build


_BUILDERS = [
    _math_build,
    _str_build,
    _time_build,
    _util_build,
    _structs_build,
    _web_build,
    _types_build,
    _io_build,
    _sys_args_build,
    _game_build,
    _os_build,
]

if __name__ == '__main__':
    settings.force_overwrite_module = True

    for builder in track(_BUILDERS, description="[green]Building..."):
        builder()

    file_dirs = ['modules/структуры/', 'modules/']

    for file_dir in track(file_dirs, description="[green]Raw module building..."):
        for file in os.listdir(file_dir):
            if file.endswith(settings.raw_postfix):
                build(f'{file_dir}{file}')

    print("Done!")
