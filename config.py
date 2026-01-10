import os
import sys
from pathlib import Path
from typing import Final

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


_MAX_THREAD_SUGGESTED: Final[int] = os.cpu_count() * 2 - 1 or 1
_MAX_THREAD_SAFE: Final[int] = min(_MAX_THREAD_SUGGESTED * 4, 256)


def get_working_directory() -> Path:
    """Получает корректную рабочую директорию для собранного приложения."""
    if getattr(sys, 'frozen', False):
        # Если приложение собрано PyInstaller
        return Path(sys.executable).parent.resolve()
    else:
        # Если запуск из исходного кода
        return Path(__file__).parent.resolve()


class ScriptDirStorage:
    def __init__(self):
        self.LW_SCRIPT_DIR = ""

script_dir_storage = ScriptDirStorage()
WORKING_DIR = get_working_directory()

class Settings(BaseSettings):
    debug: bool = Field(default=False)
    max_recursion_depth: int = Field(default=10_000)
    raw_postfix: str = Field(default="raw")
    compiled_postfix: str = Field(default="law")
    py_extend_postfix: str = Field(default="pyl")
    max_running_threads_tasks: int = Field(
        default=_MAX_THREAD_SUGGESTED,
        ge=1,
        le=_MAX_THREAD_SAFE
    )
    ttl_thread: float = Field(default=60)
    wait_task_time: float = Field(default=.001)
    std_name: str = Field(default="стандартная_библиотека")
    standard_lib_path_postfix: str = Field(default="/core/extend/standard_lib/modules")
    task_thread_switch_interval: float = Field(default=.00001)
    step_task_size_to_sleep: int = Field(default=10)
    time_to_join_thread: float = Field(default=1)

    @field_validator("std_name")
    def validate_std_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("std_name не может быть пустой строкой")
        return value

    @field_validator("standard_lib_path_postfix")
    def validate_standard_lib_path_postfix(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("standard_lib_path_postfix не может быть пустой строкой")

        if not value.startswith("/"):
            raise ValueError("standard_lib_path_postfix должен начинаться с символа '/'")

        if value.endswith("/"):
            raise ValueError("standard_lib_path_postfix не должен заканчиваться на символ '/'")

        return value

    model_config = SettingsConfigDict(env_file="law_config.env")


try:
    settings = Settings()
    sys.setrecursionlimit(settings.max_recursion_depth)
except Exception as exception:
    console = Console()

    error_text = Text(str(exception), style="bold red")
    console.print(Panel(error_text, title="Ошибка", title_align="left"))

    exit(1)
