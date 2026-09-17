# Flash Arbitrage Engine — Python Backend

Полноценная система флеш-арбитража с парсингом цен, MEV-защитой и работой в тестовой сети Sepolia.

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Backend                            │
├─────────────────────────────────────────────────────────────┤
│  1. Price Oracle      → Парсинг цен с 6 DEX (The Graph API) │
│  2. Strategy Engine   → Расчёт спредов, фильтрация, ранг    │
│  3. Executor          → Сборка flash loan транзакций        │
│  4. MEV Guard         → Flashbots bundle (бесплатно)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Sepolia Testnet (Chain ID: 11155111)           │
│  • Flashbots RPC: https://rpc.flashbots.net                 │
│  • Aave V3 Pool: 0x6Ae43d3271ff6888e7Fc43Fd7321a503ff739485│
│  • Защита от sandwich-атак через приватный mempool          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd python
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
# Заполните PRIVATE_KEY (для Sepolia тестнета)
```

### 3. Запуск

```bash
python flash_arbitrage.py
```

## 📦 Структура проекта

```
python/
├── flash_arbitrage.py          # Основной скрипт
├── requirements.txt            # Python зависимости
├── contracts/
│   └── FlashArbitrageur.sol    # Solidity контракт для арбитража
└── README.md                   # Эта документация
```

## 🔧 Компоненты

### 1. Price Oracle
Парсит цены в реальном времени с:
- **Uniswap V3** — через The Graph subgraph
- **SushiSwap** — через GraphQL API
- **PancakeSwap** — через subgraph
- **Curve** — через REST API
- **Balancer** — через API
- **1inch** — через price API

### 2. Strategy Engine
- Рассчитывает спреды между всеми парами DEX
- Фильтрует по минимальному спреду (15 bps = 0.15%)
- Учитывает комиссию флеш-кредита (0.09% для Aave V3)
- Учитывает gas cost
- Рассчитывает confidence score на основе ликвидности и спреда

### 3. Flash Loan Executor
- Собирает транзакцию для Aave V3 flashLoan
- Подписывает транзакцию приватным ключом
- Готов к интеграции с кастомным контрактом `FlashArbitrageur.sol`

### 4. MEV Guard (Flashbots Protect)
- **Бесплатный** публичный RPC: `https://rpc.flashbots.net`
- Отправляет транзакции через Flashbots bundle
- Защита от sandwich-атак (приватный mempool)
- Симуляция bundle перед отправкой (`eth_callBundle`)
- Атомарное исполнение (revert → не включается в блок)

## 🧪 Тестовая сеть Sepolia

Все операции выполняются на **Sepolia testnet**:
- Chain ID: `11155111`
- Публичный RPC: `https://rpc.sepolia.org`
- Flashbots RPC: `https://rpc.flashbots.net`
- Бесплатные ETH: https://sepoliafaucet.com

## 📊 Параметры стратегии

```python
MIN_SPREAD_BPS = 15          # 0.15% — минимальный спред для входа
MIN_NET_PROFIT_USD = 5.0     # минимальная чистая прибыль после газа
FLASH_LOAN_FEE_BPS = 9       # Aave V3 комиссия 0.09%
DEFAULT_GAS_LIMIT = 500_000  # лимит газа на транзакцию
```

## 🔐 Безопасность

- **Приватный ключ** хранится только в `.env`, не коммитится в git
- **MEV защита** через Flashbots — транзакции не видны в публичном mempool
- **Симуляция** bundle перед реальной отправкой
- **Тестнет** для разработки и тестирования

## 🌐 Интеграция с фронтендом

Python бэкенд может отдавать данные через REST API (Flask/FastAPI) для React дашборда:

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/opportunities")
def get_opportunities():
    prices = oracle.scan("ETH")
    return engine.find_opportunities(prices)

@app.post("/api/execute/{opp_id}")
def execute_arbitrage(opp_id: str):
    # ... логика исполнения
    pass
```

## 📝 Логирование

Все операции логируются с таймстемпами:
```
14:23:45 [INFO] Scanned 5 DEX for ETH — got 5 prices
14:23:45 [INFO] Found 3 opportunities
14:23:45 [INFO] Best: ETH on Uniswap V3 → SushiSwap, spread=23.45 bps, net=$127.50
14:23:46 [INFO] Built flash loan tx: Uniswap V3 → SushiSwap, loan=50 ETH, spread=23.45 bps
14:23:47 [INFO] Flashbots bundle sent: {'result': '0x...'}
```

## ⚠️ Дисклеймер

Этот код предназначен для **образовательных целей** и тестирования на **Sepolia testnet**.
Для использования на mainnet требуется:
- Аудит смарт-контракта
- Тщательное тестирование
- Мониторинг и алерты
- Управление рисками

## 📚 Ресурсы

- [Flashbots Docs](https://docs.flashbots.net/)
- [Aave V3 Docs](https://docs.aave.com/developers/)
- [Web3.py Docs](https://web3py.readthedocs.io/)
- [The Graph](https://thegraph.com/docs/)
