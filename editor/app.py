import tkinter as tk
from tkinter import scrolledtext, messagebox
import re

from core.tokens import Tokens


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
                    Tokens.procedure, Tokens.a_procedure, Tokens.table,
                    Tokens.a_table, Tokens.assign, Tokens.when, Tokens.then,
                    Tokens.else_, Tokens.loop, Tokens.from_, Tokens.to,
                    Tokens.while_, Tokens.return_, Tokens.true, Tokens.false,
                    Tokens.continue_, Tokens.break_, Tokens.void, Tokens.wait,
                    Tokens.run, Tokens.in_, Tokens.background, Tokens.execute,
                    Tokens.docs, Tokens.space, Tokens.class_, Tokens.extend,
                    Tokens.constructor, Tokens.method, Tokens.context,
                    Tokens.handler, Tokens.as_
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
        self.root = root
        self.root.title("Текстовый редактор с подсветкой синтаксиса")
        self.root.geometry("800x600")

        self.highlighter = SyntaxHighlighter()

        self.create_widgets()
        self.bind_events()
        self.setup_keybindings()

    def create_widgets(self):
        """Создает элементы интерфейса"""
        # Основное текстовое поле
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Courier New", 12),
            undo=True,
            selectbackground="lightblue"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель статуса
        self.status_bar = tk.Label(self.root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Меню
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Меню Файл
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
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

    def setup_keybindings(self):
        """Настраивает горячие клавиши"""
        # Файл
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-N>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-O>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.exit_editor())
        self.root.bind('<Control-Q>', lambda e: self.exit_editor())

        # Правка
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-Z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-Y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-X>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-C>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-V>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-A>', lambda e: self.select_all())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-F>', lambda e: self.find_text())
        self.root.bind('<Delete>', lambda e: self.delete())

        # Контекстное меню
        self.setup_context_menu()

    def setup_context_menu(self):
        """Создает контекстное меню"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self.cut)
        self.context_menu.add_command(label="Копировать", command=self.copy)
        self.context_menu.add_command(label="Вставить", command=self.paste)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить все", command=self.select_all)

        self.text_area.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        """Показывает контекстное меню"""
        self.context_menu.tk_popup(event.x_root, event.y_root)

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
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
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
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
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
