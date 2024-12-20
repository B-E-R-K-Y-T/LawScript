from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


class Printer:
    def __init__(self):
        self.console = Console()

    def print_error(self, exception: str):
        error_text = Text(exception, style="bold red")
        self.console.print(Panel(error_text, title="Ошибка", title_align="left"))

    def print_success(self, text: str):
        success_text = Text(text, style="bold green")
        self.console.print(Panel(success_text, title="Успех", title_align="left"))

    def print_yellow(self, text: str):
        yellow_text = Text(text, style="bold yellow")
        self.console.print(yellow_text)

    def print_panel(self, content: str, title: str = "Информация", style: str = "bold blue"):
        panel_text = Text(content, style=style)
        self.console.print(Panel(panel_text, title=title, title_align="left"))

    def print_table(self, table_data: dict, title: str):
        table = Table(title=title)
        for heading in table_data.keys():
            table.add_column(heading)

        # Добавляем данные в таблицу
        rows = zip(*table_data.values())
        for row in rows:
            table.add_row(*map(str, row))

        self.console.print(table)

    def print_progress(self, task_name: str):
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(task_name, total=100)
            while not progress.finished:
                progress.update(task, advance=1)

    def print_warning(self, text: str):
        warning_text = Text(text, style="bold magenta")
        self.console.print(Panel(warning_text, title="Предупреждение", title_align="left"))

    def print_info(self, text: str, style: str = "bold white"):
        info_text = Text(text, style=style)
        self.console.print(Panel(info_text, title="Информация", title_align="left"))


printer = Printer()
