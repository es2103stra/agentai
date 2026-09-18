# 📄 Document Agent — Автоматизация отчётов

Модуль для анализа DOCX документов и автоматической генерации новых документов на основе шаблонов с использованием AI.

## 🎯 Возможности

### 1. Анализ документов
- Извлечение структуры (заголовки, секции)
- Анализ стилей и форматирования
- Подсчёт таблиц и изображений
- Извлечение плейсхолдеров `{{placeholder}}`
- Экспорт структуры в JSON

### 2. Генерация документов
- Заполнение плейсхолдеров данными
- Сохранение всех стилей и форматирования
- Поддержка таблиц и изображений
- Генерация контента с помощью GPT-4

### 3. Автоматическая генерация отчётов
- Создание отчётов по описанию задачи
- Пакетная генерация нескольких отчётов
- Интеграция с GPT-4 для генерации контента
- Сохранение структуры шаблона

## 🚀 Быстрый старт

### Установка

```bash
cd python
pip install python-docx openai
export OPENAI_API_KEY="your-api-key-here"
```

### Использование

#### Режим 1: Анализ документа

```bash
python document_agent.py analyze report.docx
```

Вывод:
```
📄 Анализирую: report.docx
✅ Структура извлечена:
   Заголовок: Квартальный отчёт
   Секций: 5
   Таблиц: 2
   Изображений: 1
   Плейсхолдеров: 8

📝 Плейсхолдеры:
   - {{quarter}}
   - {{year}}
   - {{revenue}}
   ...

✅ Структура сохранена: report_structure.json
```

#### Режим 2: Генерация из данных

```bash
# Создайте файл data.json
{
  "quarter": "Q4",
  "year": "2024",
  "revenue": "10,000,000",
  "profit": "2,500,000"
}

# Сгенерируйте документ
python document_agent.py generate template.docx --data data.json
```

#### Режим 3: Автогенерация с AI

```bash
python document_agent.py auto-report template.docx "Создай квартальный отчёт за Q4 2024 с анализом продаж"
```

## 📝 Примеры использования

### Пример 1: Создание шаблона

```python
from docx import Document

# Создаём шаблон с плейсхолдерами
doc = Document()
doc.add_heading('Отчёт по проекту {{project_name}}', 0)
doc.add_heading('Описание', 1)
doc.add_paragraph('{{project_description}}')
doc.add_heading('Результаты', 1)
doc.add_paragraph('Срок: {{deadline}}')
doc.add_paragraph('Бюджет: {{budget}} рублей')
doc.save('project_template.docx')
```

### Пример 2: Генерация из данных

```python
from document_agent import DocumentGenerator

# Данные для заполнения
data = {
    "project_name": "Автоматизация отчётности",
    "project_description": "Разработка системы автоматической генерации отчётов.",
    "deadline": "31 декабря 2024",
    "budget": "500,000"
}

# Генерируем документ
generator = DocumentGenerator()
generator.load_template('project_template.docx')
result = generator.generate_from_data(data, 'project_report.docx')

print(f"✅ Документ создан: {result.path}")
```

### Пример 3: Автогенерация с AI

```python
from document_agent import AutoReportGenerator

auto_gen = AutoReportGenerator()
result = auto_gen.generate_report(
    template_path='report_template.docx',
    task='Создай маркетинговый анализ для запуска нового продукта',
    output_path='marketing_report.docx'
)

print(f"✅ Отчёт создан: {result.path}")
```

### Пример 4: Пакетная генерация

```python
from document_agent import AutoReportGenerator

# Задачи для генерации
tasks = [
    "Отчёт за неделю 1: Запуск функционала",
    "Отчёт за неделю 2: Исправление багов",
    "Отчёт за неделю 3: Оптимизация"
]

# Генерируем пакетно
auto_gen = AutoReportGenerator()
results = auto_gen.batch_generate('weekly_template.docx', tasks)

for result in results:
    print(f"✅ Создан: {result.path}")
```

## 📊 Структура документа

### Анализ структуры

```python
from document_agent import DocumentAnalyzer

analyzer = DocumentAnalyzer()
structure = analyzer.analyze('report.docx')

print(f"Заголовок: {structure.title}")
print(f"Секций: {len(structure.sections)}")
print(f"Таблиц: {structure.tables_count}")
print(f"Изображений: {structure.images_count}")
print(f"Стилей: {structure.styles_used}")
```

### Экспорт в JSON

```python
# Экспортируем структуру
structure_dict = analyzer.export_structure('structure.json')

# Или автоматически
analyzer.export_structure('report_structure.json')
```

### Извлечение плейсхолдеров

```python
# Получаем список плейсхолдеров
placeholders = analyzer.extract_placeholders()
print(f"Плейсхолдеры: {placeholders}")
# ['{{quarter}}', '{{year}}', '{{revenue}}', ...]
```

### Извлечение таблиц

```python
# Извлекаем все таблицы
tables = analyzer.extract_tables()

for i, table in enumerate(tables):
    print(f"\nТаблица {i+1}:")
    for row in table:
        print(f"  {row}")
```

## 🎨 Работа со стилями

### Анализ стилей

```python
analyzer = DocumentAnalyzer()
structure = analyzer.analyze('styled_doc.docx')

print("Используемые стили:")
for style in structure.styles_used:
    print(f"  - {style}")
```

### Сохранение форматирования

При генерации документа все стили из шаблона сохраняются:
- Шрифты и размеры
- Цвета текста
- Выравнивание
- Жирный/курсив/подчёркивание
- Отступы и интервалы

## 🤖 Интеграция с GPT-4

### Генерация контента

```python
from document_agent import DocumentGenerator

generator = DocumentGenerator()
generator.load_template('template.docx')

# GPT-4 генерирует контент для плейсхолдеров
result = generator.generate_with_ai(
    task='Создай финансовый отчёт за Q4 2024',
    output_path='financial_report.docx'
)
```

### Как это работает

1. Анализирует структуру шаблона
2. Извлекает плейсхолдеры
3. Отправляет запрос в GPT-4 с контекстом
4. Получает JSON с заполненными данными
5. Генерирует документ

### Пример запроса к GPT-4

```
Ты — эксперт по созданию документов.

Задача: Создай маркетинговый анализ

Структура шаблона:
{
  "title": "Маркетинговый анализ",
  "sections": [
    {"type": "heading", "text": "Обзор рынка"},
    {"type": "paragraph", "text": "{{market_overview}}"}
  ]
}

Плейсхолдеры: market_overview, competitors_analysis, recommendations

Сгенерируй содержимое для каждого плейсхолдера.
```

## 📁 Структура проекта

```
python/
├── document_agent.py           # Основной модуль
├── document_examples.py        # Примеры использования
├── DOCUMENT_AGENT_README.md    # Эта документация
├── generated_docs/             # Сгенерированные документы
│   ├── report_20240115_143022.docx
│   └── ...
└── *.docx                      # Шаблоны и документы
```

## 💡 Практические сценарии

### Сценарий 1: Еженедельные отчёты

```python
# Создаём шаблон
from docx import Document

doc = Document()
doc.add_heading('Еженедельный отчёт', 0)
doc.add_heading('Достижения', 1)
doc.add_paragraph('{{achievements}}')
doc.add_heading('Проблемы', 1)
doc.add_paragraph('{{issues}}')
doc.add_heading('Планы', 1)
doc.add_paragraph('{{plans}}')
doc.save('weekly_template.docx')

# Генерируем отчёты на месяц
from document_agent import AutoReportGenerator

tasks = [
    "Отчёт за неделю 1: Запуск нового функционала",
    "Отчёт за неделю 2: Исправление критических багов",
    "Отчёт за неделю 3: Оптимизация производительности",
    "Отчёт за неделю 4: Подготовка к релизу"
]

auto_gen = AutoReportGenerator()
results = auto_gen.batch_generate('weekly_template.docx', tasks)
```

### Сценарий 2: Финансовые отчёты

```python
# Шаблон с таблицами
doc = Document()
doc.add_heading('Финансовый отчёт {{company_name}}', 0)

# Таблица с плейсхолдерами
table = doc.add_table(rows=4, cols=3)
table.style = 'Table Grid'

# Заголовки
table.rows[0].cells[0].text = 'Показатель'
table.rows[0].cells[1].text = 'Q3 2024'
table.rows[0].cells[2].text = 'Q4 2024'

# Данные
table.rows[1].cells[0].text = 'Выручка'
table.rows[1].cells[1].text = '{{q3_revenue}}'
table.rows[1].cells[2].text = '{{q4_revenue}}'

# ... остальные строки

doc.save('financial_template.docx')

# Генерируем отчёт
data = {
    "company_name": "ООО Пример",
    "q3_revenue": "5,000,000",
    "q4_revenue": "6,500,000",
    "q3_expenses": "3,500,000",
    "q4_expenses": "4,000,000",
    "q3_profit": "1,500,000",
    "q4_profit": "2,500,000"
}

generator = DocumentGenerator()
generator.load_template('financial_template.docx')
result = generator.generate_from_data(data, 'financial_report.docx')
```

### Сценарий 3: Персонализированные письма

```python
# Шаблон письма
doc = Document()
doc.add_paragraph('Уважаемый {{client_name}}!')
doc.add_paragraph('')
doc.add_paragraph('Благодарим вас за сотрудничество в {{year}} году.')
doc.add_paragraph('')
doc.add_paragraph('{{personal_message}}')
doc.add_paragraph('')
doc.add_paragraph('С уважением,')
doc.add_paragraph('{{sender_name}}')
doc.save('letter_template.docx')

# Генерируем письма для клиентов
clients = [
    {
        "client_name": "Иван Иванов",
        "year": "2024",
        "personal_message": "Мы ценим ваш вклад в проект X.",
        "sender_name": "Петр Петров"
    },
    {
        "client_name": "Мария Сидорова",
        "year": "2024",
        "personal_message": "Спасибо за успешное завершение проекта Y.",
        "sender_name": "Петр Петров"
    }
]

generator = DocumentGenerator()
generator.load_template('letter_template.docx')

for i, client in enumerate(clients, 1):
    result = generator.generate_from_data(client, f'letter_{i}.docx')
    print(f"✅ Письмо {i} создано")
```

### Сценарий 4: Отчёты с AI

```python
from document_agent import AutoReportGenerator

# Шаблон с плейсхолдерами
# (создан заранее)

# Генерируем отчёт с помощью AI
auto_gen = AutoReportGenerator()

result = auto_gen.generate_report(
    template_path='analysis_template.docx',
    task='Создай детальный анализ рынка e-commerce в России за 2024 год с прогнозом на 2025',
    output_path='ecommerce_analysis_2024.docx'
)

print(f"✅ Отчёт создан: {result.path}")
print(f"   Слов: {result.word_count}")
```

## 🔧 Расширенные возможности

### Кастомные стили

```python
from docx import Document
from docx.shared import Pt, RGBColor

doc = Document()

# Заголовок с кастомным стилем
title = doc.add_heading('{{report_title}}', 0)
title.runs[0].font.size = Pt(24)
title.runs[0].font.color.rgb = RGBColor(0, 51, 102)

# Выделенный текст
highlight = doc.add_paragraph()
run = highlight.add_run('{{important_text}}')
run.bold = True
run.font.color.rgb = RGBColor(204, 0, 0)

doc.save('custom_styled_template.docx')
```

### Множественные плейсхолдеры

```python
# Один параграф с несколькими плейсхолдерами
doc.add_paragraph(
    'Отчёт за {{quarter}} квартал {{year}} года. '
    'Выручка составила {{revenue}} рублей, '
    'что на {{growth}}% больше предыдущего периода.'
)
```

### Условные плейсхолдеры

```python
# Можно реализовать логику в данных
data = {
    "show_section": "yes",  # или "no"
    "section_content": "..."
}

# В шаблоне:
# {{show_section}} -> "yes" или "no"
# Обработка в коде
```

## 📊 Логирование

Все операции логируются:

```python
result = generator.generate_from_data(data, 'output.docx')

print(f"Путь: {result.path}")
print(f"Шаблон: {result.template_used}")
print(f"Плейсхолдеров заполнено: {result.placeholders_filled}")
print(f"Время генерации: {result.generation_time:.2f}s")
print(f"Количество слов: {result.word_count}")
```

## ⚠️ Ограничения

### Формат файлов
- Поддерживается только DOCX (не DOC)
- Изображения сохраняются, но не модифицируются
- Сложные макеты могут потребовать ручной доработки

### Плейсхолдеры
- Формат: `{{placeholder_name}}`
- Имя: только буквы, цифры и подчёркивания
- Без пробелов и специальных символов

### GPT-4
- Требуется API ключ
- Стоимость: ~$0.01-0.05 за документ
- Время генерации: 5-15 секунд

## 💡 Советы

### 1. Создавайте чёткие шаблоны

```python
# Хорошо:
doc.add_heading('{{report_title}}', 0)
doc.add_paragraph('{{executive_summary}}')

# Плохо:
doc.add_paragraph('Текст {{placeholder}} ещё текст')
```

### 2. Используйте осмысленные имена

```python
# Хорошо:
# {{quarter_revenue}}, {{annual_growth}}, {{client_name}}

# Плохо:
# {{data1}}, {{text}}, {{value}}
```

### 3. Тестируйте шаблоны

```python
# Сначала анализируем
analyzer = DocumentAnalyzer()
structure = analyzer.analyze('template.docx')

# Проверяем плейсхолдеры
placeholders = analyzer.extract_placeholders()
print(f"Найдено плейсхолдеров: {len(placeholders)}")

# Затем генерируем
```

### 4. Сохраняйте структуру

```python
# Экспортируем структуру для документации
analyzer.export_structure('template_structure.json')

# Можно использовать для валидации
with open('template_structure.json', 'r') as f:
    structure = json.load(f)
    print(f"Секций: {len(structure['sections'])}")
```

## 📚 Ресурсы

- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [DOCX Format Specification](https://www.ecma-international.org/publications-and-standards/standards/ecma-376/)

## 🤝 Вклад

Идеи для улучшения:
- [ ] Поддержка DOC (старый формат)
- [ ] Извлечение и вставка изображений
- [ ] Поддержка формул и уравнений
- [ ] Интеграция с Google Docs
- [ ] Веб-интерфейс для создания шаблонов
- [ ] Система версионирования документов

## 📝 Лицензия

MIT License

---

**Запуск:**
```bash
cd python
pip install python-docx openai
export OPENAI_API_KEY="your-key"

# Анализ
python document_agent.py analyze report.docx

# Генерация из данных
python document_agent.py generate template.docx --data data.json

# Автогенерация с AI
python document_agent.py auto-report template.docx "Задача"
```

**Готово! Автоматизация отчётов на Python.** 🚀
