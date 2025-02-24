from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class Settings(BaseSettings):
    debug: bool = Field(default=False)
    raw_prefix: str = Field(default="raw")
    compiled_prefix: str = Field(default="law")

    model_config = SettingsConfigDict(env_file="law_config.env")


try:
    settings = Settings()
except Exception as exception:
    console = Console()

    error_text = Text(str(exception), style="bold red")
    console.print(Panel(error_text, title="Ошибка", title_align="left"))

    exit(1)
