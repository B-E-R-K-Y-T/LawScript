import queue
import tkinter as tk
from multiprocessing import Queue, Process
from tkinter import scrolledtext, messagebox, Text, ttk
import re
import sys

from config import settings
from src.core.call_func_stack import get_stack_pretty_str
from src.core.tokens import Tokens
from src.util.build_tools.build import build
from src.util.build_tools.starter import run_file, run_string
from src.util.console_worker import printer


class ModernButton(tk.Button):
    """Современная кнопка с градиентом и эффектами"""

    def __init__(self, master=None, **kwargs):
        self.style = kwargs.pop('style', 'primary')
        super().__init__(master, **kwargs)
        self.configure(self.get_style_config())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<ButtonPress-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)

    def get_style_config(self):
        styles = {
            'primary': {
                'bg': '#007acc',
                'fg': 'white',
                'activebackground': '#005a9e',
                'activeforeground': 'white',
                'relief': 'flat',
                'font': ('Segoe UI', 10, 'bold'),
                'padx': 15,
                'pady': 8,
                'borderwidth': 0,
                'cursor': 'hand2'
            },
            'danger': {
                'bg': '#dc3545',
                'fg': 'white',
                'activebackground': '#c82333',
                'activeforeground': 'white',
                'relief': 'flat',
                'font': ('Segoe UI', 10),
                'padx': 15,
                'pady': 8,
                'borderwidth': 0,
                'cursor': 'hand2'
            },
            'warning': {
                'bg': '#ffc107',
                'fg': '#212529',
                'activebackground': '#e0a800',
                'activeforeground': '#212529',
                'relief': 'flat',
                'font': ('Segoe UI', 10, 'bold'),
                'padx': 15,
                'pady': 8,
                'borderwidth': 0,
                'cursor': 'hand2'
            },
            'secondary': {
                'bg': '#6c757d',
                'fg': 'white',
                'activebackground': '#545b62',
                'activeforeground': 'white',
                'relief': 'flat',
                'font': ('Segoe UI', 9),
                'padx': 10,
                'pady': 5,
                'borderwidth': 0,
                'cursor': 'hand2'
            }
        }
        return styles.get(self.style, styles['secondary'])

    def on_enter(self, e):
        self['bg'] = self['activebackground']

    def on_leave(self, e):
        self['bg'] = self.get_style_config()['bg']

    def on_press(self, e):
        self['bg'] = self['activebackground']

    def on_release(self, e):
        self['bg'] = self['activebackground']


class LineNumbers(Text):
    """Виджет для отображения номеров строк"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = None
        self.bg_color = '#1e1e1e'
        self.fg_color = '#858585'
        self.current_line_color = '#2e2e2e'

        self.config(
            state='disabled',
            width=6,
            padx=5,
            pady=5,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Consolas", 12),
            relief='flat',
            borderwidth=0,
            takefocus=0,
            insertwidth=0,
            highlightthickness=0
        )

        self.tag_configure("current_line", background=self.current_line_color)

    def set_text_widget(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.bind('<KeyRelease>', self.update_line_numbers)
        self.text_widget.bind('<MouseWheel>', self.update_line_numbers)
        self.text_widget.bind('<Button-1>', self.update_line_numbers)
        self.text_widget.bind('<Key>', lambda e: self.after(10, self.update_line_numbers))
        self.text_widget.bind('<Motion>', self.update_line_numbers)
        self.bind('<Configure>', self.update_line_numbers)

    def update_line_numbers(self, event=None):
        if self.text_widget is None:
            return

        try:
            first_visible_line = self.text_widget.yview()[0]
            lines = self.text_widget.get('1.0', 'end-1c').count('\n') + 1

            current_line = self.text_widget.index(tk.INSERT).split('.')[0]

            line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))

            self.config(state='normal')
            self.delete('1.0', 'end')
            self.insert('1.0', line_numbers_text)

            self.tag_remove("current_line", "1.0", "end")
            self.tag_add("current_line", f"{current_line}.0", f"{current_line}.end")

            self.config(state='disabled')
            self.yview_moveto(first_visible_line)
        except Exception:
            pass


class OutputRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass


class RealTimeOutputQueue:
    def __init__(self, output_queue):
        self.output_queue = output_queue

    def write(self, string):
        if string:
            self.output_queue.put(("output", string))

    def flush(self):
        pass


class SyntaxHighlighter:
    def __init__(self):
        self.theme = {
            'background': '#1e1e1e',
            'foreground': '#d4d4d4',
            'keywords': '#569cd6',
            'functions': '#dcdcaa',
            'strings': '#ce9178',
            'numbers': '#b5cea8',
            'comments': '#6a9955',
            'operators': '#d4d4d4',
            'brackets': '#ffd700',
            'types': '#4ec9b0'
        }

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
                'color': self.theme['keywords'],
                'case_sensitive': False
            },
            'operators': {
                'words': [
                    Tokens.comment, Tokens.star, Tokens.plus, Tokens.minus,
                    Tokens.equal, Tokens.exponentiation, Tokens.percent,
                    Tokens.div, Tokens.attr_access
                ],
                'color': self.theme['operators'],
                'case_sensitive': True
            },
            'brackets': {
                'words': [
                    Tokens.left_bracket, Tokens.right_bracket,
                    Tokens.left_square_bracket, Tokens.right_square_bracket,
                    Tokens.comma, Tokens.dot, Tokens.end_expr
                ],
                'color': self.theme['brackets'],
                'case_sensitive': True
            },
            'strings': {
                'words': [Tokens.quotation],
                'color': self.theme['strings'],
                'case_sensitive': True
            },
            'comments': {
                'words': [Tokens.comment],
                'color': self.theme['comments'],
                'case_sensitive': True
            },
            'functions': {
                'words': ['print', 'run', 'execute', 'wait', 'check'],
                'color': self.theme['functions'],
                'case_sensitive': False
            }
        }

    def highlight(self, text_widget):
        for tag in text_widget.tag_names():
            if tag not in ["sel", "found", "current_line", "error_line"]:
                text_widget.tag_remove(tag, "1.0", tk.END)

        content = text_widget.get("1.0", tk.END)

        for group_name, group_data in self.keyword_groups.items():
            color = group_data['color']
            case_sensitive = group_data.get('case_sensitive', False)

            if group_name == 'comments':
                self.highlight_comments(text_widget, content, color)
                continue

            if group_name == 'strings':
                self.highlight_strings(text_widget, content, color)
                continue

            for keyword in group_data['words']:
                pattern = self.create_pattern(keyword, case_sensitive)
                matches = re.finditer(pattern, content)

                for match in matches:
                    start_pos = f"1.0+{match.start()}c"
                    end_pos = f"1.0+{match.end()}c"

                    # Проверяем, что это действительно отдельное слово
                    # а не часть другого слова
                    if not self.is_whole_word(content, match.start(), match.end()):
                        continue

                    tag_name = f"{group_name}_{keyword}"
                    if tag_name not in text_widget.tag_names():
                        text_widget.tag_configure(tag_name, foreground=color)

                    text_widget.tag_add(tag_name, start_pos, end_pos)

    def create_pattern(self, keyword, case_sensitive):
        """Создает regex pattern для поиска ключевых слов"""
        if len(keyword) == 1:  # Одиночные символы (операторы, скобки и т.д.)
            pattern = re.escape(keyword)
        else:  # Многосимвольные ключевые слова
            # Для русского языка нужно использовать негативные просмотры
            pattern = r'(?<![а-яА-ЯёЁa-zA-Z0-9_])' + re.escape(keyword) + r'(?![а-яА-ЯёЁa-zA-Z0-9_])'

        if not case_sensitive:
            pattern = re.compile(pattern, re.IGNORECASE)
        return pattern

    def is_whole_word(self, text, start, end):
        """Проверяет, является ли найденное совпадение целым словом"""
        # Проверяем символ перед словом
        if start > 0:
            char_before = text[start - 1]
            # Если перед словом буква, цифра или подчеркивание - это часть другого слова
            if char_before.isalpha() or char_before.isdigit() or char_before == '_':
                return False

        # Проверяем символ после слова
        if end < len(text):
            char_after = text[end]
            # Если после слова буква, цифра или подчеркивание - это часть другого слова
            if char_after.isalpha() or char_after.isdigit() or char_after == '_':
                return False

        return True

    def highlight_comments(self, text_widget, content, color):
        lines = content.split('\n')
        for i, line in enumerate(lines):
            comment_pos = line.find(Tokens.comment)
            if comment_pos != -1:
                start_pos = f"{i + 1}.{comment_pos}"
                end_pos = f"{i + 1}.end"
                tag_name = f"comment_{i}"
                if tag_name not in text_widget.tag_names():
                    text_widget.tag_configure(tag_name, foreground=color)
                text_widget.tag_add(tag_name, start_pos, end_pos)

    def highlight_strings(self, text_widget, content, color):
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
        self.root.title("⚖️ LawScript IDE")
        self.root.geometry("1200x800")

        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        self.setup_styles()

        self.highlighter = SyntaxHighlighter()
        self.current_file_path = None
        self.output_redirector = None

        self.colors = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d30',
            'bg_tertiary': '#252526',
            'fg_primary': '#d4d4d4',
            'fg_secondary': '#858585',
            'accent': '#007acc',
            'success': '#0dbc79',
            'warning': '#e5c07b',
            'error': '#f44747',
            'border': '#3e3e42'
        }

        self.create_widgets()
        self.bind_events()
        self.setup_keybindings()
        self.setup_output_redirector()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TLabel', background='#2d2d30', foreground='#d4d4d4')
        style.configure('TButton', background='#007acc', foreground='white')
        style.configure('TCheckbutton', background='#2d2d30', foreground='#d4d4d4')
        style.configure('TRadiobutton', background='#2d2d30', foreground='#d4d4d4')
        style.configure('TFrame', background='#2d2d30')
        style.configure('TLabelframe', background='#2d2d30', foreground='#d4d4d4')
        style.configure('TLabelframe.Label', background='#2d2d30', foreground='#d4d4d4')

    def update_line_numbers_scroll(self, *args):
        if hasattr(self, 'line_numbers'):
            self.line_numbers.yview_moveto(args[0])

    def create_widgets(self):
        main_container = tk.Frame(self.root, bg=self.colors['bg_secondary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.create_top_bar(main_container)
        self.create_main_area(main_container)
        self.create_status_bar()
        self.create_menu()

    def create_top_bar(self, parent):
        top_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], height=50)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=(0, 1))
        top_frame.pack_propagate(False)

        logo_frame = tk.Frame(top_frame, bg=self.colors['bg_tertiary'])
        logo_frame.pack(side=tk.LEFT, padx=15)

        logo_label = tk.Label(
            logo_frame,
            text="⚖️ LawScript IDE",
            font=("Segoe UI", 14, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_tertiary']
        )
        logo_label.pack(side=tk.LEFT)

        toolbar_frame = tk.Frame(top_frame, bg=self.colors['bg_tertiary'])
        toolbar_frame.pack(side=tk.LEFT, padx=20)

        buttons = [
            ("📁", "Новый", self.new_file, 'secondary'),
            ("📂", "Открыть", self.open_file, 'secondary'),
            ("💾", "Сохранить", self.save_file, 'secondary'),
            ("▶️", "Запуск", self.run_code, 'primary'),
            ("⏹️", "Стоп", self.stop_execution, 'danger'),
            ("⚡", "Собрать", self.build_code, 'warning'),
            ("🗑️", "Очистить", self.clear_output, 'secondary'),
        ]

        for icon, text, command, style in buttons:
            btn = ModernButton(
                toolbar_frame,
                text=f" {icon} {text}",
                command=command,
                style=style
            )
            btn.pack(side=tk.LEFT, padx=2)

        self.file_info_label = tk.Label(
            top_frame,
            text="Файл не сохранен",
            font=("Segoe UI", 10),
            fg=self.colors['fg_secondary'],
            bg=self.colors['bg_tertiary']
        )
        self.file_info_label.pack(side=tk.RIGHT, padx=15)

    def create_main_area(self, parent):
        paned_window = tk.PanedWindow(
            parent,
            orient=tk.VERTICAL,
            sashwidth=5,
            sashrelief=tk.RAISED,
            sashpad=3,
            bg=self.colors['border']
        )
        paned_window.pack(fill=tk.BOTH, expand=True)

        editor_frame = self.create_editor_frame()
        paned_window.add(editor_frame)

        output_frame = self.create_output_frame()
        paned_window.add(output_frame)

        paned_window.paneconfig(editor_frame, height=500, stretch='always')
        paned_window.paneconfig(output_frame, height=250, stretch='never')

    def create_editor_frame(self):
        editor_frame = tk.Frame(bg=self.colors['bg_primary'])

        editor_container = tk.Frame(editor_frame, bg=self.colors['bg_primary'])
        editor_container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = LineNumbers(editor_container)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        text_frame = tk.Frame(editor_container, bg=self.colors['bg_primary'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(text_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_area = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 12),
            undo=True,
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_primary'],
            selectbackground='#264f78',
            selectforeground='white',
            relief=tk.FLAT,
            highlightthickness=0,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.text_area.yview)
        h_scrollbar.config(command=self.text_area.xview)

        self.line_numbers.set_text_widget(self.text_area)

        def sync_scroll(*args):
            v_scrollbar.set(*args)
            self.update_line_numbers_scroll(args[0])

        self.text_area.config(yscrollcommand=sync_scroll)

        self.text_area.tag_configure("current_line", background='#2e2e2e')
        self.text_area.bind('<KeyRelease>', self.highlight_current_line)
        self.text_area.bind('<ButtonRelease-1>', self.highlight_current_line)

        return editor_frame

    def create_output_frame(self):
        output_frame = tk.Frame(bg=self.colors['bg_tertiary'])

        output_header = tk.Frame(output_frame, bg=self.colors['bg_tertiary'], height=30)
        output_header.pack(side=tk.TOP, fill=tk.X)
        output_header.pack_propagate(False)

        title_label = tk.Label(
            output_header,
            text="Вывод программы",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors['fg_primary'],
            bg=self.colors['bg_tertiary']
        )
        title_label.pack(side=tk.LEFT, padx=10)

        output_buttons_frame = tk.Frame(output_header, bg=self.colors['bg_tertiary'])
        output_buttons_frame.pack(side=tk.RIGHT, padx=5)

        clear_btn = ModernButton(
            output_buttons_frame,
            text="Очистить",
            command=self.clear_output,
            style='secondary'
        )
        clear_btn.pack(side=tk.LEFT, padx=2)

        copy_btn = ModernButton(
            output_buttons_frame,
            text="Копировать",
            command=self.copy_output,
            style='secondary'
        )
        copy_btn.pack(side=tk.LEFT, padx=2)

        self.output_area = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.colors['bg_primary'],
            fg=self.colors['fg_primary'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))

        return output_frame

    def create_status_bar(self):
        status_frame = tk.Frame(self.root, bg=self.colors['bg_tertiary'], height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_pos_label = tk.Label(
            status_frame,
            text="Строка: 1, Колонка: 1",
            font=("Segoe UI", 9),
            fg=self.colors['fg_secondary'],
            bg=self.colors['bg_tertiary']
        )
        self.status_pos_label.pack(side=tk.LEFT, padx=10)

        self.status_exec_label = tk.Label(
            status_frame,
            text="Готов",
            font=("Segoe UI", 9),
            fg=self.colors['success'],
            bg=self.colors['bg_tertiary']
        )
        self.status_exec_label.pack(side=tk.LEFT, padx=10, expand=True)

        self.status_encoding_label = tk.Label(
            status_frame,
            text="UTF-8",
            font=("Segoe UI", 9),
            fg=self.colors['fg_secondary'],
            bg=self.colors['bg_tertiary']
        )
        self.status_encoding_label.pack(side=tk.RIGHT, padx=10)

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root, tearoff=0, bg=self.colors['bg_tertiary'], fg=self.colors['fg_primary'])
        self.root.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors['bg_primary'], fg=self.colors['fg_primary'])
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Открыть Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Сохранить Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Сохранить как...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Запустить файл...", command=self.run_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Выход Ctrl+Q", command=self.exit_editor)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors['bg_primary'], fg=self.colors['fg_primary'])
        self.menu_bar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Повторить Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать Ctrl+X", command=self.cut)
        edit_menu.add_command(label="Копировать Ctrl+C", command=self.copy)
        edit_menu.add_command(label="Вставить Ctrl+V", command=self.paste)
        edit_menu.add_command(label="Удалить Del", command=self.delete)
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все Ctrl+A", command=self.select_all)
        edit_menu.add_command(label="Найти Ctrl+F", command=self.find_text)

        run_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors['bg_primary'], fg=self.colors['fg_primary'])
        self.menu_bar.add_cascade(label="Выполнение", menu=run_menu)
        run_menu.add_command(label="Запустить код F5", command=self.run_code)
        run_menu.add_command(label="Остановить выполнение F6", command=self.stop_execution)
        run_menu.add_separator()
        run_menu.add_command(label="Собрать проект", command=self.build_code)
        run_menu.add_command(label="Очистить вывод", command=self.clear_output)

        help_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors['bg_primary'], fg=self.colors['fg_primary'])
        self.menu_bar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)

    def highlight_current_line(self, event=None):
        self.text_area.tag_remove("current_line", "1.0", "end")
        current_line = self.text_area.index(tk.INSERT).split('.')[0]
        self.text_area.tag_add("current_line", f"{current_line}.0", f"{current_line}.end")

    def copy_output(self):
        text = self.output_area.get(1.0, tk.END)
        if text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_exec_label.config(text="Вывод скопирован", fg=self.colors['success'])

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("400x200")
        about_window.configure(bg=self.colors['bg_primary'])

        tk.Label(
            about_window,
            text="⚖️ LawScript IDE",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg_primary']
        ).pack(pady=20)

        tk.Label(
            about_window,
            text="Интегрированная среда разработки для языка LawScript",
            font=("Segoe UI", 10),
            fg=self.colors['fg_primary'],
            bg=self.colors['bg_primary']
        ).pack(pady=5)

        tk.Label(
            about_window,
            text="Версия 1.0.0",
            font=("Segoe UI", 9),
            fg=self.colors['fg_secondary'],
            bg=self.colors['bg_primary']
        ).pack(pady=5)

    def setup_output_redirector(self):
        self.output_redirector = OutputRedirector(self.output_area)

    def clear_output(self):
        self.output_area.delete(1.0, tk.END)

    def build_code(self):
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
            self.status_exec_label.config(text="Выполнение...", fg=self.colors['warning'])

            try:
                printer.debug = True
                build(file_path)
            except Exception as e:
                msg = f"Ошибка: {e}"
                self.status_exec_label.config(text=msg, fg=self.colors['error'])
            else:
                msg = "Успех!"
                self.status_exec_label.config(text=msg, fg=self.colors['success'])

            printer.debug = settings.debug

    def run_code(self):
        code = self.text_area.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Предупреждение", "Нет кода для выполнения!")
            return

        self.clear_output()
        self.status_exec_label.config(text="Выполнение...", fg=self.colors['warning'])

        self.output_queue = Queue()

        self.execution_process = Process(
            target=self._execute_code_in_process,
            args=(code, self.output_queue)
        )
        self.execution_process.daemon = True
        self.execution_process.start()

        self.monitor_output()

    def monitor_output(self):
        try:
            got_data = False
            while True:
                try:
                    msg_type, content = self.output_queue.get_nowait()
                    got_data = True

                    self.output_area.insert(tk.END, content)
                    self.output_area.see(tk.END)
                    self.output_area.update_idletasks()

                except queue.Empty:
                    break

            if not self.execution_process.is_alive():
                try:
                    while True:
                        msg_type, content = self.output_queue.get_nowait()
                        self.output_area.insert(tk.END, content)
                        self.output_area.see(tk.END)
                        self.output_area.update_idletasks()
                except queue.Empty:
                    pass

                self.output_area.insert(tk.END, "\n=== Выполнение завершено ===\n")
                self.output_area.see(tk.END)
                self.status_exec_label.config(text="Готов", fg=self.colors['success'])
                return

        except Exception as e:
            self.output_area.insert(tk.END, f"Ошибка мониторинга: {e}\n")
            self.status_exec_label.config(text="Ошибка мониторинга", fg=self.colors['error'])

        if self.execution_process.is_alive():
            self.root.after(50, self.monitor_output)

    @staticmethod
    def _execute_code_in_process(code, output_queue):
        try:
            real_time_output = RealTimeOutputQueue(output_queue)

            old_stdout = sys.stdout
            old_stderr = sys.stderr

            sys.stdout = real_time_output
            sys.stderr = real_time_output

            try:
                run_string(code)
            except Exception as e:
                stack_trace = get_stack_pretty_str()
                if stack_trace:
                    stack_trace += "\n"
                printer.print_error(f"{stack_trace}{str(e)}")

        except Exception as e:
            import traceback
            error_msg = f"Ошибка в процессе выполнения: {str(e)}\n{traceback.format_exc()}"
            output_queue.put(("error", error_msg))

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def stop_execution(self):
        if hasattr(self, 'execution_process') and self.execution_process.is_alive():
            self.execution_process.terminate()
            self.execution_process.join(timeout=1.0)

        self.output_area.insert(tk.END, "\n=== Выполнение прервано пользователем ===\n")
        self.output_area.see(tk.END)
        self.status_exec_label.config(text="Выполнение прервано", fg=self.colors['error'])

    def run_file_dialog(self):
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
        self.clear_output()
        self.status_exec_label.config(text=f"Запуск файла: {file_path}", fg=self.colors['warning'])

        try:
            self.output_area.insert(tk.END, f"=== Запуск файла: {file_path} ===\n")

            old_stdout = sys.stdout
            old_stderr = sys.stderr

            sys.stdout = self.output_redirector
            sys.stderr = self.output_redirector

            run_file(file_path)

            self.output_area.insert(tk.END, "\n=== Выполнение завершено ===\n")
            self.status_exec_label.config(text="Готов", fg=self.colors['success'])

        except Exception as e:
            self.output_area.insert(tk.END, f"\nОшибка при запуске файла: {str(e)}\n")
            self.status_exec_label.config(text=f"Ошибка: {str(e)}", fg=self.colors['error'])

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def save_as_file(self):
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

    def setup_keybindings(self):
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<F6>', lambda e: self.stop_execution())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.exit_editor())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())

    def bind_events(self):
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.bind('<<Selection>>', self.update_status_bar)

    def on_key_release(self, event):
        self.update_highlighting()
        self.update_status_bar()
        if hasattr(self, 'line_numbers'):
            self.line_numbers.update_line_numbers()

    def update_highlighting(self):
        self.highlighter.highlight(self.text_area)

    def update_status_bar(self, event=None):
        line, column = self.get_cursor_position()
        self.status_pos_label.config(text=f"Строка: {line}, Колонка: {column}")
        self.highlight_current_line()

    def get_cursor_position(self):
        cursor_pos = self.text_area.index(tk.INSERT)
        line, column = cursor_pos.split('.')
        return int(line), int(column)

    def zoom_in(self):
        self.change_font_size(1)

    def zoom_out(self):
        self.change_font_size(-1)

    def reset_zoom(self):
        self.text_area.configure(font=("Consolas", 12))
        self.output_area.configure(font=("Consolas", 10))
        self.line_numbers.configure(font=("Consolas", 12))

    def change_font_size(self, delta):
        editor_font = self.text_area.cget("font")
        size = int(editor_font.split()[1])
        new_size = max(8, min(24, size + delta))

        self.text_area.configure(font=("Consolas", new_size))
        self.line_numbers.configure(font=("Consolas", new_size))

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
        find_window.configure(bg=self.colors['bg_primary'])

        tk.Label(find_window, text="Найти:", bg=self.colors['bg_primary'], fg=self.colors['fg_primary']).pack(pady=5)
        find_entry = tk.Entry(find_window, width=30, bg=self.colors['bg_primary'], fg=self.colors['fg_primary'])
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
        self.root.title("Новый файл - LawScript IDE")
        self.file_info_label.config(text="Файл не сохранен")
        if hasattr(self, 'line_numbers'):
            self.line_numbers.update_line_numbers()

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
                    self.root.title(f"{file_path} - LawScript IDE")
                    self.file_info_label.config(text=file_path)
                    if hasattr(self, 'line_numbers'):
                        self.line_numbers.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def save_file(self):
        if not self.current_file_path:
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
            else:
                return

        try:
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                content = self.text_area.get(1.0, tk.END)
                file.write(content)
                self.root.title(f"{self.current_file_path} - LawScript IDE")
                self.file_info_label.config(text=self.current_file_path)
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
