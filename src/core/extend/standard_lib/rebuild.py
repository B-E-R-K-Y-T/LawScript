from typing import Iterable, Callable, Generator

try:
    from rich.progress import track
except ImportError:
    def track(seq: Iterable[Callable], *, description=None) -> Generator[Callable, None, None]:
        yield from seq
        print("Done!")

from src.core.extend.standard_lib.lib_math.lib import build_module as _math_build
from src.core.extend.standard_lib.lib_str.lib import build_module as _str_build
from src.core.extend.standard_lib.lib_time.lib import build_module as _time_build
from src.core.extend.standard_lib.lib_util.lib import build_module as _util_build
from src.core.extend.standard_lib.lib_structs.lib import build_module as _structs_build
from src.core.extend.standard_lib.lib_web.lib import build_module as _web_build


_BUILDERS = [
    _math_build,
    _str_build,
    _time_build,
    _util_build,
    _structs_build,
    _web_build,
]

if __name__ == '__main__':
    for builder in track(_BUILDERS, description="[green]Building..."):
        builder()
