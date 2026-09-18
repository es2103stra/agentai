# 🔄 Integrated AI Workflow

Интеграция всех 4 проектов в единый рабочий процесс для максимальной автоматизации.

## 🎯 Что это?

Объединяет все модули в сложные сценарии:

1. **AI Agent** — принимает и анализирует задачу
2. **Self-Healing Agent** — генерирует и тестирует код
3. **Document Agent** — создаёт отчёты о результатах
4. **Flash Arbitrage** — (опционально) выполняет торговые стратегии

## 🚀 Быстрый старт

```bash
cd python
pip install openai python-docx
export OPENAI_API_KEY="your-key"

python integrated_workflow.py
```

## 📊 Workflow 1: Code + Report

**Сценарий:** Генерация кода + автоматический отчёт

```
1. Вы описываете задачу
2. Self-Healing Agent генерирует код
3. Код тестируется и исправляется
4. Document Agent создаёт отчёт о результатах
```

### Пример

```bash
python integrated_workflow.py
# Выберите: 1
# Задача: Создай Flask API с CRUD операциями для задач
```

**Результат:**
```
integrated_workspace/
├── code/
│   ├── app.py
│   └── requirements.txt
└── reports/
    └── report_20240115_143022.docx
```

## 🔍 Workflow 2: AI Analysis + Report

**Сценарий:** AI исследование + аналитический отчёт

```
1. Вы указываете тему
2. AI Agent исследует тему
3. Собирает информацию
4. Document Agent создаёт аналитический отчёт
```

### Пример

```bash
python integrated_workflow.py
# Выберите: 2
# Тема: Анализ рынка e-commerce в России 2024
```

**Результат:**
```
integrated_workspace/
└── reports/
    ├── analysis_results.json
    └── analysis_20240115_143022.docx
```

## 📦 Workflow 3: Batch Reports

**Сценарий:** Пакетная генерация отчётов

```
1. Вы вводите список задач
2. Для каждой задачи генерируется код
3. Для каждого результата создаётся отчёт
4. Создаётся сводный отчёт
```

### Пример

```bash
python integrated_workflow.py
# Выберите: 3
# Задача 1: Создай калькулятор
# Задача 2: Создай файловый менеджер
# Задача 3: Создай игру угадай число
# (пустая строка)
```

**Результат:**
```
integrated_workspace/
├── code/
│   ├── calculator/
│   ├── file_manager/
│   └── guess_game/
└── reports/
    ├── report_1_20240115_143022.docx
    ├── report_2_20240115_143025.docx
    ├── report_3_20240115_143028.docx
    └── summary_20240115_143030.docx
```

## 💡 Практические сценарии

### Сценарий 1: Автоматизация разработки

```python
from integrated_workflow import IntegratedWorkflow

workflow = IntegratedWorkflow()

# Генерируем код + документацию
result = workflow.workflow_1_code_and_report(
    "Создай REST API для управления пользователями с аутентификацией"
)

print(f"✅ Код создан в: {result['code_result'].files_created}")
print(f"📄 Отчёт: {result['report_path']}")
```

### Сценарий 2: Исследовательский отчёт

```python
workflow = IntegratedWorkflow()

# AI исследует тему и создаёт отчёт
result = workflow.workflow_2_ai_analysis_and_report(
    "Тренды в области искусственного интеллекта 2024-2025"
)

print(f"📊 Отчёт создан: {result['report_path']}")
```

### Сценарий 3: Пакетная автоматизация

```python
workflow = IntegratedWorkflow()

# Генерируем 5 утилит + отчёты
tasks = [
    "Создай утилиту для конвертации CSV в JSON",
    "Создай скрипт для бэкапа файлов",
    "Создай инструмент для анализа логов",
    "Создай генератор случайных данных",
    "Создай валидатор email адресов"
]

result = workflow.workflow_3_batch_reports(tasks)

print(f"✅ Создано {len(result['results'])} проектов")
print(f"📊 Сводный отчёт: {result['summary_path']}")
```

## 📁 Структура результатов

```
integrated_workspace/
├── code/                       # Сгенерированный код
│   ├── app.py
│   ├── requirements.txt
│   └── ...
├── reports/                    # Отчёты
│   ├── report_20240115_143022.docx
│   ├── analysis_20240115_143025.docx
│   └── summary_20240115_143030.docx
├── code_report_template.docx   # Шаблоны
├── analysis_template.docx
└── summary_template.docx
```

## 📊 Содержание отчётов

### Отчёт о генерации кода

```
Отчёт о генерации кода
======================

Описание задачи:
  Создай Flask API с CRUD операциями

Результаты:
  Дата генерации: 2024-01-15 14:30:22
  Статус: ✅ Успешно
  Файлов создано: 3
  Итераций: 2
  Попыток исправления: 1

Созданные файлы:
  - app.py
  - requirements.txt
  - README.md

Резюме:
  Код успешно сгенерирован за 2 итерации.
  Создано 3 файла. Все файлы прошли тестирование.
```

### Аналитический отчёт

```
Аналитический отчёт
===================

Тема исследования:
  Тренды в области AI 2024-2025

Дата анализа:
  2024-01-15 14:30:25

Ключевые findings:
  1. Рост использования LLM
  2. Развитие мультимодальных моделей
  3. Улучшение эффективности

Выводы:
  AI продолжает быстро развиваться...

Рекомендации:
  1. Инвестировать в LLM технологии
  2. Развивать компетенции в области AI
```

## 🔧 Кастомизация

### Изменение шаблонов

```python
from docx import Document

# Создаём свой шаблон
doc = Document()
doc.add_heading('Мой отчёт', 0)
doc.add_paragraph('{{custom_field}}')
doc.save('my_template.docx')

# Используем в workflow
workflow = IntegratedWorkflow()
workflow.doc_generator.load_template('my_template.docx')
result = workflow.doc_generator.generate_from_data(
    {"custom_field": "Мои данные"},
    'my_report.docx'
)
```

### Добавление новых workflow

```python
class IntegratedWorkflow:
    def workflow_4_custom(self, task: str):
        """Ваш кастомный workflow."""
        # Ваша логика
        pass
```

## 📈 Статистика

### Время выполнения

- **Workflow 1 (Code + Report):** 2-5 минут
- **Workflow 2 (AI Analysis):** 3-7 минут
- **Workflow 3 (Batch):** 5-15 минут (зависит от количества задач)

### Стоимость OpenAI API

- **Workflow 1:** ~$0.10-0.30
- **Workflow 2:** ~$0.05-0.15
- **Workflow 3:** ~$0.10-0.30 × количество задач

### Успешность

- **Генерация кода:** 80-95% (зависит от сложности)
- **Генерация отчётов:** 99%
- **AI анализ:** 70-90% (зависит от темы)

## 💡 Советы

### 1. Начинайте с простых задач

```python
# Хорошо:
"Создай калькулятор с базовыми операциями"

# Слишком сложно:
"Создай распределённую систему с микросервисами"
```

### 2. Используйте пакетную генерацию для рутины

```python
tasks = [
    "Создай скрипт для задачи 1",
    "Создай скрипт для задачи 2",
    # ...
]
workflow.workflow_3_batch_reports(tasks)
```

### 3. Сохраняйте шаблоны

```python
# Создайте шаблоны один раз
workflow._create_report_template()
workflow._create_analysis_template()

# Используйте повторно
workflow.doc_generator.load_template('saved_template.docx')
```

### 4. Мониторьте результаты

```python
result = workflow.workflow_1_code_and_report(task)

# Проверяем успех
if result["success"]:
    print(f"✅ Код: {len(result['code_result'].files_created)} файлов")
    print(f"📄 Отчёт: {result['report_path']}")
else:
    print(f"❌ Ошибка: {result.get('error')}")
```

## ⚠️ Ограничения

### Время
- Каждая итерация занимает 30-60 секунд
- Сложные задачи могут потребовать 10+ итераций
- Пакетная генерация — последовательная

### Стоимость
- OpenAI API: ~$0.05-0.30 за задачу
- Зависит от сложности и количества итераций

### Точность
- Не все задачи решаются с первого раза
- Может потребоваться ручная доработка
- AI анализ не всегда полный

## 🔐 Безопасность

✅ Код генерируется в изолированной директории  
✅ Отчёты сохраняются локально  
✅ Нет доступа к внешним системам (кроме OpenAI API)  
⚠️ Проверяйте сгенерированный код перед запуском  
⚠️ Не запускайте с root правами  

## 📚 Ресурсы

- [Self-Healing Agent](SELF_HEALING_README.md)
- [Document Agent](DOCUMENT_AGENT_README.md)
- [AI Agent](AGENT_README.md)
- [Flash Arbitrage](README.md)

## 🤝 Вклад

Идеи для улучшения:
- [ ] Параллельная обработка задач
- [ ] Интеграция с базами данных
- [ ] Веб-интерфейс для управления workflow
- [ ] Система уведомлений (email, Telegram)
- [ ] Экспорт в другие форматы (PDF, HTML)
- [ ] Интеграция с CI/CD системами

## 📝 Лицензия

MIT License

---

**Запуск:**
```bash
cd python
pip install openai python-docx
export OPENAI_API_KEY="your-key"
python integrated_workflow.py
```

**Готово! Интегрированный AI workflow.** 🚀
