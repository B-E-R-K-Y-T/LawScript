import os
import sys

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class Settings(BaseSettings):
    debug: bool = Field(default=False)
    max_recursion_depth: int = Field(default=10_000)
    raw_postfix: str = Field(default="raw")
    compiled_postfix: str = Field(default="law")
    py_extend_postfix: str = Field(default="pyl")
    max_running_threads_tasks: int = Field(
        # default=min(2, os.cpu_count() or 1),
        default=max(1, os.cpu_count() or 1),
        ge=1,
        le=os.cpu_count() or 1
    )
    ttl_thread: float = Field(default=1)
    wait_task_time: float = Field(default=.001)
    std_name: str = Field(default="стандартная_библиотека")
    standard_lib_path_postfix: str = Field(default="/core/extend/standard_lib/modules")
    task_thread_switch_interval: float = Field(default=.1)
    step_task_size_to_sleep: int = Field(default=10)

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
