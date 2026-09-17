"""
Flash Arbitrage Engine — Python Full Stack
============================================
Однофайловый Flask веб-сервер с полным дашбордом.
Запуск: pip install -r requirements.txt && python app.py
"""

from flask import Flask, render_template, jsonify, request
import json
import time
import random
import math
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)

# ─── Mock данные (в реальности — запросы к DEX API) ─────────────
TOKENS = ['ETH', 'WBTC', 'LINK', 'UNI', 'DAI']
DEXES = ['Uniswap V3', 'SushiSwap', 'PancakeSwap', 'Curve', 'Balancer', '1inch']

def generate_prices():
    """Генерирует цены с DEX (имитация парсинга)."""
    base = {'ETH': 3450, 'WBTC': 67500, 'LINK': 18.5, 'UNI': 12.3, 'DAI': 1.0}
    prices = {}
    for dex in DEXES[:4]:
        prices[dex] = {}
        for token, bp in base.items():
            prices[dex][token] = bp * (1 + (random.random() - 0.5) * 0.008)
    return prices

def find_opportunities(prices):
    """Ищет арбитражные возможности."""
    opps = []
    for token in TOKENS:
        dex_prices = [(dex, prices[dex].get(token, 0)) for dex in DEXES[:4]]
        dex_prices = [(d, p) for d, p in dex_prices if p > 0]
        if len(dex_prices) < 2:
            continue
        
        for i, (buy_dex, buy_price) in enumerate(dex_prices):
            for sell_dex, sell_price in dex_prices[i+1:]:
                if sell_price <= buy_price:
                    continue
                spread = (sell_price - buy_price) / buy_price
                spread_bps = spread * 10000
                if spread_bps < 15:
                    continue
                
                loan = 50 if token == 'ETH' else 10000
                gross = loan * spread * buy_price
                gas = 0.003 * 3450
                fee = loan * 0.0009 * buy_price
                net = gross - gas - fee
                
                if net > 5:
                    opps.append({
                        'id': f"{token}-{buy_dex}-{sell_dex}",
                        'token': token,
                        'buy_dex': buy_dex,
                        'sell_dex': sell_dex,
                        'buy_price': round(buy_price, 2),
                        'sell_price': round(sell_price, 2),
                        'spread_bps': round(spread_bps, 3),
                        'gross_profit': round(gross, 2),
                        'gas_cost': round(gas, 2),
                        'net_profit': round(net, 2),
                        'confidence': random.randint(70, 99),
                        'timestamp': int(time.time()),
                    })
    
    return sorted(opps, key=lambda x: x['net_profit'], reverse=True)

def calculate_probability(spread_bps, liquidity_m, latency_ms=150):
    """Расчёт вероятности успеха."""
    competitors = max(0, int((spread_bps - 10) / 5))
    
    latency_factor = max(0, 1 - latency_ms / 1000)
    competition_level = min(spread_bps / 100, 1)
    
    # Gas escalation
    base_fee = 1.0 + random.random() * 2
    priority_fee = 1.0 * (1 + competition_level * 3)
    tip_percent = min(0.5 * (1 + competition_level * 2), 5.0)
    
    gross_profit = spread_bps * 0.01 * 50 * 3450
    tip_usd = gross_profit * (tip_percent / 100)
    gas_usd = (500000 * (base_fee + priority_fee) * 1e-9) * 3450
    total_cost = gas_usd + tip_usd
    
    avg_competitor_tip = 2.0
    tip_advantage = min(tip_percent / avg_competitor_tip / (competitors + 1), 1)
    priority_factor = min(priority_fee / 10, 1)
    liq_factor = min(liquidity_m / 1, 1)
    
    win_prob = (0.30 * latency_factor + 0.35 * tip_advantage + 
                0.20 * priority_factor + 0.15 * liq_factor)
    if competitors > 0:
        win_prob *= 1 / (1 + competitors * 0.3)
    win_prob = max(0, min(1, win_prob))
    
    net_profit = gross_profit - total_cost
    ev = win_prob * net_profit - (1 - win_prob) * total_cost
    
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
        'latency_ms': round(latency_ms, 0),
        'gas_bid_rank': 1 if tip_advantage > 0.7 else 2 if tip_advantage > 0.4 else 3,
        'recommendation': rec,
        'factors': {
            'latency': round(latency_factor * 100),
            'tip_advantage': round(tip_advantage * 100),
            'priority_fee': round(priority_factor * 100),
            'liquidity': round(liq_factor * 100),
        },
        'gas_bid': {
            'base_fee': round(base_fee, 2),
            'priority_fee': round(priority_fee, 2),
            'tip_usd': round(tip_usd, 2),
            'tip_percent': round(tip_percent, 1),
            'total_cost': round(total_cost, 2),
            'escalation_level': int(competition_level * 10),
        },
    }

# ─── Routes ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prices')
def api_prices():
    prices = generate_prices()
    return jsonify(prices)

@app.route('/api/opportunities')
def api_opportunities():
    prices = generate_prices()
    opps = find_opportunities(prices)
    return jsonify(opps)

@app.route('/api/probability')
def api_probability():
    spread = request.args.get('spread', 25, type=float)
    liquidity = request.args.get('liquidity', 5, type=float)
    latency = request.args.get('latency', 150, type=float)
    result = calculate_probability(spread, liquidity, latency)
    return jsonify(result)

@app.route('/api/network')
def api_network():
    return jsonify({
        'network': 'Sepolia Testnet',
        'chain_id': 11155111,
        'block_number': 5847291 + random.randint(0, 100),
        'gas_price': round(2 + random.random() * 3, 2),
        'rpc_endpoint': 'https://rpc.sepolia.org',
        'mev_rpc': 'https://rpc.flashbots.net',
        'mev_status': 'active',
        'protected_txs': 156 + random.randint(0, 10),
        'sandwich_blocked': 23,
        'total_saved': round(0.847 + random.random() * 0.1, 3),
    })

@app.route('/api/strategies')
def api_strategies():
    return jsonify([
        {
            'id': 'strat-1',
            'name': 'ETH Cross-DEX Arbitrage',
            'protocol': 'Aave V3',
            'status': 'testing',
            'executions': 47,
            'success_rate': 91.5,
            'total_profit': 2.34,
            'mev_protection': True,
        },
        {
            'id': 'strat-2',
            'name': 'Stablecoin Triangular',
            'protocol': 'dYdX',
            'status': 'active',
            'executions': 128,
            'success_rate': 96.1,
            'total_profit': 5.67,
            'mev_protection': True,
        },
        {
            'id': 'strat-3',
            'name': 'WBTC Price Convergence',
            'protocol': 'Aave V3',
            'status': 'paused',
            'executions': 23,
            'success_rate': 87.0,
            'total_profit': 1.12,
            'mev_protection': True,
        },
        {
            'id': 'strat-4',
            'name': 'LINK Liquidity Sweep',
            'protocol': 'MakerDAO',
            'status': 'active',
            'executions': 89,
            'success_rate': 93.3,
            'total_profit': 3.89,
            'mev_protection': True,
        },
    ])

@app.route('/api/price-history')
def api_price_history():
    history = []
    base = 3450
    for i in range(60, -1, -1):
        drift = math.sin(i / 10) * 5
        history.append({
            'time': i,
            'uniswap': round(base + drift + (random.random() - 0.5) * 3, 2),
            'sushiswap': round(base + drift + 2 + (random.random() - 0.5) * 4, 2),
            'pancakeswap': round(base + drift - 1.5 + (random.random() - 0.5) * 3, 2),
            'curve': round(base + drift + 0.5 + (random.random() - 0.5) * 2, 2),
        })
    return jsonify(history)

if __name__ == '__main__':
    print("=" * 60)
    print("  Flash Arbitrage Engine — Python Full Stack")
    print("  Dashboard: http://localhost:5000")
    print("  Network: Sepolia Testnet")
    print("  MEV: Flashbots Protect (free)")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
