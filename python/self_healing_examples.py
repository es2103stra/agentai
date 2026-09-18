"""
Self-Healing Agent Examples
============================
Примеры использования агента с автоматическим исправлением ошибок.
"""

from self_healing_agent import SelfHealingAgent

def example_1_simple_script():
    """Пример 1: Создание простого скрипта."""
    agent = SelfHealingAgent()
    
    task = """
    Создай Python скрипт calculator.py который:
    1. Принимает два числа от пользователя
    2. Выполняет сложение, вычитание, умножение, деление
    3. Обрабатывает деление на ноль
    4. Показывает результаты
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Задача выполнена: {result.completed}")
    print(f"📊 Итераций: {result.total_iterations}")


def example_2_flask_api():
    """Пример 2: Создание Flask API."""
    agent = SelfHealingAgent()
    
    task = """
    Создай Flask REST API с CRUD операциями для задач (todos):
    1. GET /todos — список всех задач
    2. POST /todos — создать задачу
    3. GET /todos/<id> — получить задачу
    4. PUT /todos/<id> — обновить задачу
    5. DELETE /todos/<id> — удалить задачу
    
    Используй in-memory хранилище (список).
    Добавь обработку ошибок.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ API создано: {result.completed}")


def example_3_data_processing():
    """Пример 3: Обработка данных."""
    agent = SelfHealingAgent()
    
    task = """
    Создай скрипт data_processor.py который:
    1. Генерирует тестовые данные (CSV файл с 100 строками)
    2. Читает CSV
    3. Анализирует данные (среднее, медиана, стандартное отклонение)
    4. Создаёт отчёт в текстовом файле
    5. Строит простой график (если matplotlib доступен)
    
    Обработай все возможные ошибки.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Обработка данных: {result.completed}")


def example_4_web_scraper():
    """Пример 4: Веб-скрапер."""
    agent = SelfHealingAgent()
    
    task = """
    Создай веб-скрапер scraper.py который:
    1. Загружает HTML страницу (используй requests)
    2. Парсит заголовки (используй BeautifulSoup или regex)
    3. Сохраняет результаты в JSON
    4. Обрабатывает ошибки сети
    5. Добавляет retry логику
    
    Тестируй на https://example.com
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Скрапер создан: {result.completed}")


def example_5_game():
    """Пример 5: Простая игра."""
    agent = SelfHealingAgent()
    
    task = """
    Создай консольную игру guess_number.py:
    1. Компьютер загадывает число от 1 до 100
    2. Пользователь угадывает
    3. Программа подсказывает "больше" или "меньше"
    4. Считает количество попыток
    5. Показывает статистику
    
    Добавь обработку некорректного ввода.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Игра создана: {result.completed}")


def example_6_file_manager():
    """Пример 6: Файловый менеджер."""
    agent = SelfHealingAgent()
    
    task = """
    Создай файловый менеджер file_manager.py с функциями:
    1. list_files(path) — список файлов
    2. create_file(path, content) — создать файл
    3. read_file(path) — прочитать файл
    4. delete_file(path) — удалить файл
    5. search_files(pattern) — поиск файлов
    
    Добавь обработку всех ошибок (permissions, not found, etc).
    Создай тесты для каждой функции.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Файловый менеджер: {result.completed}")


def example_7_async_scraper():
    """Пример 7: Асинхронный скрапер."""
    agent = SelfHealingAgent()
    
    task = """
    Создай асинхронный веб-скрапер async_scraper.py:
    1. Использует aiohttp и asyncio
    2. Загружает 5 URL параллельно
    3. Извлекает заголовки страниц
    4. Сохраняет результаты в JSON
    5. Добавляет таймауты и retry
    
    Тестируй на популярных сайтах.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Асинхронный скрапер: {result.completed}")


def example_8_database_app():
    """Пример 8: Приложение с базой данных."""
    agent = SelfHealingAgent()
    
    task = """
    Создай приложение с SQLite базой данных db_app.py:
    1. Создаёт таблицу users (id, name, email, created_at)
    2. Функции: add_user, get_user, update_user, delete_user, list_users
    3. Валидация email
    4. Обработка ошибок БД
    5. Пример использования
    
    Используй только стандартную библиотеку sqlite3.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Приложение с БД: {result.completed}")


def example_9_cli_tool():
    """Пример 9: CLI инструмент."""
    agent = SelfHealingAgent()
    
    task = """
    Создай CLI инструмент word_counter.py:
    1. Принимает путь к файлу как аргумент
    2. Считает слова, строки, символы
    3. Показывает топ-10 частых слов
    4. Поддерживает флаги: --words, --lines, --chars, --top
    5. Красивый вывод с форматированием
    
    Используй argparse для парсинга аргументов.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ CLI инструмент: {result.completed}")


def example_10_multi_file_project():
    """Пример 10: Многофайловый проект."""
    agent = SelfHealingAgent()
    
    task = """
    Создай проект для управления заметками:
    
    Структура:
    notes_app/
    ├── main.py (точка входа)
    ├── models.py (модели данных)
    ├── storage.py (работа с файлами)
    ├── utils.py (утилиты)
    └── requirements.txt
    
    Функциональность:
    1. Создание заметок
    2. Поиск по заметкам
    3. Теги
    4. Экспорт в JSON/Markdown
    5. Статистика
    
    Все модули должны работать вместе.
    """
    
    result = agent.execute_task(task)
    print(f"\n✅ Проект создан: {result.completed}")


if __name__ == "__main__":
    import sys
    
    examples = {
        "1": ("Простой скрипт", example_1_simple_script),
        "2": ("Flask API", example_2_flask_api),
        "3": ("Обработка данных", example_3_data_processing),
        "4": ("Веб-скрапер", example_4_web_scraper),
        "5": ("Игра", example_5_game),
        "6": ("Файловый менеджер", example_6_file_manager),
        "7": ("Асинхронный скрапер", example_7_async_scraper),
        "8": ("Приложение с БД", example_8_database_app),
        "9": ("CLI инструмент", example_9_cli_tool),
        "10": ("Многофайловый проект", example_10_multi_file_project),
    }
    
    print("\n" + "="*70)
    print("🤖 Self-Healing Agent — Examples")
    print("="*70)
    print("\nВыберите пример:")
    
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\n  0. Выход")
    
    choice = input("\nВаш выбор: ").strip()
    
    if choice == "0":
        print("👋 До свидания!")
        sys.exit(0)
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n🚀 Запускаю: {name}\n")
        func()
    else:
        print("❌ Неверный выбор")
