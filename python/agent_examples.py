"""
AI Agent Examples
=================
Примеры использования AI-агента для различных задач.
"""

from agent import AIAgent

def example_1_simple_task():
    """Пример 1: Простая задача с файлами."""
    agent = AIAgent()
    
    task = """
    Создай файл hello.py с кодом:
    print('Hello from AI Agent!')
    
    Затем выполни этот файл и покажи результат.
    """
    
    result = agent.run_task(task)
    print(f"\n✅ Задача выполнена: {result.completed}")
    print(f"📝 Ответ: {result.final_answer}")


def example_2_system_info():
    """Пример 2: Сбор информации о системе."""
    agent = AIAgent()
    
    task = """
    Собери информацию о системе:
    1. Операционная система
    2. Использование CPU и памяти
    3. Свободное место на диске
    4. Список запущенных процессов (топ-5)
    
    Сохрани результат в файл system_info.txt
    """
    
    result = agent.run_task(task)
    print(f"\n✅ Информация собрана: {result.completed}")


def example_3_web_search():
    """Пример 3: Поиск в интернете."""
    agent = AIAgent()
    
    task = """
    Найди в интернете информацию о Python 3.12:
    1. Основные новые функции
    2. Улучшения производительности
    3. Дата выхода
    
    Сохрани найденную информацию в файл python_312_info.txt
    """
    
    result = agent.run_task(task)
    print(f"\n✅ Поиск выполнен: {result.completed}")


def example_4_code_generation():
    """Пример 4: Генерация и выполнение кода."""
    agent = AIAgent()
    
    task = """
    Напиши Python функцию, которая:
    1. Принимает список чисел
    2. Возвращает сумму, среднее и максимум
    
    Создай файл calculator.py с этой функцией.
    Добавь тесты для функции.
    Выполни файл и покажи результаты тестов.
    """
    
    result = agent.run_task(task)
    print(f"\n✅ Код создан и протестирован: {result.completed}")


def example_5_file_organization():
    """Пример 5: Организация файлов."""
    agent = AIAgent()
    
    task = """
    Найди в текущей директории все файлы:
    1. Python файлы (.py)
    2. Текстовые файлы (.txt)
    3. Markdown файлы (.md)
    
    Создай отчёт file_report.txt со списком всех найденных файлов,
    сгруппированных по типу.
    """
    
    result = agent.run_task(task)
    print(f"\n✅ Файлы организованы: {result.completed}")


def example_6_data_analysis():
    """Пример 6: Анализ данных."""
    agent = AIAgent()
    
    task = """
    Создай CSV файл data.csv с тестовыми данными:
    - 10 строк
    - Колонки: name, age, city, salary
    
    Затем прочитай этот файл и покажи:
    1. Количество записей
    2. Средний возраст
    3. Среднюю зарплату
    
    Сохрани результаты в analysis_report.txt
    """
    
    result = agent.run_task(task)
    print(f"\n✅ Данные проанализированы: {result.completed}")


def example_7_automation():
    """Пример 7: Автоматизация рабочего процесса."""
    agent = AIAgent()
    
    task = """
    Автоматизируй создание нового Python проекта:
    1. Создай директорию my_project
    2. Создай виртуальное окружение venv
    3. Создай файл requirements.txt с flask
    4. Создай файл app.py с базовым Flask приложением
    5. Создай README.md с описанием проекта
    6. Создай .gitignore файл
    """
    
    result = agent.run_task(task)
    print(f"\n✅ Проект создан: {result.completed}")


def example_8_interactive():
    """Пример 8: Интерактивный режим."""
    agent = AIAgent()
    
    print("\n" + "="*60)
    print("🤖 AI Agent — Interactive Mode")
    print("="*60)
    print("\nПопробуйте следующие задачи:")
    print("• 'Сделай скриншот экрана'")
    print("• 'Покажи информацию о системе'")
    print("• 'Создай файл test.txt с текстом Hello'")
    print("• 'Найди все .py файлы в текущей директории'")
    print("\nДля выхода введите 'quit'\n")
    
    agent.interactive_mode()


if __name__ == "__main__":
    import sys
    
    examples = {
        "1": ("Простая задача с файлами", example_1_simple_task),
        "2": ("Сбор информации о системе", example_2_system_info),
        "3": ("Поиск в интернете", example_3_web_search),
        "4": ("Генерация и выполнение кода", example_4_code_generation),
        "5": ("Организация файлов", example_5_file_organization),
        "6": ("Анализ данных", example_6_data_analysis),
        "7": ("Автоматизация рабочего процесса", example_7_automation),
        "8": ("Интерактивный режим", example_8_interactive),
    }
    
    print("\n" + "="*60)
    print("🤖 AI Agent — Examples")
    print("="*60)
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
