import os
import sys

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class Settings(BaseSettings):
    debug: bool = Field(default=False)
    max_recursion_depth: int = Field(default=4000)
    raw_postfix: str = Field(default="raw")
    compiled_postfix: str = Field(default="law")
    py_extend_postfix: str = Field(default="pyl")
    max_running_threads_tasks: int = Field(default=os.cpu_count() or 1, ge=1, le=os.cpu_count() or 1)
    ttl_thread: float = Field(default=.1)
    wait_task_time: float = Field(default=.001)

    model_config = SettingsConfigDict(env_file="law_config.env")


try:
    settings = Settings()
    sys.setrecursionlimit(settings.max_recursion_depth)
except Exception as exception:
    console = Console()

    error_text = Text(str(exception), style="bold red")
    console.print(Panel(error_text, title="Ошибка", title_align="left"))

    exit(1)
