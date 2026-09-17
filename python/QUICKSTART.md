# 🎯 AI Agent — Полное руководство

## 📦 Что создано

### 1. Flash Arbitrage Engine (Python Full Stack)
**Папка:** `python/`

Полноценная система флеш-арбитража на Python:
- **app.py** — Flask веб-сервер с дашбордом
- **templates/index.html** — интерактивный UI
- **requirements.txt** — зависимости

**Функциональность:**
- Парсинг цен с 6 DEX
- Поиск арбитражных возможностей
- MEV защита через Flashbots
- Gas escalation для первой позиции
- Probability engine

**Запуск:**
```bash
cd python
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

---

### 2. AI Agent — Autonomous Computer Use
**Папка:** `python/`

Автономный AI-агент с computer use:
- **agent.py** — основной агент
- **advanced_tools.py** — 20+ расширенных инструментов
- **agent_examples.py** — примеры использования
- **agent_requirements.txt** — зависимости
- **AGENT_README.md** — подробная документация

**Функциональность:**
- ✅ Computer Use (мышь + клавиатура)
- ✅ Terminal Execution
- ✅ Voice Input (Whisper API)
- ✅ Loop Execution (цикл до успеха)
- ✅ OpenAI GPT-4
- ✅ 20+ инструментов

**Запуск:**
```bash
cd python
pip install -r agent_requirements.txt
export OPENAI_API_KEY="your-key"
python agent.py
```

---

## 🚀 Быстрый старт

### Flash Arbitrage
```bash
cd python
pip install -r requirements.txt
python app.py
```

### AI Agent
```bash
cd python
pip install -r agent_requirements.txt
export OPENAI_API_KEY="your-key"
python agent.py
```

### Self-Healing Agent
```bash
cd python
pip install openai
export OPENAI_API_KEY="your-key"

# Одна задача
python self_healing_agent.py "Создай Flask API"

# Daemon mode (фон)
python self_healing_agent.py --daemon
```

---

## 📊 Сравнение проектов

| Характеристика | Flash Arbitrage | AI Agent | Self-Healing Agent |
|----------------|-----------------|----------|-------------------|
| **Язык** | Python | Python | Python |
| **UI** | Flask + HTML | Terminal + Voice | Terminal |
| **Зависимости** | 5 пакетов | 12 пакетов | 1 пакет (openai) |
| **API** | OpenAI не нужен | OpenAI обязателен | OpenAI обязателен |
| **Сложность** | Средняя | Высокая | Средняя |
| **Стоимость** | $0 (тестнет) | ~$0.01-0.10/задача | ~$0.05-0.20/задача |
| **Безопасность** | Высокая | Требует осторожности | Высокая (workspace) |
| **Фон** | ❌ | ❌ | ✅ Daemon mode |
| **Self-healing** | ❌ | ❌ | ✅ Авто-исправление |

---

## 🎯 Примеры использования AI Agent

### 1. Автоматизация разработки
```
📝 Создай новый Python проект с виртуальным окружением, 
   установи Flask и создай базовое приложение
```

### 2. Анализ данных
```
📝 Создай CSV файл с данными, проанализируй его 
   и создай график
```

### 3. Системное администрирование
```
📝 Проверь использование диска, найди большие файлы 
   и покажи топ-10
```

### 4. Веб-скрапинг
```
📝 Открой сайт новостей, найди заголовки статей 
   и сохрани в файл
```

### 5. Голосовой ввод
```
📝 voice
🎤 Говорите: "Создай файл test.txt"
```

---

## 🛠️ Инструменты AI Agent

### Базовые (9 инструментов)
1. `terminal` — выполнение команд
2. `screenshot` — скриншоты
3. `keyboard` — клавиатура
4. `mouse` — мышь
5. `voice` — голосовой ввод
6. `web_search` — поиск
7. `file_read` — чтение файлов
8. `file_write` — запись файлов
9. `system_info` — информация о системе

### Расширенные (17 инструментов)
10. `open_url` — открытие URL
11. `execute_python` — выполнение Python
12. `execute_javascript` — выполнение JS
13. `analyze_csv` — анализ CSV
14. `create_chart` — создание графиков
15. `process_image` — обработка изображений
16. `ping` — ping хоста
17. `get_ip_info` — информация о IP
18. `clipboard_read` — чтение буфера
19. `clipboard_write` — запись в буфер
20. `list_windows` — список окон
21. `focus_window` — фокус окна
22. `notify` — уведомления
23. `list_directory` — список файлов
24. `search_files` — поиск файлов
25. `system_stats` — статистика системы
26. `http_request` — HTTP запросы

---

## 💡 Советы по использованию

### Flash Arbitrage
- Используйте Sepolia testnet для тестирования
- Мониторьте gas prices
- Настраивайте MIN_SPREAD_BPS под рынок
- Включайте MEV protection всегда

### AI Agent
- Начинайте с простых задач
- Используйте MAX_ITERATIONS для ограничения
- Мониторьте расходы OpenAI API
- Будьте осторожны с деструктивными командами
- Используйте в изолированной среде

---

## 🔐 Безопасность

### Flash Arbitrage
✅ Безопасно на testnet  
⚠️ Требует аудита для mainnet  
✅ MEV защита через Flashbots  

### AI Agent
⚠️ Может выполнять любые команды  
⚠️ Используйте в VM/Docker  
⚠️ Не запускайте с root  
✅ Логирует все действия  

---

## 📚 Документация

- **Flash Arbitrage:** `python/README.md`
- **AI Agent:** `python/AGENT_README.md`
- **Self-Healing Agent:** `python/SELF_HEALING_README.md`
- **Примеры AI Agent:** `python/agent_examples.py`
- **Примеры Self-Healing:** `python/self_healing_examples.py`

---

## 🎓 Обучение

Эти проекты отлично подходят для изучения:
- DeFi и флеш-кредиты
- MEV и Flashbots
- AI-агенты и computer use
- OpenAI API
- Автоматизация задач
- Python веб-разработка

---

## 🚀 Следующие шаги

### Для Flash Arbitrage
1. Подключить реальные DEX API
2. Добавить базу данных
3. Реализовать реальную торговлю
4. Добавить мониторинг и алерты
5. Оптимизировать для mainnet

### Для AI Agent
1. Добавить Claude Computer Use
2. Поддержка мультимодальных моделей
3. Параллельное выполнение
4. Система плагинов
5. Веб-интерфейс

---

## 📞 Поддержка

Если возникли вопросы:
1. Проверьте документацию в `python/README.md` и `python/AGENT_README.md`
2. Посмотрите примеры в `python/agent_examples.py`
3. Проверьте логи в `agent_log.jsonl`

---

**Готово! Три мощных Python проекта в одном.** 🎉

- **Flash Arbitrage** — для DeFi арбитража
- **AI Agent** — для автономной автоматизации с computer use
- **Self-Healing Agent** — для генерации кода с авто-исправлением

Все проекты полностью на Python, с простой установкой и подробной документацией.

---

## 🔄 Self-Healing AI Agent (Новое!)

Агент с автоматическим исправлением ошибок:

### Возможности
- ✅ Генерация файлов по описанию
- ✅ Автоматическое тестирование
- ✅ Self-healing (редактирование при ошибках)
- ✅ Фоновый режим (daemon)
- ✅ Очередь задач
- ✅ Полное логирование

### Как работает

```
1. Генерирует файлы (GPT-4)
2. Запускает для тестирования
3. Если ошибка:
   ├─ Анализирует проблему
   ├─ РЕДАКТИРУЕТ файл (не удаляет!)
   ├─ Повторный запуск
   └─ Цикл до успеха
4. Логирует все попытки
```

### Примеры задач

```bash
# Простой скрипт
python self_healing_agent.py "Создай калькулятор"

# Веб-приложение
python self_healing_agent.py "Создай Flask API с CRUD"

# Многофайловый проект
python self_healing_agent.py "Создай проект для заметок с модульной структурой"

# Daemon mode
python self_healing_agent.py --daemon
echo "Создай скрипт анализа" >> workspace/task_queue.txt
```

### Преимущества

✅ **Не удаляет файлы** — только редактирует  
✅ **Сохраняет историю** — все версии и исправления  
✅ **Фоновый режим** — работает как сервис  
✅ **Очередь задач** — пакетная обработка  
✅ **Полные логи** — анализ успешности  

### Структура

```
workspace/          # Сгенерированные файлы
logs/
├── tasks.jsonl    # Список задач
├── task_*.json    # Детали исправлений
└── daemon_state.json
```

**Документация:** `python/SELF_HEALING_README.md`
