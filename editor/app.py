import tkinter as tk
from tkinter import scrolledtext
from tkinter import Menu, messagebox, filedialog
from enum import StrEnum

from util.interpreter import run_file


class Token(StrEnum):
    comment = "#"
    start_body = "("
    end_body = ")"
    comma = ","
    quotation = "\""
    define = "ОПРЕДЕЛИТЬ"
    types = "ТИПЫ"
    degree = "СТЕПЕНЬ"
    of_rigor = "СТРОГОСТИ"
    of_sanction = "САНКЦИЯ"
    sanction = "САНКЦИЯ"
    procedural = "ПРОЦЕССУАЛЬНЫЙ"
    aspect = "АСПЕКТ"
    hypothesis = "ГИПОТЕЗА"
    subject = "СУБЪЕКТ"
    object = "ОБЪЕКТ"
    condition = "УСЛОВИЕ"
    article = "СТАТЬЯ"
    create = "СОЗДАТЬ"
    document = "ДОКУМЕНТ"
    disposition = "ДИСПОЗИЦИЯ"
    right = "ПРАВО"
    duty = "ОБЯЗАННОСТЬ"
    rule = "ПРАВИЛО"
    include = "ВКЛЮЧИТЬ"
    the_actual = "ФАКТИЧЕСКУЮ"
    the_situation = "СИТУАЦИЮ"
    actual = "ФАКТИЧЕСКАЯ"
    situation = "СИТУАЦИЯ"
    check = "ПРОВЕРКА"
    description = "ОПИСАНИЕ"
    name = "ИМЯ"


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("LawScript редактор")

        # Настраиваем поведение окна
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        # Создаем текстовое поле для редактирования
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.text_area.grid(row=0, sticky="nsew")  # Расширяем текстовое поле по всему окну

        # Создаем текстовое поле для консольного вывода
        self.console_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', height=10)
        self.console_output.grid(row=1, sticky="nsew")  # Консольное поле внизу окна

        # Создаем меню
        menu = Menu(root)
        root.config(menu=menu)

        # Подменю "Файл"
        file_menu = Menu(menu)
        menu.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить как...", command=self.save_file)
        file_menu.add_command(label="Запустить", command=self.run_code)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=root.quit)

        # Подменю "Справка"
        help_menu = Menu(menu)
        menu.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_help)

        # Связываем событие изменения текста
        self.text_area.bind('<<Modified>>', self.highlight_keywords)

    def highlight_keywords(self, event=None):
        # Удаляем все подсветки
        self.text_area.tag_remove("keyword", "1.0", tk.END)

        # Перебираем все токены и добавляем их подсветку
        for token in Token:
            start_idx = '1.0'
            while True:
                start_idx = self.text_area.search(token.value, start_idx, stopindex=tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(token.value)}c"
                self.text_area.tag_add("keyword", start_idx, end_idx)
                start_idx = end_idx

        # Настройка стиля для подсветки
        self.text_area.tag_config("keyword", foreground="blue", font=("Arial", 10, "bold"))

        # Сбрасываем модификацию текста
        self.text_area.edit_modified(False)

    def run_code(self):
        # Берем текст из текстового поля

        run_file(self.save_file())
        code = self.text_area.get("1.0", tk.END).strip()

        # Очищаем консоль перед выводом
        self.console_output.configure(state='normal')
        self.console_output.delete("1.0", tk.END)

        # Здесь можно реализовать логику выполнения кода
        if code:
            self.console_output.insert(tk.END, "Запуск кода...\n")
            # Пример вывода: просто выведем текст кода в консоль
            self.console_output.insert(tk.END, f"Код:\n{code}\n")
            self.console_output.insert(tk.END, "Код выполнен!\n")
        else:
            self.console_output.insert(tk.END, "Нет кода для выполнения.\n")

        self.console_output.configure(state='disabled')  # Отключаем редактирование

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".lws",
                                                 filetypes=[("LWS files", "*.lws"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get("1.0", tk.END))
            messagebox.showinfo("Сохранение", "Файл успешно сохранен!")

        return file_path

    def show_help(self):
        help_text = "Это текстовый редактор, предназначенный для работы с файлами lws.\n\n" \
                    "Функции:\n" \
                    "- Сохранение содержимого\n" \
                    "- Поиск и подсветка ключевых слов\n" \
                    "- Простая кнопка запуска\n\n" \
                    "Версия 1.0"
        messagebox.showinfo("Справка", help_text)


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
