# -*- coding: utf-8 -*-
"""Система управления базами данных с готовой тестовой БД (Лабораторная работа №6)"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import io
import random

# ============================================
# ЧАСТЬ 1: ТЕСТОВАЯ БАЗА ДАННЫХ
# ============================================

def create_sample_database():
    """
    Создание готовой тестовой базы данных
    """
    
    # Данные для 15 товаров
    data = {
        'ID': [f'PR00{i}' for i in range(1, 16)],
        'Название': [
            'Ноутбук', 'Смартфон', 'Планшет', 'Наушники', 'Мышь',
            'Клавиатура', 'Монитор', 'Флешка 32GB', 'Внешний диск', 'Принтер',
            'Колонки', 'Веб-камера', 'Микрофон', 'Коврик для мыши', 'Чехол для ноутбука'
        ],
        'Категория': [
            'Электроника', 'Электроника', 'Электроника', 'Аксессуары', 'Аксессуары',
            'Аксессуары', 'Электроника', 'Накопители', 'Накопители', 'Периферия',
            'Аксессуары', 'Периферия', 'Периферия', 'Аксессуары', 'Аксессуары'
        ],
        'Цена': [
            45000, 25000, 18000, 3500, 1200,
            2500, 15000, 800, 4500, 8500,
            3200, 2100, 2800, 500, 1500
        ],
        'Количество': [
            15, 23, 8, 45, 60,
            32, 12, 100, 25, 7,
            18, 14, 9, 80, 30
        ],
        'Рейтинг': [
            4.8, 4.9, 4.5, 4.3, 4.6,
            4.4, 4.7, 4.2, 4.5, 4.1,
            4.3, 4.0, 4.4, 4.8, 4.2
        ],
        'Страна': [
            'Китай', 'Китай', 'Китай', 'Китай', 'Китай',
            'Китай', 'Корея', 'Китай', 'США', 'Китай',
            'Китай', 'Китай', 'Китай', 'Китай', 'Китай'
        ],
        'Год': [
            2024, 2024, 2023, 2024, 2024,
            2023, 2024, 2024, 2023, 2022,
            2024, 2023, 2023, 2024, 2024
        ],
        'Беспроводной': [
            True, True, True, True, True,
            True, False, False, False, False,
            True, False, True, False, False
        ],
        'Вес': [
            1800, 180, 500, 250, 100,
            800, 3500, 20, 200, 5000,
            1200, 150, 350, 200, 600
        ]
    }
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Добавляем вычисляемый столбец
    df['Общая стоимость'] = df['Цена'] * df['Количество']
    
    return df, "Товары на складе"


# ============================================
# ЧАСТЬ 2: СИСТЕМА УПРАВЛЕНИЯ БАЗАМИ ДАННЫХ
# ============================================

class DatabaseManager:
    """
    Класс для управления базами данных (таблицами данных)
    """
    
    def __init__(self, initial_data=None, initial_name="Новая БД"):
        self.data = initial_data
        self.current_table_name = initial_name
        self.supported_formats = {
            'csv': 'CSV (разделители запятые)',
            'txt': 'TXT (текстовый файл)',
            'xlsx': 'Excel',
            'json': 'JSON'
        }
        
    def create_database(self):
        """Создание новой базы данных"""
        print("\n" + "="*50)
        print("СОЗДАНИЕ НОВОЙ БАЗЫ ДАННЫХ")
        print("="*50)
        
        table_name = input("Введите название базы данных: ").strip()
        if table_name:
            self.current_table_name = table_name
        
        try:
            n_rows = int(input("Введите количество строк: "))
            n_cols = int(input("Введите количество столбцов: "))
            
            columns = []
            for i in range(n_cols):
                col_name = input(f"Введите название столбца {i+1}: ").strip()
                if not col_name:
                    col_name = f"Столбец_{i+1}"
                columns.append(col_name)
            
            data = {col: [''] * n_rows for col in columns}
            self.data = pd.DataFrame(data)
            
            print(f"\n✅ База данных '{self.current_table_name}' успешно создана!")
            print(f"Размер: {n_rows} строк × {n_cols} столбцов")
            self.view_data()
            
        except ValueError:
            print("❌ Ошибка: введите корректные числовые значения")
            self.data = None
    
    def view_data(self):
        """Просмотр данных"""
        if self.data is None:
            print("❌ Нет данных для просмотра")
            return
        
        print("\n" + "="*50)
        print(f"📊 ТАБЛИЦА: {self.current_table_name}")
        print("="*50)
        
        print(f"Размер: {self.data.shape[0]} строк × {self.data.shape[1]} столбцов")
        print("\n📋 Столбцы:")
        for i, col in enumerate(self.data.columns, 1):
            dtype = self.data[col].dtype
            print(f"  {i}. {col} (тип: {dtype})")
        
        print("\n📋 Первые 5 строк данных:")
        print("-" * 80)
        print(self.data.head().to_string(index=False))
        
        print("\n📊 Основная статистика:")
        print("-" * 80)
        print(self.data.describe(include='all').to_string())
    
    def add_record(self):
        """Добавление новой записи"""
        if self.data is None:
            print("❌ Нет базы данных. Сначала создайте или загрузите данные.")
            return
        
        print("\n" + "="*50)
        print("➕ ДОБАВЛЕНИЕ НОВОЙ ЗАПИСИ")
        print("="*50)
        
        new_record = {}
        for col in self.data.columns:
            value = input(f"Введите значение для '{col}': ").strip()
            new_record[col] = value
        
        self.data = pd.concat([self.data, pd.DataFrame([new_record])], ignore_index=True)
        print("✅ Новая запись добавлена!")
    
    def update_record(self):
        """Обновление записи"""
        if self.data is None or len(self.data) == 0:
            print("❌ Нет данных для обновления")
            return
        
        self.view_data()
        
        try:
            index = int(input(f"\nВведите номер строки для обновления (0-{len(self.data)-1}): "))
            
            if 0 <= index < len(self.data):
                print(f"\nТекущие значения строки {index}:")
                for col in self.data.columns:
                    print(f"  {col}: {self.data.loc[index, col]}")
                
                for col in self.data.columns:
                    new_value = input(f"Новое значение для '{col}' (Enter - оставить без изменений): ").strip()
                    if new_value:
                        self.data.loc[index, col] = new_value
                
                print("✅ Запись обновлена!")
            else:
                print("❌ Неверный индекс")
                
        except ValueError:
            print("❌ Введите корректный номер строки")
    
    def delete_record(self):
        """Удаление записи"""
        if self.data is None or len(self.data) == 0:
            print("❌ Нет данных для удаления")
            return
        
        self.view_data()
        
        try:
            index = int(input(f"\nВведите номер строки для удаления (0-{len(self.data)-1}): "))
            
            if 0 <= index < len(self.data):
                self.data = self.data.drop(index).reset_index(drop=True)
                print("✅ Запись удалена!")
            else:
                print("❌ Неверный индекс")
                
        except ValueError:
            print("❌ Введите корректный номер строки")
    
    def sort_data(self):
        """Сортировка данных"""
        if self.data is None or len(self.data) == 0:
            print("❌ Нет данных для сортировки")
            return
        
        print("\nДоступные столбцы для сортировки:")
        for i, col in enumerate(self.data.columns, 1):
            print(f"  {i}. {col}")
        
        try:
            col_choice = int(input("\nВыберите номер столбца: ")) - 1
            if 0 <= col_choice < len(self.data.columns):
                col_name = self.data.columns[col_choice]
                ascending = input("Сортировать по возрастанию? (да/нет): ").strip().lower() == 'да'
                
                self.data = self.data.sort_values(by=col_name, ascending=ascending).reset_index(drop=True)
                print(f"✅ Данные отсортированы по столбцу '{col_name}'")
                self.view_data()
            else:
                print("❌ Неверный номер столбца")
                
        except ValueError:
            print("❌ Введите корректный номер")
    
    def filter_data(self):
        """Фильтрация данных"""
        if self.data is None or len(self.data) == 0:
            print("❌ Нет данных для фильтрации")
            return
        
        print("\nДоступные столбцы для фильтрации:")
        for i, col in enumerate(self.data.columns, 1):
            print(f"  {i}. {col}")
        
        try:
            col_choice = int(input("\nВыберите номер столбца: ")) - 1
            if 0 <= col_choice < len(self.data.columns):
                col_name = self.data.columns[col_choice]
                value = input(f"Введите значение для фильтрации в столбце '{col_name}': ").strip()
                
                filtered_data = self.data[self.data[col_name].astype(str).str.contains(value, case=False, na=False)]
                
                if len(filtered_data) > 0:
                    print(f"\n✅ Найдено {len(filtered_data)} записей:")
                    print(filtered_data.to_string(index=False))
                    
                    if input("\nСохранить отфильтрованные данные как новую таблицу? (да/нет): ").strip().lower() == 'да':
                        self.data = filtered_data.reset_index(drop=True)
                        print("✅ Отфильтрованные данные сохранены как основная таблица")
                else:
                    print("❌ Записей не найдено")
            else:
                print("❌ Неверный номер столбца")
                
        except ValueError:
            print("❌ Введите корректный номер")
    
    def visualize_data(self):
        """Визуализация данных"""
        if self.data is None or len(self.data) == 0:
            print("❌ Нет данных для визуализации")
            return
        
        print("\n" + "="*50)
        print("📊 ВИЗУАЛИЗАЦИЯ ДАННЫХ")
        print("="*50)
        
        print("\nТипы диаграмм:")
        print("  1. Гистограмма (для числовых данных)")
        print("  2. Столбчатая диаграмма")
        print("  3. Круговая диаграмма")
        print("  4. Точечная диаграмма")
        print("  5. Тепловая карта корреляции")
        
        try:
            chart_type = int(input("\nВыберите тип диаграммы (1-5): "))
            
            plt.figure(figsize=(12, 8))
            
            if chart_type == 1:
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    for i, col in enumerate(numeric_cols[:4], 1):
                        plt.subplot(2, 2, i)
                        self.data[col].hist(bins=10, edgecolor='black', color='skyblue')
                        plt.title(f'Гистограмма: {col}')
                        plt.xlabel(col)
                        plt.ylabel('Частота')
                else:
                    print("❌ Нет числовых столбцов для гистограммы")
                    return
                    
            elif chart_type == 2:
                col = input("Введите название столбца для анализа: ").strip()
                if col in self.data.columns:
                    self.data[col].value_counts().plot(kind='bar', color='coral')
                    plt.title(f'Столбчатая диаграмма: {col}')
                    plt.xlabel(col)
                    plt.ylabel('Количество')
                    plt.xticks(rotation=45)
                else:
                    print("❌ Столбец не найден")
                    return
                    
            elif chart_type == 3:
                col = input("Введите название столбца для анализа: ").strip()
                if col in self.data.columns:
                    self.data[col].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['gold', 'lightcoral', 'lightskyblue'])
                    plt.title(f'Круговая диаграмма: {col}')
                    plt.ylabel('')
                else:
                    print("❌ Столбец не найден")
                    return
                    
            elif chart_type == 4:
                numeric_cols = list(self.data.select_dtypes(include=[np.number]).columns)
                if len(numeric_cols) >= 2:
                    print(f"Числовые столбцы: {numeric_cols}")
                    x_col = input("Введите столбец для оси X: ").strip()
                    y_col = input("Введите столбец для оси Y: ").strip()
                    if x_col in numeric_cols and y_col in numeric_cols:
                        plt.scatter(self.data[x_col], self.data[y_col], alpha=0.6, color='green')
                        plt.xlabel(x_col)
                        plt.ylabel(y_col)
                        plt.title(f'Точечная диаграмма: {x_col} vs {y_col}')
                    else:
                        print("❌ Указаны нечисловые столбцы")
                        return
                else:
                    print("❌ Нужно минимум 2 числовых столбца")
                    return
                    
            elif chart_type == 5:
                numeric_data = self.data.select_dtypes(include=[np.number])
                if len(numeric_data.columns) > 1:
                    corr_matrix = numeric_data.corr()
                    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
                    plt.title('Тепловая карта корреляции')
                else:
                    print("❌ Нужно минимум 2 числовых столбца для корреляции")
                    return
            else:
                print("❌ Неверный тип диаграммы")
                return
            
            plt.tight_layout()
            plt.show()
            
        except ValueError:
            print("❌ Введите корректное значение")
        except Exception as e:
            print(f"❌ Ошибка при создании диаграммы: {e}")
    
    def generate_report(self):
        """Генерация отчета"""
        if self.data is None:
            print("❌ Нет данных для отчета")
            return
        
        print("\n" + "="*50)
        print("📝 ГЕНЕРАЦИЯ ОТЧЕТА")
        print("="*50)
        
        report = []
        report.append("="*60)
        report.append(f"ОТЧЕТ ПО БАЗЕ ДАННЫХ: {self.current_table_name}")
        report.append(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*60)
        
        # Общая информация
        report.append(f"\n1. ОБЩАЯ ИНФОРМАЦИЯ")
        report.append(f"   - Количество записей: {len(self.data)}")
        report.append(f"   - Количество полей: {len(self.data.columns)}")
        report.append(f"   - Поля: {', '.join(self.data.columns)}")
        
        # Статистика по числовым полям
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            report.append(f"\n2. СТАТИСТИКА ПО ЧИСЛОВЫМ ПОЛЯМ")
            for col in numeric_cols:
                report.append(f"\n   Поле: {col}")
                report.append(f"     - Минимум: {self.data[col].min()}")
                report.append(f"     - Максимум: {self.data[col].max()}")
                report.append(f"     - Среднее: {self.data[col].mean():.2f}")
                report.append(f"     - Медиана: {self.data[col].median()}")
        
        # Статистика по текстовым полям
        text_cols = self.data.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            report.append(f"\n3. СТАТИСТИКА ПО ТЕКСТОВЫМ ПОЛЯМ")
            for col in text_cols:
                report.append(f"\n   Поле: {col}")
                report.append(f"     - Уникальных значений: {self.data[col].nunique()}")
                if len(self.data[col].dropna()) > 0:
                    report.append(f"     - Самое частое значение: {self.data[col].mode().iloc[0] if len(self.data[col].mode()) > 0 else 'Нет'}")
        
        # Первые 10 записей
        report.append(f"\n4. ПЕРВЫЕ 10 ЗАПИСЕЙ")
        report.append("-" * 60)
        for i, row in self.data.head(10).iterrows():
            report.append(f"   {i}: " + " | ".join([f"{col}: {val}" for col, val in row.items()]))
        
        report.append("\n" + "="*60)
        report.append("КОНЕЦ ОТЧЕТА")
        report.append("="*60)
        
        # Вывод отчета
        print("\n".join(report))
        
        # Сохранение отчета
        save_choice = input("\nСохранить отчет в файл? (да/нет): ").strip().lower()
        if save_choice == 'да':
            filename = f"report_{self.current_table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(report))
            print(f"✅ Отчет сохранен в файл {filename}")
            print("📥 Скачайте файл из панели файлов Colab")
    
    def save_to_csv(self):
        """Сохранение в CSV файл"""
        if self.data is None:
            print("❌ Нет данных для сохранения")
            return
        
        filename = f"{self.current_table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.data.to_csv(filename, index=False)
        print(f"✅ Данные сохранены в файл {filename}")
        print("📥 Скачайте файл из панели файлов Colab")


# ============================================
# ЧАСТЬ 3: ГЛАВНАЯ ПРОГРАММА
# ============================================

def main():
    """Главная функция программы"""
    
    print("="*60)
    print("🏢 СИСТЕМА УПРАВЛЕНИЯ БАЗАМИ ДАННЫХ")
    print("Лабораторная работа №6")
    print("="*60)
    
    # Создаем тестовую базу данных
    print("\n📦 Загрузка тестовой базы данных...")
    sample_data, sample_name = create_sample_database()
    
    # Инициализируем менеджер с тестовыми данными
    db = DatabaseManager(sample_data, sample_name)
    
    print("\n" + "="*60)
    print("✅ ТЕСТОВАЯ БАЗА ДАННЫХ ЗАГРУЖЕНА!")
    print(f"📊 Название: {sample_name}")
    print(f"📊 Размер: {sample_data.shape[0]} строк × {sample_data.shape[1]} столбцов")
    print("="*60)
    
    while True:
        print("\n" + "="*50)
        print("📌 ГЛАВНОЕ МЕНЮ")
        print("="*50)
        print("1.  Создать новую базу данных")
        print("2.  Просмотр текущей базы данных")
        print("3.  Добавить запись")
        print("4.  Обновить запись")
        print("5.  Удалить запись")
        print("6.  Сортировка данных")
        print("7.  Фильтрация данных")
        print("8.  Визуализация данных")
        print("9.  Сгенерировать отчет")
        print("10. Сохранить в CSV")
        print("0.  Выход")
        print("-" * 50)
        print(f"📁 Текущая БД: {db.current_table_name}")
        if db.data is not None:
            print(f"📊 Записей: {len(db.data)}")
        print("="*50)
        
        choice = input("\n🔹 Выберите действие (0-10): ").strip()
        
        if choice == '1':
            db.create_database()
        elif choice == '2':
            db.view_data()
        elif choice == '3':
            db.add_record()
        elif choice == '4':
            db.update_record()
        elif choice == '5':
            db.delete_record()
        elif choice == '6':
            db.sort_data()
        elif choice == '7':
            db.filter_data()
        elif choice == '8':
            db.visualize_data()
        elif choice == '9':
            db.generate_report()
        elif choice == '10':
            db.save_to_csv()
        elif choice == '0':
            print("\n👋 Программа завершена. До свидания!")
            break
        else:
            print("❌ Неверный выбор. Пожалуйста, выберите действие от 0 до 10.")

# Запуск программы
if __name__ == "__main__":
    main()
