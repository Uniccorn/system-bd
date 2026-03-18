import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import csv
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

# Проверка наличия дополнительных библиотек
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class DatabaseManager:
    """Класс для управления базой данных SQLite"""
    
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.current_table = None
        self.connect()
    
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к БД: {e}")
            return False
    
    def create_table(self, table_name, columns):
        """Создание таблицы"""
        try:
            columns_def = ", ".join([f"{col['name']} {col['type']}" for col in columns])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns_def})"
            self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать таблицу: {e}")
            return False
    
    def insert_record(self, table_name, data):
        """Вставка записи"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, tuple(data.values()))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить запись: {e}")
            return False
    
    def get_all_records(self, table_name):
        """Получение всех записей"""
        try:
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить записи: {e}")
            return []
    
    def get_table_columns(self, table_name):
        """Получение структуры таблицы"""
        try:
            query = f"PRAGMA table_info({table_name})"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить структуру: {e}")
            return []
    
    def update_record(self, table_name, record_id, data):
        """Обновление записи"""
        try:
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
            self.cursor.execute(query, tuple(list(data.values()) + [record_id]))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить запись: {e}")
            return False
    
    def delete_record(self, table_name, record_id):
        """Удаление записи"""
        try:
            query = f"DELETE FROM {table_name} WHERE id = ?"
            self.cursor.execute(query, (record_id,))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись: {e}")
            return False
    
    def search_records(self, table_name, column, value):
        """Поиск записей"""
        try:
            query = f"SELECT * FROM {table_name} WHERE {column} LIKE ?"
            self.cursor.execute(query, (f"%{value}%",))
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")
            return []
    
    def sort_records(self, table_name, column, order="ASC"):
        """Сортировка записей"""
        try:
            query = f"SELECT * FROM {table_name} ORDER BY {column} {order}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить сортировку: {e}")
            return []
    
    def get_tables(self):
        """Получение списка таблиц"""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список таблиц: {e}")
            return []
    
    def export_csv(self, table_name, file_path):
        """Экспорт в CSV"""
        try:
            records = self.get_all_records(table_name)
            columns = self.get_table_columns(table_name)
            col_names = [col[1] for col in columns]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(col_names)
                writer.writerows(records)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать в CSV: {e}")
            return False
    
    def import_csv(self, table_name, file_path, columns):
        """Импорт из CSV"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # Пропускаем заголовок
                
                for row in reader:
                    if len(row) == len(columns):
                        data = {col['name']: row[i] for i, col in enumerate(columns)}
                        self.insert_record(table_name, data)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось импортировать из CSV: {e}")
            return False
    
    def export_xml(self, table_name, file_path):
        """Экспорт в XML"""
        try:
            records = self.get_all_records(table_name)
            columns = self.get_table_columns(table_name)
            col_names = [col[1] for col in columns]
            
            root = ET.Element("database")
            table_elem = ET.SubElement(root, "table", name=table_name)
            
            for record in records:
                row_elem = ET.SubElement(table_elem, "row")
                for i, col_name in enumerate(col_names):
                    field_elem = ET.SubElement(row_elem, col_name)
                    field_elem.text = str(record[i])
            
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать в XML: {e}")
            return False
    
    def export_json(self, table_name, file_path):
        """Экспорт в JSON"""
        try:
            records = self.get_all_records(table_name)
            columns = self.get_table_columns(table_name)
            col_names = [col[1] for col in columns]
            
            data = []
            for record in records:
                row_dict = {col_names[i]: record[i] for i in range(len(col_names))}
                data.append(row_dict)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать в JSON: {e}")
            return False
    
    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()


class DatabaseApp:
    """Основной класс приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления базами данных v1.0")
        self.root.geometry("1400x900")
        
        self.db = DatabaseManager()
        self.current_table = None
        self.tree = None
        
        self._create_widgets()
        self._refresh_tables_list()
    
    def _create_widgets(self):
        """Создание элементов интерфейса"""
        
        # Верхняя панель инструментов
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Новая БД", command=self.new_database).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Открыть БД", command=self.open_database).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Создать таблицу", command=self.create_table).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        ttk.Button(toolbar, text="Добавить запись", command=self.add_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Редактировать", command=self.edit_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить запись", command=self.delete_record).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        ttk.Button(toolbar, text="Импорт CSV", command=self.import_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Экспорт CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Экспорт XML", command=self.export_xml).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Экспорт JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        ttk.Button(toolbar, text="Поиск", command=self.search_records).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Сортировка", command=self.sort_records).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        ttk.Button(toolbar, text="Визуализация", command=self.visualize_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Отчёт", command=self.generate_report).pack(side=tk.LEFT, padx=2)
        
        # Основная область
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - список таблиц
        tables_frame = ttk.LabelFrame(main_frame, text="Таблицы")
        tables_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.tables_listbox = tk.Listbox(tables_frame, width=25)
        self.tables_listbox.pack(fill=tk.BOTH, expand=True)
        self.tables_listbox.bind('<<ListboxSelect>>', self._on_table_select)
        
        ttk.Button(tables_frame, text="Обновить", command=self._refresh_tables_list).pack(fill=tk.X, pady=5)
        
        # Центральная панель - данные таблицы
        data_frame = ttk.LabelFrame(main_frame, text="Данные")
        data_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Treeview для отображения данных
        tree_frame = ttk.Frame(data_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Нижняя панель статуса
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Готов к работе", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        self.records_label = ttk.Label(status_frame, text="Записей: 0")
        self.records_label.pack(side=tk.RIGHT, padx=10)
    
    def _refresh_tables_list(self):
        """Обновление списка таблиц"""
        self.tables_listbox.delete(0, tk.END)
        tables = self.db.get_tables()
        for table in tables:
            if table != 'sqlite_sequence':  # Системная таблица
                self.tables_listbox.insert(tk.END, table)
        self.status_label.config(text="Список таблиц обновлён")
    
    def _on_table_select(self, event):
        """Выбор таблицы из списка"""
        selection = self.tables_listbox.curselection()
        if selection:
            self.current_table = self.tables_listbox.get(selection[0])
            self._load_table_data()
            self.status_label.config(text=f"Выбрана таблица: {self.current_table}")
    
    def _load_table_data(self):
        """Загрузка данных таблицы в Treeview"""
        if not self.current_table:
            return
        
        # Очистка Treeview
        self.tree.delete(*self.tree.get_children())
        
        # Получение структуры таблицы
        columns_info = self.db.get_table_columns(self.current_table)
        col_names = [col[1] for col in columns_info]
        
        # Настройка колонок
        self.tree["columns"] = col_names
        self.tree["show"] = "headings"
        
        for col in col_names:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Загрузка данных
        records = self.db.get_all_records(self.current_table)
        for record in records:
            self.tree.insert("", tk.END, values=record)
        
        self.records_label.config(text=f"Записей: {len(records)}")
    
    def new_database(self):
        """Создание новой базы данных"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Создать новую базу данных"
        )
        
        if file_path:
            self.db.close()
            self.db = DatabaseManager(file_path)
            self.status_label.config(text=f"Новая БД создана: {os.path.basename(file_path)}")
            self._refresh_tables_list()
    
    def open_database(self):
        """Открытие существующей базы данных"""
        file_path = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Открыть базу данных"
        )
        
        if file_path:
            self.db.close()
            self.db = DatabaseManager(file_path)
            self.status_label.config(text=f"БД открыта: {os.path.basename(file_path)}")
            self._refresh_tables_list()
    
    def create_table(self):
        """Создание новой таблицы"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Создать таблицу")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Имя таблицы:").pack(pady=5)
        table_name_entry = ttk.Entry(dialog, width=40)
        table_name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Колонки (формат: имя:тип, имя:тип):").pack(pady=5)
        columns_entry = ttk.Entry(dialog, width=40)
        columns_entry.pack(pady=5)
        columns_entry.insert(0, "name:TEXT, age:INTEGER, email:TEXT")
        
        def create():
            try:
                table_name = table_name_entry.get().strip()
                columns_str = columns_entry.get().strip()
                
                if not table_name:
                    raise ValueError("Введите имя таблицы")
                
                columns = []
                for col in columns_str.split(","):
                    name, dtype = col.strip().split(":")
                    columns.append({"name": name.strip(), "type": dtype.strip().upper()})
                
                if self.db.create_table(table_name, columns):
                    self._refresh_tables_list()
                    self.status_label.config(text=f"Таблица '{table_name}' создана")
                    dialog.destroy()
                else:
                    raise ValueError("Ошибка создания таблицы")
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(dialog, text="Создать", command=create).pack(pady=10)
    
    def add_record(self):
        """Добавление записи"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        columns_info = self.db.get_table_columns(self.current_table)
        col_names = [col[1] for col in columns_info if col[1] != 'id']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить запись")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        entries = {}
        for col_name in col_names:
            ttk.Label(dialog, text=col_name).pack(pady=2)
            entry = ttk.Entry(dialog, width=40)
            entry.pack(pady=2)
            entries[col_name] = entry
        
        def add():
            try:
                data = {col: entry.get() for col, entry in entries.items()}
                if self.db.insert_record(self.current_table, data):
                    self._load_table_data()
                    self.status_label.config(text="Запись добавлена")
                    dialog.destroy()
                else:
                    raise ValueError("Ошибка добавления записи")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(dialog, text="Добавить", command=add).pack(pady=10)
    
    def edit_record(self):
        """Редактирование записи"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования")
            return
        
        item = self.tree.item(selected[0])
        values = item['values']
        record_id = values[0]
        
        columns_info = self.db.get_table_columns(self.current_table)
        col_names = [col[1] for col in columns_info if col[1] != 'id']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать запись")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        entries = {}
        for i, col_name in enumerate(col_names):
            ttk.Label(dialog, text=col_name).pack(pady=2)
            entry = ttk.Entry(dialog, width=40)
            entry.pack(pady=2)
            entry.insert(0, values[i + 1] if i + 1 < len(values) else "")
            entries[col_name] = entry
        
        def save():
            try:
                data = {col: entry.get() for col, entry in entries.items()}
                if self.db.update_record(self.current_table, record_id, data):
                    self._load_table_data()
                    self.status_label.config(text="Запись обновлена")
                    dialog.destroy()
                else:
                    raise ValueError("Ошибка обновления записи")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
    
    def delete_record(self):
        """Удаление записи"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            item = self.tree.item(selected[0])
            record_id = item['values'][0]
            if self.db.delete_record(self.current_table, record_id):
                self._load_table_data()
                self.status_label.config(text="Запись удалена")
    
    def import_csv(self):
        """Импорт из CSV"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Импорт из CSV"
        )
        
        if file_path:
            columns_info = self.db.get_table_columns(self.current_table)
            columns = [{"name": col[1], "type": col[2]} for col in columns_info if col[1] != 'id']
            
            if self.db.import_csv(self.current_table, file_path, columns):
                self._load_table_data()
                self.status_label.config(text="Данные импортированы из CSV")
    
    def export_csv(self):
        """Экспорт в CSV"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Экспорт в CSV"
        )
        
        if file_path:
            if self.db.export_csv(self.current_table, file_path):
                self.status_label.config(text="Данные экспортированы в CSV")
    
    def export_xml(self):
        """Экспорт в XML"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")],
            title="Экспорт в XML"
        )
        
        if file_path:
            if self.db.export_xml(self.current_table, file_path):
                self.status_label.config(text="Данные экспортированы в XML")
    
    def export_json(self):
        """Экспорт в JSON"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Экспорт в JSON"
        )
        
        if file_path:
            if self.db.export_json(self.current_table, file_path):
                self.status_label.config(text="Данные экспортированы в JSON")
    
    def search_records(self):
        """Поиск записей"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        columns_info = self.db.get_table_columns(self.current_table)
        col_names = [col[1] for col in columns_info if col[1] != 'id']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Поиск")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Колонка:").pack(pady=5)
        column_var = tk.StringVar(value=col_names[0] if col_names else "")
        column_combo = ttk.Combobox(dialog, textvariable=column_var, values=col_names, width=35)
        column_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Значение:").pack(pady=5)
        value_entry = ttk.Entry(dialog, width=40)
        value_entry.pack(pady=5)
        
        def search():
            column = column_var.get()
            value = value_entry.get()
            if column and value:
                records = self.db.search_records(self.current_table, column, value)
                self._display_search_results(records)
                self.status_label.config(text=f"Найдено записей: {len(records)}")
                dialog.destroy()
            else:
                messagebox.showwarning("Внимание", "Заполните все поля")
        
        ttk.Button(dialog, text="Найти", command=search).pack(pady=10)
    
    def _display_search_results(self, records):
        """Отображение результатов поиска"""
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", tk.END, values=record)
        self.records_label.config(text=f"Записей: {len(records)}")
    
    def sort_records(self):
        """Сортировка записей"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        columns_info = self.db.get_table_columns(self.current_table)
        col_names = [col[1] for col in columns_info if col[1] != 'id']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Сортировка")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Колонка:").pack(pady=5)
        column_var = tk.StringVar(value=col_names[0] if col_names else "")
        column_combo = ttk.Combobox(dialog, textvariable=column_var, values=col_names, width=30)
        column_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Порядок:").pack(pady=5)
        order_var = tk.StringVar(value="ASC")
        ttk.Radiobutton(dialog, text="По возрастанию", variable=order_var, value="ASC").pack()
        ttk.Radiobutton(dialog, text="По убыванию", variable=order_var, value="DESC").pack()
        
        def sort():
            column = column_var.get()
            order = order_var.get()
            if column:
                records = self.db.sort_records(self.current_table, column, order)
                self._display_search_results(records)
                self.status_label.config(text=f"Сортировка по {column} {order}")
                dialog.destroy()
            else:
                messagebox.showwarning("Внимание", "Выберите колонку")
        
        ttk.Button(dialog, text="Сортировать", command=sort).pack(pady=10)
    
    def visualize_data(self):
        """Визуализация данных"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showinfo("Информация", "Библиотека matplotlib не установлена.\nУстановите: pip install matplotlib")
            return
        
        records = self.db.get_all_records(self.current_table)
        columns_info = self.db.get_table_columns(self.current_table)
        col_names = [col[1] for col in columns_info]
        
        # Простая визуализация - количество записей
        plt.figure(figsize=(8, 6))
        plt.bar(range(len(records)), [1] * len(records))
        plt.xlabel('Запись')
        plt.ylabel('Значение')
        plt.title(f'Данные таблицы: {self.current_table}')
        plt.tight_layout()
        plt.show()
        
        self.status_label.config(text="Визуализация выполнена")
    
    def generate_report(self):
        """Генерация отчёта"""
        if not self.current_table:
            messagebox.showwarning("Внимание", "Выберите таблицу")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("HTML Files", "*.html"), ("All Files", "*.*")],
            title="Сохранить отчёт"
        )
        
        if file_path:
            try:
                records = self.db.get_all_records(self.current_table)
                columns_info = self.db.get_table_columns(self.current_table)
                col_names = [col[1] for col in columns_info]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"=== ОТЧЁТ ПО ТАБЛИЦЕ: {self.current_table} ===\n\n")
                    f.write(f"Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Всего записей: {len(records)}\n\n")
                    f.write("Структура таблицы:\n")
                    for col in columns_info:
                        f.write(f"  - {col[1]} ({col[2]})\n")
                    f.write("\nДанные:\n")
                    f.write("-" * 80 + "\n")
                    f.write(" | ".join(col_names) + "\n")
                    f.write("-" * 80 + "\n")
                    for record in records:
                        f.write(" | ".join(str(v) for v in record) + "\n")
                    f.write("-" * 80 + "\n")
                
                self.status_label.config(text=f"Отчёт сохранён: {os.path.basename(file_path)}")
                messagebox.showinfo("Успех", "Отчёт успешно создан!")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать отчёт: {e}")
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        self.db.close()
        self.root.destroy()


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = DatabaseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()