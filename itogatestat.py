import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# Файлы для хранения данных
QUOTES_FILE = "quotes.json"
HISTORY_FILE = "history.json"

# Предопределённые цитаты (текст, автор, тема)
DEFAULT_QUOTES = [
    {"text": "Будь изменением, которое ты хочешь видеть в мире.", "author": "Махатма Ганди", "topic": "Мотивация"},
    {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "topic": "Жизнь"},
    {"text": "Воображение важнее знаний.", "author": "Альберт Эйнштейн", "topic": "Наука"},
    {"text": "Ты упускаешь 100% выстрелов, которые не делаешь.", "author": "Уэйн Гретцки", "topic": "Мотивация"},
    {"text": "Будь собой; остальные роли уже заняты.", "author": "Оскар Уайльд", "topic": "Индивидуальность"},
    {"text": "Единственный способ сделать отличную работу — любить то, что ты делаешь.", "author": "Стив Джобс", "topic": "Работа"},
]

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Загрузка данных
        self.quotes = self.load_quotes()
        self.history = self.load_history()

        # Переменные для фильтров
        self.filter_author_var = tk.StringVar()
        self.filter_topic_var = tk.StringVar()

        # Создание GUI
        self.create_widgets()
        self.update_history_display()
        self.update_filters()

    def load_quotes(self):
        """Загружает цитаты из JSON или создаёт файл с умолчаниями"""
        if os.path.exists(QUOTES_FILE):
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            self.save_quotes(DEFAULT_QUOTES)
            return DEFAULT_QUOTES.copy()

    def save_quotes(self, quotes):
        with open(QUOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(quotes, f, ensure_ascii=False, indent=4)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Область отображения цитаты ---
        self.quote_frame = ttk.LabelFrame(main_frame, text="Случайная цитата", padding="10")
        self.quote_frame.pack(fill=tk.X, pady=5)

        self.quote_text = tk.Text(self.quote_frame, height=4, wrap=tk.WORD, font=("Arial", 12))
        self.quote_text.pack(fill=tk.X, padx=5, pady=5)

        # Кнопка генерации
        self.generate_btn = ttk.Button(self.quote_frame, text="🎲 Сгенерировать цитату", command=self.generate_quote)
        self.generate_btn.pack(pady=5)

        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация истории", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        # Фильтр по автору
        ttk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.author_combo = ttk.Combobox(filter_frame, textvariable=self.filter_author_var, state="readonly")
        self.author_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.author_combo.bind("<<ComboboxSelected>>", lambda e: self.update_history_display())

        # Фильтр по теме
        ttk.Label(filter_frame, text="Тема:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.topic_combo = ttk.Combobox(filter_frame, textvariable=self.filter_topic_var, state="readonly")
        self.topic_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.topic_combo.bind("<<ComboboxSelected>>", lambda e: self.update_history_display())

        # Кнопка сброса фильтров
        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=0, column=4, padx=10)

        # --- Добавление новой цитаты ---
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую цитату", padding="10")
        add_frame.pack(fill=tk.X, pady=5)

        ttk.Label(add_frame, text="Текст:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.new_text = tk.Text(add_frame, height=2, width=40)
        self.new_text.grid(row=0, column=1, padx=5, pady=5, columnspan=3)

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.new_author = ttk.Entry(add_frame, width=30)
        self.new_author.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Тема:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.new_topic = ttk.Entry(add_frame, width=20)
        self.new_topic.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(add_frame, text="➕ Добавить цитату", command=self.add_quote).grid(row=2, column=1, pady=10)

        # --- История цитат ---
        history_frame = ttk.LabelFrame(main_frame, text="История сгенерированных цитат", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Список с прокруткой
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Кнопка очистки истории
        ttk.Button(history_frame, text="🗑 Очистить историю", command=self.clear_history).pack(pady=5)

    def update_filters(self):
        """Обновляет выпадающие списки для фильтров"""
        authors = sorted(set(q["author"] for q in self.quotes))
        topics = sorted(set(q["topic"] for q in self.quotes))
        self.author_combo["values"] = ["Все"] + authors
        self.topic_combo["values"] = ["Все"] + topics
        self.filter_author_var.set("Все")
        self.filter_topic_var.set("Все")

    def reset_filters(self):
        self.filter_author_var.set("Все")
        self.filter_topic_var.set("Все")
        self.update_history_display()

    def generate_quote(self):
        """Выбирает случайную цитату и добавляет в историю"""
        if not self.quotes:
            messagebox.showwarning("Нет цитат", "Сначала добавьте хотя бы одну цитату!")
            return

        quote = random.choice(self.quotes)
        display_text = f'"{quote["text"]}"\n— {quote["author"]} (Тема: {quote["topic"]})'
        self.quote_text.delete(1.0, tk.END)
        self.quote_text.insert(tk.END, display_text)

        # Добавляем в историю с датой
        history_entry = {
            "text": quote["text"],
            "author": quote["author"],
            "topic": quote["topic"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        self.save_history()
        self.update_history_display()

    def update_history_display(self):
        """Обновляет отображение истории с учётом фильтров"""
        self.history_listbox.delete(0, tk.END)

        filtered = self.history[:]
        author_filter = self.filter_author_var.get()
        topic_filter = self.filter_topic_var.get()

        if author_filter != "Все":
            filtered = [h for h in filtered if h["author"] == author_filter]
        if topic_filter != "Все":
            filtered = [h for h in filtered if h["topic"] == topic_filter]

        for entry in filtered:
            display = f'[{entry["timestamp"]}] "{entry["text"][:50]}..." — {entry["author"]} ({entry["topic"]})'
            self.history_listbox.insert(tk.END, display)

    def add_quote(self):
        """Добавляет новую цитату с проверкой ввода"""
        text = self.new_text.get(1.0, tk.END).strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()

        # Проверка на пустые строки
        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
            return
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return
        if not topic:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return

        new_quote = {"text": text, "author": author, "topic": topic}
        self.quotes.append(new_quote)
        self.save_quotes(self.quotes)
        self.update_filters()

        # Очищаем поля ввода
        self.new_text.delete(1.0, tk.END)
        self.new_author.delete(0, tk.END)
        self.new_topic.delete(0, tk.END)

        messagebox.showinfo("Успех", "Цитата успешно добавлена!")

    def clear_history(self):
        """Очищает историю"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
