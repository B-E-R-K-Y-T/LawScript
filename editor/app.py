import queue
import tkinter as tk
from multiprocessing import Queue, Process
from tkinter import scrolledtext, messagebox
import re
import sys

from config import settings
from src.core.call_func_stack import get_stack_pretty_str
from src.core.tokens import Tokens
from src.util.build_tools.build import build
from src.util.build_tools.starter import run_file, run_string
from src.util.console_worker import printer


class OutputRedirector:
    """Перенаправляет вывод в текстовое поле"""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class SyntaxHighlighter:
    def __init__(self):
        # Словарь с группами токенов и их цветами
        self.keyword_groups = {
            'keywords': {
                'words': [
                    Tokens.define, Tokens.print_, Tokens.types, Tokens.degree,
                    Tokens.of_rigor, Tokens.of_sanction, Tokens.sanction,
                    Tokens.procedural, Tokens.aspect, Tokens.hypothesis,
                    Tokens.subject, Tokens.object, Tokens.condition,
                    Tokens.article, Tokens.create, Tokens.document,
                    Tokens.disposition, Tokens.law, Tokens.duty, Tokens.rule,
                    Tokens.include, Tokens.the_actual, Tokens.the_situation,
                    Tokens.actual, Tokens.situation, Tokens.check,
                    Tokens.description, Tokens.name, Tokens.criteria,
                    Tokens.only, Tokens.not_, Tokens.may, Tokens.be,
                    Tokens.and_, Tokens.or_, Tokens.bool_equal, Tokens.bool_not_equal,
                    Tokens.less, Tokens.greater, Tokens.between, Tokens.data,
                    Tokens.procedure, Tokens.a_procedure,
                    Tokens.assign, Tokens.when, Tokens.then,
                    Tokens.else_, Tokens.loop, Tokens.from_, Tokens.to,
                    Tokens.while_, Tokens.return_, Tokens.true, Tokens.false,
                    Tokens.continue_, Tokens.break_, Tokens.void, Tokens.wait,
                    Tokens.run, Tokens.in_, Tokens.background, Tokens.execute,
                    Tokens.docs, Tokens.space, Tokens.class_, Tokens.extend,
                    Tokens.constructor, Tokens.method, Tokens.context,
                    Tokens.handler, Tokens.as_, Tokens.blocking,
                ],
                'color': 'blue',
                'case_sensitive': False
            },
            'operators': {
                'words': [
                    Tokens.comment, Tokens.star, Tokens.plus, Tokens.minus,
                    Tokens.equal, Tokens.exponentiation, Tokens.percent,
                    Tokens.div, Tokens.attr_access
                ],
                'color': 'red',
                'case_sensitive': True
            },
            'brackets': {
                'words': [
                    Tokens.left_bracket, Tokens.right_bracket,
                    Tokens.left_square_bracket, Tokens.right_square_bracket,
                    Tokens.comma, Tokens.dot, Tokens.end_expr
                ],
                'color': 'purple',
                'case_sensitive': True
            },
            'strings': {
                'words': [Tokens.quotation],
                'color': 'green',
                'case_sensitive': True
            },
            'comments': {
                'words': [Tokens.comment],
                'color': 'gray',
                'case_sensitive': True
            }
        }

    def highlight(self, text_widget):
        """Применяет подсветку синтаксиса"""
        # Сначала удаляем все существующие теги
        for tag in text_widget.tag_names():
            if tag != "sel" and tag != "found":  # Не удаляем теги выделения и поиска
                text_widget.tag_remove(tag, "1.0", tk.END)

        # Получаем весь текст
        content = text_widget.get("1.0", tk.END)

        # Применяем подсветку для каждой группы
        for group_name, group_data in self.keyword_groups.items():
            color = group_data['color']
            case_sensitive = group_data.get('case_sensitive', False)

            for keyword in group_data['words']:
                # Для комментариев обрабатываем всю строку после !
                if group_name == 'comments':
                    self.highlight_comments(text_widget, content, color)
                    continue

                # Для строк обрабатываем текст между кавычками
                if group_name == 'strings':
                    self.highlight_strings(text_widget, content, color)
                    continue

                # Для остальных токенов
                pattern = self.create_pattern(keyword, case_sensitive)
                matches = re.finditer(pattern, content)

                for match in matches:
                    start_pos = f"1.0+{match.start()}c"
                    end_pos = f"1.0+{match.end()}c"

                    # Создаем тег если его еще нет
                    tag_name = f"{group_name}_{keyword}"
                    if tag_name not in text_widget.tag_names():
                        text_widget.tag_configure(tag_name, foreground=color)

                    # Применяем тег
                    text_widget.tag_add(tag_name, start_pos, end_pos)

    def create_pattern(self, keyword, case_sensitive):
        """Создает regex pattern для поиска"""
        if len(keyword) == 1:  # Одиночные символы
            pattern = re.escape(keyword)
        else:  # Многосимвольные ключевые слова
            pattern = r'\b' + re.escape(keyword) + r'\b'

        if not case_sensitive:
            pattern = re.compile(pattern, re.IGNORECASE)
        return pattern

    def highlight_comments(self, text_widget, content, color):
        """Подсвечивает комментарии (всю строку после !)"""
        lines = content.split('\n')
        line_start = 0

        for i, line in enumerate(lines):
            comment_pos = line.find(Tokens.comment)
            if comment_pos != -1:
                start_pos = f"{i + 1}.{comment_pos}"
                end_pos = f"{i + 1}.end"

                tag_name = f"comment_{i}"
                if tag_name not in text_widget.tag_names():
                    text_widget.tag_configure(tag_name, foreground=color)

                text_widget.tag_add(tag_name, start_pos, end_pos)

            line_start += len(line) + 1  # +1 для символа новой строки

    def highlight_strings(self, text_widget, content, color):
        """Подсвечивает строки между кавычками"""
        pattern = r'"(.*?)"'
        matches = re.finditer(pattern, content)

        for match in matches:
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"

            tag_name = f"string_{match.start()}"
            if tag_name not in text_widget.tag_names():
                text_widget.tag_configure(tag_name, foreground=color)

            text_widget.tag_add(tag_name, start_pos, end_pos)


class TextEditor:
    def __init__(self, root):
        self.execution_process = None
        self.output_queue = None
        self.root = root
        self.root.title("Текстовый редактор с подсветкой синтаксиса")
        self.root.geometry("1000x700")

        self.highlighter = SyntaxHighlighter()
        self.current_file_path = None
        self.output_redirector = None

        self.create_widgets()
        self.bind_events()
        self.setup_keybindings()

    def create_widgets(self):
        """Создает элементы интерфейса"""
        # Основная рамка
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Панель инструментов
        self.create_toolbar(main_frame)

        # Разделитель редактора и вывода
        paned_window = tk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Редактор кода
        editor_frame = tk.Frame(paned_window)
        self.text_area = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=("Courier New", 12),
            undo=True,
            selectbackground="lightblue"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        paned_window.add(editor_frame)

        # Панель вывода
        output_frame = tk.Frame(paned_window)
        output_label = tk.Label(output_frame, text="Вывод:", font=("Arial", 10, "bold"))
        output_label.pack(anchor=tk.W)

        self.output_area = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            height=8,
            state=tk.DISABLED,
            bg="#f0f0f0"
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)
        paned_window.add(output_frame)

        # Настройка разделителя (70% редактор, 30% вывод)
        paned_window.paneconfig(editor_frame, stretch="always")
        paned_window.paneconfig(output_frame, stretch="never")
        # paned_window.sashpos(0, int(self.root.winfo_height() * 0.7))

        # Панель статуса
        self.status_bar = tk.Label(self.root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Меню
        self.create_menu()

        # Настройка перенаправления вывода
        self.setup_output_redirector()

    def create_toolbar(self, parent):
        """Создает панель инструментов с кнопками"""
        toolbar = tk.Frame(parent, relief=tk.RAISED, bd=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Кнопка запуска
        run_btn = tk.Button(toolbar, text="▶ Запуск", command=self.run_code,
                            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        run_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Кнопка остановки
        stop_btn = tk.Button(toolbar, text="⏹ Стоп", command=self.stop_execution,
                             bg="#f44336", fg="white", font=("Arial", 10))
        stop_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Кнопка сборки
        build_btn = tk.Button(toolbar, text="⚡ Собрать", command=self.build_code,
                              bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        build_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Разделитель
        separator = tk.Frame(toolbar, width=2, bg="gray", height=20)
        separator.pack(side=tk.LEFT, padx=5, pady=2)

        # Кнопка очистки вывода
        clear_btn = tk.Button(toolbar, text="🧹 Очистить вывод",
                              command=self.clear_output, font=("Arial", 9))
        clear_btn.pack(side=tk.LEFT, padx=2, pady=2)

    def create_menu(self):
        """Создает меню"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Меню Файл
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Запустить файл", command=self.run_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_editor, accelerator="Ctrl+Q")

        # Меню Правка
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Удалить", command=self.delete, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Найти", command=self.find_text, accelerator="Ctrl+F")

        # Меню Выполнение
        run_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Выполнение", menu=run_menu)
        run_menu.add_command(label="Запустить код", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="Остановить выполнение", command=self.stop_execution, accelerator="F6")
        run_menu.add_separator()
        run_menu.add_command(label="Очистить вывод", command=self.clear_output)

    def setup_output_redirector(self):
        """Настраивает перенаправление вывода"""
        self.output_redirector = OutputRedirector(self.output_area)

    def clear_output(self):
        """Очищает область вывода"""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        self.output_area.config(state=tk.DISABLED)

    def build_code(self):
        """Собирает код из файла"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите файл для запуска",
            filetypes=[
                ("Контракты", "*.raw"),
                ("Скомпилированные проекты", "*.law"),
                ("Python расширения", "*.pyl"),
                ("Все файлы", "*.*"),
            ]
        )

        if file_path:
            self.clear_output()
            self.status_bar.config(text="Выполнение...")

            try:
                printer.debug = True
                build(file_path)
            except Exception as e:
                msg = f"Ошибка: {e}"
            else:
                msg = "Успех!"

            printer.debug = settings.debug
            self.clear_output()
            self.status_bar.config(text=msg)

    def run_code(self):
        """Запускает код из редактора"""
        code = self.text_area.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Предупреждение", "Нет кода для выполнения!")
            return

        self.clear_output()
        self.status_bar.config(text="Выполнение...")

        # Создаем очередь для обмена данными между процессами
        self.output_queue = Queue()

        # Запускаем в отдельном процессе чтобы не блокировать GUI
        self.execution_process = Process(
            target=self._execute_code_in_process,
            args=(code, self.output_queue)
        )
        self.execution_process.daemon = True
        self.execution_process.start()

        # Запускаем мониторинг вывода
        self.monitor_output()

    def monitor_output(self):
        """Мониторит вывод из дочернего процесса"""
        try:
            # Пытаемся получить данные из очереди
            while True:
                try:
                    msg_type, content = self.output_queue.get_nowait()

                    if msg_type == "output":
                        self.output_area.config(state=tk.NORMAL)
                        self.output_area.insert(tk.END, content)
                        self.output_area.config(state=tk.DISABLED)

                    elif msg_type == "error":
                        self.output_area.config(state=tk.NORMAL)
                        self.output_area.insert(tk.END, f"\n{content}\n")
                        self.output_area.config(state=tk.DISABLED)

                    elif msg_type == "status":
                        if content == "completed":
                            self.output_area.config(state=tk.NORMAL)
                            self.output_area.insert(tk.END, "\n=== Выполнение завершено ===\n")
                            self.output_area.config(state=tk.DISABLED)
                            self.status_bar.config(text="Готов")
                        elif content == "error":
                            self.status_bar.config(text="Ошибка выполнения")
                        break

                except queue.Empty:
                    break

        except Exception as e:
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert(tk.END, f"Ошибка мониторинга: {e}\n")
            self.output_area.config(state=tk.DISABLED)
            self.status_bar.config(text="Ошибка мониторинга")

        # Продолжаем мониторинг, если процесс еще работает
        if self.execution_process.is_alive():
            self.root.after(100, self.monitor_output)

    @staticmethod
    def _execute_code_in_process(code, output_queue):
        """Выполняет код в отдельном процессе"""
        try:
            # Перенаправляем вывод в очередь
            import sys
            from io import StringIO

            # Захватываем вывод
            old_stdout = sys.stdout
            old_stderr = sys.stderr

            # Создаем буфер для вывода
            output_buffer = StringIO()
            sys.stdout = output_buffer
            sys.stderr = output_buffer

            try:
                run_string(code)
            except Exception as e:
                stack_trace = get_stack_pretty_str()

                if stack_trace:
                    stack_trace += "\n"

                printer.print_error(f"{stack_trace}{str(e)}")
            # Отправляем вывод в очередь
            output = output_buffer.getvalue()
            output_queue.put(("output", output))
            output_queue.put(("status", "completed"))

        except Exception as e:
            import traceback
            error_msg = f"Ошибка: {str(e)}\n{traceback.format_exc()}"
            output_queue.put(("error", error_msg))
            output_queue.put(("status", "error"))

        finally:
            # Восстанавливаем stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def stop_execution(self):
        """Останавливает выполнение"""
        if hasattr(self, 'execution_process') and self.execution_process.is_alive():
            self.execution_process.terminate()  # Более надежное завершение
            self.execution_process.join(timeout=1.0)

        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, "\n=== Выполнение прервано пользователем ===\n")
        self.output_area.config(state=tk.DISABLED)
        self.status_bar.config(text="Выполнение прервано")

    def run_file_dialog(self):
        """Диалог запуска файла"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите файл для запуска",
            filetypes=[
                ("Контракты", "*.raw"),
                ("Скомпилированные проекты", "*.law"),
                ("Python расширения", "*.pyl"),
                ("Все файлы", "*.*"),
            ]
        )

        if file_path:
            self.run_external_file(file_path)

    def run_external_file(self, file_path):
        """Запускает внешний файл"""
        self.clear_output()
        self.status_bar.config(text=f"Запуск файла: {file_path}")

        try:
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert(tk.END, f"=== Запуск файла: {file_path} ===\n")

            # Сохраняем оригинальные stdout/stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr

            # Перенаправляем вывод
            sys.stdout = self.output_redirector
            sys.stderr = self.output_redirector

            run_file(file_path)  # Ваша функция запуска файла

            self.output_area.insert(tk.END, "\n=== Выполнение завершено ===\n")

        except Exception as e:
            self.output_area.insert(tk.END, f"\nОшибка при запуске файла: {str(e)}\n")

        finally:
            # Восстанавливаем оригинальные stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.output_area.config(state=tk.DISABLED)
            self.status_bar.config(text="Готов")

    def save_as_file(self):
        """Сохранить как"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".raw",
            filetypes=[
                ("Контракты", "*.raw"),
                ("Скомпилированные проекты", "*.law"),
                ("Python расширения", "*.pyl"),
                ("Все файлы", "*.*"),
            ]
        )

        if file_path:
            self.current_file_path = file_path
            self.save_file()

    # ... (остальные ваши методы остаются без изменений)
    def setup_keybindings(self):
        """Настраивает горячие клавиши"""
        # Существующие привязки...
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<F6>', lambda e: self.stop_execution())

    def bind_events(self):
        """Привязывает события"""
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.bind('<<Selection>>', self.update_status_bar)

    def on_key_release(self, event):
        """Обработчик отпускания клавиши"""
        self.update_highlighting()
        self.update_status_bar()

    def update_highlighting(self):
        """Обновляет подсветку синтаксиса"""
        self.highlighter.highlight(self.text_area)

    def update_status_bar(self, event=None):
        """Обновляет статус бар"""
        line, column = self.get_cursor_position()
        self.status_bar.config(text=f"Строка: {line}, Колонка: {column}")

    def get_cursor_position(self):
        """Возвращает текущую позицию курсора"""
        cursor_pos = self.text_area.index(tk.INSERT)
        line, column = cursor_pos.split('.')
        return int(line), int(column)

    def undo(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        self.text_area.event_generate("<<Cut>>")

    def copy(self):
        self.text_area.event_generate("<<Copy>>")

    def paste(self):
        self.text_area.event_generate("<<Paste>>")

    def delete(self):
        self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return "break"

    def find_text(self):
        find_window = tk.Toplevel(self.root)
        find_window.title("Найти")
        find_window.geometry("300x100")

        tk.Label(find_window, text="Найти:").pack(pady=5)
        find_entry = tk.Entry(find_window, width=30)
        find_entry.pack(pady=5)

        def find():
            text_to_find = find_entry.get()
            if text_to_find:
                self.text_area.tag_remove("found", "1.0", tk.END)

                start_pos = "1.0"
                while True:
                    start_pos = self.text_area.search(text_to_find, start_pos, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(text_to_find)}c"
                    self.text_area.tag_add("found", start_pos, end_pos)
                    start_pos = end_pos

                self.text_area.tag_config("found", background="yellow")
                find_window.destroy()

        tk.Button(find_window, text="Найти", command=find).pack(pady=5)

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.root.title("Новый файл - Текстовый редактор")

    def open_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Контракты", "*.raw"),
                ("Скомпилированные проекты", "*.law"),
                ("Python расширения", "*.pyl"),
                ("Все файлы", "*.*"),
            ]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.update_highlighting()
                    self.root.title(f"{file_path} - Текстовый редактор")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def save_file(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Контракты", "*.raw"),
                ("Скомпилированные проекты", "*.law"),
                ("Python расширения", "*.pyl"),
                ("Все файлы", "*.*"),
            ]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    content = self.text_area.get(1.0, tk.END)
                    file.write(content)
                    self.root.title(f"{file_path} - Текстовый редактор")
                    messagebox.showinfo("Успех", "Файл сохранен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def exit_editor(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.quit()


def main():
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
