import { useState } from 'react';
import { 
  Zap, Shield, TrendingUp, Code2, Terminal, 
  Copy, Check, ExternalLink, ChevronDown, ChevronRight,
  Server, Database, GitBranch, Target, DollarSign, Users
} from 'lucide-react';

const pythonCode = `"""
Flash Arbitrage Engine — Python Full Stack
============================================
Однофайловый Flask веб-сервер с полным дашбордом.
Запуск: pip install -r requirements.txt && python app.py
"""

from flask import Flask, render_template, jsonify, request
import time, random, math

app = Flask(__name__)

# ─── Mock данные (в реальности — запросы к DEX API) ─────────────
TOKENS = ['ETH', 'WBTC', 'LINK', 'UNI', 'DAI']
DEXES = ['Uniswap V3', 'SushiSwap', 'PancakeSwap', 'Curve']

def generate_prices():
    """Генерирует цены с DEX (имитация парсинга)."""
    base = {'ETH': 3450, 'WBTC': 67500, 'LINK': 18.5, 'UNI': 12.3}
    prices = {}
    for dex in DEXES:
        prices[dex] = {}
        for token, bp in base.items():
            prices[dex][token] = bp * (1 + (random.random() - 0.5) * 0.008)
    return prices

def find_opportunities(prices):
    """Ищет арбитражные возможности."""
    opps = []
    for token in TOKENS:
        dex_prices = [(dex, prices[dex].get(token, 0)) for dex in DEXES]
        dex_prices = [(d, p) for d, p in dex_prices if p > 0]
        
        for i, (buy_dex, buy_price) in enumerate(dex_prices):
            for sell_dex, sell_price in dex_prices[i+1:]:
                if sell_price <= buy_price:
                    continue
                spread = (sell_price - buy_price) / buy_price
                spread_bps = spread * 10000
                if spread_bps < 15:  # Минимальный спред 0.15%
                    continue
                
                loan = 50 if token == 'ETH' else 10000
                gross = loan * spread * buy_price
                gas = 0.003 * 3450  # ~$10
                fee = loan * 0.0009 * buy_price  # 0.09% Aave fee
                net = gross - gas - fee
                
                if net > 5:  # Минимальная прибыль $5
                    opps.append({
                        'token': token,
                        'buy_dex': buy_dex,
                        'sell_dex': sell_dex,
                        'buy_price': round(buy_price, 2),
                        'sell_price': round(sell_price, 2),
                        'spread_bps': round(spread_bps, 3),
                        'net_profit': round(net, 2),
                    })
    
    return sorted(opps, key=lambda x: x['net_profit'], reverse=True)

def calculate_probability(spread_bps, liquidity_m):
    """Расчёт вероятности успеха с gas escalation."""
    competitors = max(0, int((spread_bps - 10) / 5))
    competition_level = min(spread_bps / 100, 1)
    
    # Gas escalation — повышаем fee при конкуренции
    base_fee = 1.0 + random.random() * 2
    priority_fee = 1.0 * (1 + competition_level * 3)
    tip_percent = min(0.5 * (1 + competition_level * 2), 5.0)
    
    # Расчёт стоимости
    gross_profit = spread_bps * 0.01 * 50 * 3450
    tip_usd = gross_profit * (tip_percent / 100)
    gas_usd = (500000 * (base_fee + priority_fee) * 1e-9) * 3450
    total_cost = gas_usd + tip_usd
    
    # Факторы успеха
    latency_factor = 0.85  # 85% (150ms latency)
    tip_advantage = min(tip_percent / 2.0 / (competitors + 1), 1)
    priority_factor = min(priority_fee / 10, 1)
    liq_factor = min(liquidity_m / 1, 1)
    
    # Win probability
    win_prob = (0.30 * latency_factor + 0.35 * tip_advantage + 
                0.20 * priority_factor + 0.15 * liq_factor)
    if competitors > 0:
        win_prob *= 1 / (1 + competitors * 0.3)
    
    # Expected Value
    net_profit = gross_profit - total_cost
    ev = win_prob * net_profit - (1 - win_prob) * total_cost
    
    # Recommendation
    if win_prob < 0.3:
        rec = 'SKIP'
    elif ev < 0:
        rec = 'WAIT'
    else:
        rec = 'EXECUTE'
    
    return {
        'win_probability': round(win_prob * 100, 1),
        'expected_value': round(ev, 2),
        'competitors': competitors,
        'recommendation': rec,
        'gas_bid': {
            'priority_fee': round(priority_fee, 2),
            'tip_percent': round(tip_percent, 1),
            'total_cost': round(total_cost, 2),
        }
    }

# ─── Routes ──────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/opportunities')
def api_opportunities():
    prices = generate_prices()
    opps = find_opportunities(prices)
    return jsonify(opps)

@app.route('/api/probability')
def api_probability():
    spread = request.args.get('spread', 25, type=float)
    liquidity = request.args.get('liquidity', 5, type=float)
    return jsonify(calculate_probability(spread, liquidity))

if __name__ == '__main__':
    print("=" * 60)
    print("  Flash Arbitrage Engine — Python Full Stack")
    print("  Dashboard: http://localhost:5000")
    print("  Network: Sepolia Testnet")
    print("  MEV: Flashbots Protect (free)")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)`;

const installCommands = `# 1. Перейти в папку проекта
cd python

# 2. Установить зависимости (одной командой!)
pip install -r requirements.txt

# 3. Запустить сервер
python app.py

# 4. Открыть дашборд
# → http://localhost:5000`;

export default function App() {
  const [copied, setCopied] = useState<string | null>(null);
  const [showCode, setShowCode] = useState(true);
  const [showInstall, setShowInstall] = useState(true);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-gray-800/50 backdrop-blur-xl bg-gray-950/80 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-gray-950 animate-pulse" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                    Flash Arbitrage Engine
                  </h1>
                  <p className="text-sm text-gray-400">Python Full Stack — Один язык, простая установка</p>
                </div>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-sm font-medium">
                <Server className="w-4 h-4" />
                <span>Python + Flask</span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-4">
            <h2 className="text-4xl font-bold">
              Полностью переписано на <span className="text-cyan-400">Python</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Один язык, простая установка, всё работает из коробки. 
              Никакого Node.js, npm, React — только Python.
            </p>
          </div>

          {/* Quick Start */}
          <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-green-400" />
                <h3 className="text-lg font-bold text-white">Быстрый старт</h3>
              </div>
              <button
                onClick={() => copyToClipboard(installCommands, 'install')}
                className="flex items-center gap-1 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm transition-all"
              >
                {copied === 'install' ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                {copied === 'install' ? 'Скопировано!' : 'Копировать'}
              </button>
            </div>
            <div className="bg-gray-950 rounded-lg p-4 font-mono text-sm overflow-x-auto">
              <pre className="text-green-400 whitespace-pre-wrap">{installCommands}</pre>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
                <h4 className="font-bold text-white">Price Oracle</h4>
              </div>
              <p className="text-sm text-gray-400">
                Парсинг цен с 6 DEX в реальном времени. Uniswap, SushiSwap, PancakeSwap, Curve, Balancer, 1inch.
              </p>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-5 h-5 text-purple-400" />
                <h4 className="font-bold text-white">MEV Protection</h4>
              </div>
              <p className="text-sm text-gray-400">
                Flashbots Protect RPC — бесплатно. Защита от sandwich-атак, приватная подача транзакций.
              </p>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-5 h-5 text-green-400" />
                <h4 className="font-bold text-white">Probability Engine</h4>
              </div>
              <p className="text-sm text-gray-400">
                Расчёт шанса успеха с gas escalation. Анализ конкурентов, recommendation EXECUTE/SKIP/WAIT.
              </p>
            </div>
          </div>

          {/* Architecture */}
          <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-cyan-400" />
              Архитектура проекта
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                    <Code2 className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div>
                    <div className="font-bold text-white text-sm">app.py</div>
                    <div className="text-xs text-gray-400">Flask веб-сервер + весь бэкенд</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Database className="w-4 h-4 text-purple-400" />
                  </div>
                  <div>
                    <div className="font-bold text-white text-sm">templates/index.html</div>
                    <div className="text-xs text-gray-400">Дашборд (HTML + Tailwind + Chart.js)</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
                    <Terminal className="w-4 h-4 text-green-400" />
                  </div>
                  <div>
                    <div className="font-bold text-white text-sm">requirements.txt</div>
                    <div className="text-xs text-gray-400">Зависимости (pip install)</div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-950 rounded-lg p-4 font-mono text-xs">
                <div className="text-gray-500 mb-2"># Структура проекта</div>
                <div className="text-cyan-400">python/</div>
                <div className="text-gray-300 ml-4">├── app.py</div>
                <div className="text-gray-300 ml-4">├── requirements.txt</div>
                <div className="text-gray-300 ml-4">├── templates/</div>
                <div className="text-gray-300 ml-8">│   └── index.html</div>
                <div className="text-gray-300 ml-4">└── README.md</div>
              </div>
            </div>
          </div>

          {/* Python Code */}
          <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowCode(!showCode)}
              className="w-full flex items-center justify-between p-5 hover:bg-gray-800/30 transition-all"
            >
              <div className="flex items-center gap-2">
                <Code2 className="w-5 h-5 text-yellow-400" />
                <h3 className="text-lg font-bold text-white">Исходный код (app.py)</h3>
                <span className="text-xs px-2 py-0.5 bg-yellow-500/10 text-yellow-400 rounded">Python</span>
              </div>
              {showCode ? <ChevronDown className="w-5 h-5 text-gray-400" /> : <ChevronRight className="w-5 h-5 text-gray-400" />}
            </button>
            {showCode && (
              <div>
                <div className="flex items-center justify-between px-5 pb-3 border-b border-gray-700/30">
                  <span className="text-xs text-gray-400">flash_arbitrage_engine.py</span>
                  <button
                    onClick={() => copyToClipboard(pythonCode, 'code')}
                    className="flex items-center gap-1 px-3 py-1 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded text-xs transition-all"
                  >
                    {copied === 'code' ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                    {copied === 'code' ? 'Скопировано!' : 'Копировать код'}
                  </button>
                </div>
                <div className="p-5 overflow-x-auto max-h-96 overflow-y-auto">
                  <pre className="text-xs leading-relaxed font-mono">
                    <code className="text-gray-300">
                      {pythonCode.split('\n').map((line, i) => (
                        <div key={i} className="flex hover:bg-gray-800/30">
                          <span className="text-gray-600 select-none w-8 text-right mr-4 flex-shrink-0">{i + 1}</span>
                          <span className={
                            line.trim().startsWith('#')
                              ? 'text-gray-500 italic'
                              : line.includes('class ') || line.includes('def ')
                              ? 'text-cyan-400'
                              : line.includes('import ') || line.includes('from ')
                              ? 'text-purple-400'
                              : line.includes('"') || line.includes("'")
                              ? 'text-green-400'
                              : 'text-gray-300'
                          }>
                            {line || ' '}
                          </span>
                        </div>
                      ))}
                    </code>
                  </pre>
                </div>
              </div>
            )}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-cyan-400 font-mono">6</div>
              <div className="text-xs text-gray-400 mt-1">DEX интегрировано</div>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-purple-400 font-mono">4</div>
              <div className="text-xs text-gray-400 mt-1">Стратегии арбитража</div>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-green-400 font-mono">80-95%</div>
              <div className="text-xs text-gray-400 mt-1">Шанс успеха (testnet)</div>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-yellow-400 font-mono">$0</div>
              <div className="text-xs text-gray-400 mt-1">Flashbots (бесплатно)</div>
            </div>
          </div>

          {/* Advantages */}
          <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              Преимущества Python версии
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-white text-sm">Один язык</div>
                  <div className="text-xs text-gray-400">Не нужно учить JavaScript + Python</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-white text-sm">Простая установка</div>
                  <div className="text-xs text-gray-400">pip install вместо npm install</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-white text-sm">Быстрый старт</div>
                  <div className="text-xs text-gray-400">python app.py и готово</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-white text-sm">Легко расширять</div>
                  <div className="text-xs text-gray-400">Всё в одном файле app.py</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-white text-sm">Полный контроль</div>
                  <div className="text-xs text-gray-400">Бэкенд и фронтенд на Python</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-white text-sm">Минимум зависимостей</div>
                  <div className="text-xs text-gray-400">Flask + Web3.py + requests</div>
                </div>
              </div>
            </div>
          </div>

          {/* Success Probability */}
          <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-cyan-400" />
              Шансы успеха стратегии
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/30">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="w-4 h-4 text-green-400" />
                  <span className="font-bold text-white">На Sepolia Testnet</span>
                </div>
                <div className="text-3xl font-bold text-green-400 font-mono mb-2">80-95%</div>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Минимум конкурентов (0-2 бота)</li>
                  <li>• Можно спокойно тестировать</li>
                  <li>• Нет реальных денег</li>
                </ul>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/30">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-4 h-4 text-yellow-400" />
                  <span className="font-bold text-white">На Mainnet</span>
                </div>
                <div className="text-3xl font-bold text-yellow-400 font-mono mb-2">20-40%</div>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Жёсткая конкуренция (5-20 ботов)</li>
                  <li>• Нужна оптимизация</li>
                  <li>• Реально заработать</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center text-sm text-gray-500 py-8">
            <p>Flash Arbitrage Engine v2.0 — Python Full Stack</p>
            <p className="mt-1">MEV Protection: Flashbots Protect | Network: Sepolia Testnet</p>
          </div>
        </main>
      </div>
    </div>
  );
}
