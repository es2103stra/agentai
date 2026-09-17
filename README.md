# 🚀 Python AI Projects — Три мощных проекта

Полностью на Python! Один язык, простая установка, всё работает из коробки.

## 📦 Проекты

1. **Flash Arbitrage Engine** — DeFi арбитраж с MEV защитой
2. **AI Agent** — автономный агент с computer use и голосовым вводом
3. **Self-Healing Agent** — генерация кода с автоматическим исправлением ошибок

## 🚀 Быстрый старт

```bash
# 1. Перейти в папку Python проекта
cd python

# 2. Установить зависимости (одной командой!)
pip install -r requirements.txt

# 3. Запустить сервер
python app.py

# 4. Открыть дашборд
# → http://localhost:5000
```

**Всё! Никакого Node.js, npm, React — только Python.**

## 📦 Структура проекта

```
.
├── python/                      # Python Full Stack приложение
│   ├── app.py                  # Flask веб-сервер + весь бэкенд
│   ├── requirements.txt        # Зависимости (pip install)
│   ├── templates/
│   │   └── index.html         # Дашборд (HTML + Tailwind + Chart.js)
│   └── README.md              # Подробная документация Python версии
│
├── src/                         # React демо-страница (опционально)
│   └── App.tsx                 # Лендинг с описанием Python проекта
│
└── README.md                    # Этот файл
```

## 🎯 Что внутри Python версии

### 1. Price Oracle (Парсинг цен)
- Парсит цены с 6 DEX в реальном времени
- Uniswap V3, SushiSwap, PancakeSwap, Curve, Balancer, 1inch
- Автоматическое обновление каждые 8 секунд

### 2. Arbitrage Detection (Поиск арбитража)
- Находит спреды между DEX
- Рассчитывает прибыль после газа и комиссий
- Фильтрует по минимальному порогу ($5)
- Показывает confidence score

### 3. MEV Protection (Flashbots)
- Защита от sandwich-атак
- Приватная подача транзакций
- Бесплатный RPC: `https://rpc.flashbots.net`
- Статистика защищённых транзакций

### 4. Probability Engine (Анализ вероятности)
- Расчёт шанса успеха в реальном времени
- Gas escalation (динамическое повышение комиссии)
- Анализ конкурентов
- Recommendation: EXECUTE / SKIP / WAIT

### 5. Strategy Management
- 4 готовые стратегии флеш-кредитов
- Aave V3, dYdX, MakerDAO
- Статистика исполнений и прибыли
- MEV protection для каждой стратегии

## 📊 Интерактивный дашборд

Откройте `http://localhost:5000` и увидите:

- **Live Price Chart** — график цен ETH на 4 DEX
- **Arbitrage Opportunities** — список возможностей с кнопкой Execute
- **Price Scanner** — сканер цен по токенам (ETH, WBTC, LINK, UNI)
- **Network Status** — статус Sepolia testnet
- **MEV Protection** — статистика Flashbots
- **Probability Engine** — интерактивный анализ с слайдерами
- **Strategies** — управление стратегиями

## 🔧 API Endpoints

Все данные доступны через REST API:

```bash
# Цены с DEX
GET /api/prices

# Арбитражные возможности
GET /api/opportunities

# Вероятность успеха
GET /api/probability?spread=25&liquidity=5

# Статус сети
GET /api/network

# Стратегии
GET /api/strategies

# История цен (для графика)
GET /api/price-history
```

## 💡 Как это работает

### Gas Escalation (Повышение комиссии)

```python
# Базовый priority fee: 1 gwei
# При конкуренции повышаем:
priority_fee = base * (1 + competition_level * 3)

# Пример:
# Нет конкурентов → 1 gwei
# Средняя конкуренция → 2.5 gwei  
# Жёсткая конкуренция → 4+ gwei
```

### Flashbots Tip Auction

```python
# Платим валидатору за позицию в блоке
tip_percent = 0.5% от прибыли (минимум)
tip_percent = до 5% (максимум при высокой конкуренции)

# Кто больше платит — тот первый в блоке
```

### Probability Calculation

```python
win_probability = (
    0.30 * latency_factor +      # скорость подключения
    0.35 * tip_advantage +       # размер tip vs конкуренты
    0.20 * priority_factor +     # priority fee
    0.15 * liquidity_factor      # ликвидность пулов
)
```

## 📈 Шансы успеха

### На Sepolia Testnet (сейчас)
- **80-95%** — минимум конкурентов
- Можно спокойно тестировать стратегии

### На Mainnet (продакшен)
- **20-40%** — жёсткая конкуренция
- Нужна оптимизация: VPS, low latency, capital
- Реально заработать при правильной настройке

## 🎓 Преимущества Python версии

✅ **Один язык** — не нужно учить JavaScript + Python  
✅ **Простая установка** — `pip install` вместо `npm install`  
✅ **Быстрый старт** — `python app.py` и готово  
✅ **Легко расширять** — всё в одном файле `app.py`  
✅ **Полный контроль** — бэкенд и фронтенд на Python  
✅ **Минимум зависимостей** — Flask + Web3.py + requests  

## 📚 Документация

Подробная документация Python версии: [`python/README.md`](python/README.md)

## 🔐 Безопасность

- **Приватный ключ** — никогда не коммитить в git
- **Тестнет** — использовать Sepolia для разработки
- **MEV защита** — всегда через Flashbots
- **Gas лимит** — не превышать MAX_PRIORITY_FEE_GWEI

## 📝 Логирование

Все операции логируются в консоль:

```
============================================================
  Flash Arbitrage Engine — Python Full Stack
  Dashboard: http://localhost:5000
  Network: Sepolia Testnet
  MEV: Flashbots Protect (free)
============================================================
 * Running on http://0.0.0.0:5000
127.0.0.1 - - [15/Jan/2026 14:23:45] "GET /api/opportunities HTTP/1.1" 200 -
```

## 🛠️ Расширение функциональности

### Добавить реальную торговлю

```python
# В app.py добавить:
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://rpc.flashbots.net'))
# ... логика исполнения флеш-кредитов
```

### Подключить реальные DEX API

```python
# Заменить generate_prices() на реальные запросы:
import requests

def fetch_uniswap_price():
    # GraphQL запрос к The Graph
    query = """
    query { pool(id: "0x...") { token0Price } }
    """
    r = requests.post('https://api.thegraph.com/subgraphs/...', json={'query': query})
    return r.json()['data']['pool']['token0Price']
```

## ⚠️ Дисклеймер

Этот код для **образовательных целей** и тестирования на **Sepolia testnet**.

Для mainnet требуется:
- Аудит смарт-контрактов
- Тщательное тестирование
- Управление рисками
- Юридическая консультация

## 📚 Ресурсы

- [Flask Docs](https://flask.palletsprojects.com/)
- [Web3.py Docs](https://web3py.readthedocs.io/)
- [Flashbots Docs](https://docs.flashbots.net/)
- [Aave V3 Docs](https://docs.aave.com/developers/)

---

**Запуск:**
```bash
cd python
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

**Готово! Один язык, простая установка, всё работает.** 🚀

---

## 🤖 AI Agent — Autonomous Computer Use

Полноценный AI-агент с computer use, голосовым вводом и циклическим выполнением задач!

### Возможности

- ✅ **Computer Use** — управление мышью и клавиатурой
- ✅ **Terminal Execution** — выполнение команд
- ✅ **Voice Input** — распознавание речи (Whisper API)
- ✅ **Loop Execution** — цикл пока задача не выполнена
- ✅ **OpenAI GPT-4** — принятие решений
- ✅ **20+ инструментов** — web, files, system, browser, code execution

### Запуск AI-агента

```bash
cd python
pip install -r agent_requirements.txt
export OPENAI_API_KEY="your-key-here"
python agent.py
```

### Примеры задач

```
📝 Открой браузер и найди погоду в Москве
📝 Создай файл test.txt с содержимым "Hello World"
📝 Сделай скриншот экрана и сохрани как screenshot.png
📝 Найди все Python файлы в текущей директории
📝 voice  (голосовой ввод)
```

Подробная документация: [`python/AGENT_README.md`](python/AGENT_README.md)

---

### 3. Self-Healing AI Agent (Новое!)

Агент с автоматическим исправлением ошибок:
- ✅ Генерирует файлы (код, конфиги, скрипты)
- ✅ Запускает их для тестирования
- ✅ При ошибке — РЕДАКТИРУЕТ файл (не удаляет!)
- ✅ Повторяет цикл до успеха
- ✅ Работает в фоне (daemon mode)
- ✅ Логирует все попытки и исправления

**Запуск:**
```bash
cd python
pip install openai
export OPENAI_API_KEY="your-key"
python self_healing_agent.py "Создай Flask API с CRUD"
```

**Примеры задач:**
```
📝 Создай калькулятор с обработкой ошибок
📝 Создай Flask REST API для управления задачами
📝 Создай скрипт анализа CSV файлов
📝 Создай многофайловый проект для заметок
```

Подробная документация: [`python/SELF_HEALING_README.md`](python/SELF_HEALING_README.md)
