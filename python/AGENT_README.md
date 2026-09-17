# 🤖 AI Agent — Autonomous Computer Use

Автономный AI-агент с возможностями computer use, голосовым вводом и циклическим выполнением задач.

## 🚀 Возможности

### Основные функции
- ✅ **Computer Use** — управление мышью и клавиатурой
- ✅ **Terminal Execution** — выполнение команд в терминале
- ✅ **Voice Input** — распознавание речи через Whisper API
- ✅ **Loop Execution** — цикл пока задача не выполнена правильно
- ✅ **OpenAI GPT-4** — принятие решений
- ✅ **Screenshot Analysis** — анализ скриншотов экрана
- ✅ **Web Search** — поиск в интернете
- ✅ **File Operations** — чтение/запись файлов
- ✅ **System Info** — информация о системе

### Расширенные инструменты
- 🌐 **Browser Automation** — открытие URL, скриншоты браузера
- 💻 **Code Execution** — выполнение Python/JavaScript кода
- 📊 **Data Analysis** — анализ CSV, создание графиков
- 🖼️ **Image Processing** — обработка изображений
- 🌐 **Network Tools** — ping, IP info
- 📋 **Clipboard** — операции с буфером обмена
- 🪟 **Window Management** — управление окнами
- 🔔 **Notifications** — системные уведомления
- 📁 **File System** — поиск и список файлов
- 📈 **System Monitoring** — мониторинг CPU, RAM, disk

## 📦 Установка

### 1. Установите зависимости

```bash
cd python
pip install -r agent_requirements.txt
```

### 2. Настройте OpenAI API ключ

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Или создайте файл `.env`:
```bash
OPENAI_API_KEY=your-api-key-here
```

### 3. Дополнительные зависимости (опционально)

**Для голосового ввода:**
```bash
# macOS
brew install portaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio

# Windows
# PyAudio устанавливается автоматически через pip
```

**Для browser automation:**
```bash
pip install selenium playwright
playwright install
```

## 🎯 Использование

### Интерактивный режим

```bash
python agent.py
```

Примеры задач:
```
📝 Задача: Открой браузер и найди погоду в Москве
📝 Задача: Создай файл test.txt с содержимым "Hello World"
📝 Задача: Сделай скриншот экрана и сохрани как screenshot.png
📝 Задача: Найди все Python файлы в текущей директории
📝 Задача: voice  (голосовой ввод)
```

### Режим одной задачи

```bash
python agent.py "Создай файл hello.py с кодом print('Hello World')"
```

### Примеры использования

#### 1. Автоматизация браузера
```
📝 Задача: Открой https://google.com и найди "Python tutorial"
```

#### 2. Работа с файлами
```
📝 Задача: Создай директорию project, перейди в неё и создай файл README.md
```

#### 3. Анализ данных
```
📝 Задача: Прочитай файл data.csv и покажи первые 5 строк
```

#### 4. Системные команды
```
📝 Задача: Покажи информацию о системе и использование диска
```

#### 5. Голосовой ввод
```
📝 Задача: voice
🎤 Говорите: "Создай файл test.txt"
```

## 🧠 Как это работает

### Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent Loop                         │
├─────────────────────────────────────────────────────────┤
│  1. Получает задачу (текст/голос)                       │
│  2. GPT-4 анализирует и выбирает действие               │
│  3. Выполняет действие через tools                      │
│  4. Проверяет результат                                 │
│  5. Повторяет пока задача не выполнена                  │
└─────────────────────────────────────────────────────────┘
```

### Цикл выполнения

```python
while not task_completed and iteration < MAX_ITERATIONS:
    # 1. Думаем
    decision = gpt4.think(task, history)
    
    # 2. Проверяем завершение
    if decision.task_completed:
        break
    
    # 3. Выполняем действие
    result = execute_action(decision.action)
    
    # 4. Добавляем в историю
    history.append(result)
    
    # 5. Повторяем
    iteration += 1
```

### Пример рассуждений GPT-4

```json
{
  "thought": "Нужно создать файл. Использую инструмент file_write.",
  "action": {
    "tool": "file_write",
    "parameters": {
      "filepath": "test.txt",
      "content": "Hello World"
    }
  },
  "task_completed": false,
  "final_answer": null
}
```

## 🛠️ Доступные инструменты

### Базовые инструменты

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `terminal` | Выполняет команду | `command: str` |
| `screenshot` | Делает скриншот | — |
| `keyboard` | Управление клавиатурой | `type_text`, `hotkey`, `press_key` |
| `mouse` | Управление мышью | `click`, `move_to`, `scroll` |
| `voice` | Распознавание речи | `timeout: int` |
| `web_search` | Поиск в интернете | `query: str` |
| `file_read` | Чтение файла | `filepath: str` |
| `file_write` | Запись в файл | `filepath: str, content: str` |
| `system_info` | Информация о системе | — |

### Расширенные инструменты

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `open_url` | Открывает URL в браузере | `url: str` |
| `execute_python` | Выполняет Python код | `code: str` |
| `execute_javascript` | Выполняет JS код | `code: str` |
| `analyze_csv` | Анализирует CSV | `filepath: str` |
| `create_chart` | Создаёт график | `data: Dict, chart_type: str` |
| `process_image` | Обрабатывает изображение | `filepath: str, operation: str` |
| `ping` | Ping хоста | `host: str, count: int` |
| `get_ip_info` | Информация о IP | — |
| `clipboard_read` | Читает буфер обмена | — |
| `clipboard_write` | Пишет в буфер | `text: str` |
| `list_windows` | Список окон | — |
| `focus_window` | Фокусирует окно | `title: str` |
| `notify` | Показывает уведомление | `title: str, message: str` |
| `list_directory` | Список файлов | `path: str` |
| `search_files` | Поиск файлов | `pattern: str, path: str` |
| `system_stats` | Статистика системы | — |
| `http_request` | HTTP запрос | `url: str, method: str, data: Dict` |

## 📊 Логирование

Все действия логируются в `agent_log.jsonl`:

```json
{
  "timestamp": 1705312345.678,
  "task": "Создай файл test.txt",
  "completed": true,
  "iterations": 2,
  "actions_count": 2,
  "final_answer": "Файл test.txt успешно создан"
}
```

Скриншоты сохраняются в папку `screenshots/`.

## 🔐 Безопасность

⚠️ **Важно:** Агент может выполнять любые команды на вашем компьютере!

### Рекомендации

1. **Используйте в изолированной среде** (VM, Docker)
2. **Не запускайте с root/sudo правами**
3. **Ограничьте MAX_ITERATIONS** (по умолчанию 50)
4. **Мониторьте действия агента**
5. **Не давайте доступ к чувствительным данным**

### Ограничения

```python
# В agent.py можно добавить whitelist команд:
ALLOWED_COMMANDS = ['ls', 'pwd', 'echo', 'cat', 'python']

# Или blacklist:
BLOCKED_COMMANDS = ['rm -rf', 'sudo', 'shutdown']
```

## 🎨 Примеры сценариев

### 1. Автоматизация разработки

```
📝 Задача: Создай новый Python проект с виртуальным окружением, установи Flask и создай базовое приложение
```

### 2. Анализ данных

```
📝 Задача: Скачай CSV файл с данными, проанализируй его и создай график
```

### 3. Системное администрирование

```
📝 Задача: Проверь использование диска, найди большие файлы и покажи топ-10
```

### 4. Веб-скрапинг

```
📝 Задача: Открой сайт новостей, найди заголовки статей и сохрани в файл
```

### 5. Тестирование

```
📝 Задача: Запусти тесты в проекте, найди упавшие тесты и покажи ошибки
```

## 🚧 Ограничения

- **Точность GPT-4** — может ошибаться в сложных задачах
- **Скорость** — каждая итерация занимает 2-5 секунд
- **Стоимость** — OpenAI API платный (~$0.01-0.10 за задачу)
- **Безопасность** — требует осторожности при использовании
- **Зависимости** — некоторые инструменты требуют дополнительных библиотек

## 💡 Советы

### Оптимизация затрат

```python
# Используйте более дешёвую модель для простых задач
MODEL = "gpt-3.5-turbo"  # вместо gpt-4

# Ограничьте количество итераций
MAX_ITERATIONS = 20  # вместо 50
```

### Улучшение точности

```python
# Добавляйте контекст в системный промпт
self.system_prompt += """
Ты работаешь на macOS.
Предпочитай Python команды.
Всегда проверяй результаты.
"""
```

### Расширение функциональности

```python
# Добавьте свои инструменты в advanced_tools.py
@staticmethod
def my_custom_tool(param: str) -> Dict[str, Any]:
    # Ваша логика
    return {"success": True, "result": "..."}
```

## 📚 Ресурсы

- [OpenAI API Docs](https://platform.openai.com/docs/)
- [PyAutoGUI Docs](https://pyautogui.readthedocs.io/)
- [SpeechRecognition Docs](https://pypi.org/project/SpeechRecognition/)
- [Whisper API](https://platform.openai.com/docs/guides/speech-to-text)

## 🤝 Вклад

Идеи для улучшения:
- [ ] Интеграция с Claude Computer Use
- [ ] Поддержка мультимодальных моделей (GPT-4 Vision)
- [ ] Параллельное выполнение действий
- [ ] Система плагинов для инструментов
- [ ] Веб-интерфейс для мониторинга
- [ ] База знаний для повторного использования решений

## ⚠️ Дисклеймер

Этот агент предназначен для **образовательных целей** и **автоматизации рутинных задач**.

Используйте на свой страх и риск. Автор не несёт ответственности за любые повреждения или потери данных.

---

**Запуск:**
```bash
cd python
pip install -r agent_requirements.txt
export OPENAI_API_KEY="your-key"
python agent.py
```

**Готово! Автономный AI-агент с computer use.** 🚀
