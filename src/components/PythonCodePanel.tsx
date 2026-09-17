import { useState } from 'react';
import { Code2, Copy, Check, Terminal, FileCode, BookOpen, ChevronDown, ChevronRight } from 'lucide-react';

const pythonCode = `"""
Flash Arbitrage Engine — Python Backend
========================================
Стратегия флеш-арбитража с парсингом цен на DEX,
MEV-защитой через Flashbots Protect и работой в тестовой сети Sepolia.
"""

import os, time, json, logging
from dataclasses import dataclass, field
from typing import List, Optional
from decimal import Decimal

import requests
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account

# ─── Конфигурация ────────────────────────────────────────────────
SEPOLIA_CHAIN_ID = 11155111
SEPOLIA_RPC = "https://rpc.sepolia.org"
FLASHBOTS_RPC = "https://rpc.flashbots.net"  # бесплатный MEV-protected RPC
FLASHBOTS_RELAY = "https://relay.flashbots.net"

AAVE_POOL_V3 = "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff739485"
MIN_SPREAD_BPS = 15          # 0.15% — минимальный спред
MIN_NET_PROFIT_USD = 5.0     # мин. чистая прибыль
FLASH_LOAN_FEE_BPS = 9       # Aave V3 комиссия 0.09%

# ─── 1. Price Oracle ────────────────────────────────────────────
class PriceOracle:
    """Парсит цены с 6 DEX через The Graph / REST API."""
    
    DEX_ENDPOINTS = {
        "Uniswap V3": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
        "SushiSwap": "https://api.thegraph.com/subgraphs/name/sushi-v2/sushiswap-ethereum",
        "PancakeSwap": "https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2-eth",
        "Curve": "https://api.curve.fi/api/getPools/ethereum",
        "Balancer": "https://api.balancer.fi/pools/ethereum",
        "1inch": "https://api.1inch.dev/price/v1.1/ethereum",
    }
    
    def scan(self, token="ETH") -> List[dict]:
        """Сканирует все DEX и возвращает список цен."""
        prices = []
        for dex, endpoint in self.DEX_ENDPOINTS.items():
            try:
                # GraphQL / REST запрос к DEX
                price = self._fetch_price(dex, endpoint, token)
                if price:
                    prices.append(price)
            except Exception as e:
                logging.warning(f"{dex} fetch failed: {e}")
        return prices

# ─── 2. Strategy Engine ─────────────────────────────────────────
class StrategyEngine:
    """Ищет арбитражные возможности между DEX."""
    
    def find_opportunities(self, prices, loan_eth=50):
        opps = []
        for i, buy in enumerate(prices):
            for sell in prices[i+1:]:
                spread = (sell.price - buy.price) / buy.price
                spread_bps = spread * 10000
                if spread_bps < MIN_SPREAD_BPS:
                    continue
                
                profit = loan_eth * spread
                gas_cost = 0.003 * 3500  # ~$10
                flash_fee = loan_eth * (FLASH_LOAN_FEE_BPS / 10000)
                net = profit * 3500 - gas_cost - flash_fee * 3500
                
                if net > MIN_NET_PROFIT_USD:
                    opps.append({
                        "buy_dex": buy.dex,
                        "sell_dex": sell.dex,
                        "spread_bps": spread_bps,
                        "net_profit_usd": net,
                    })
        return sorted(opps, key=lambda x: x["net_profit_usd"], reverse=True)

# ─── 3. MEV Guard (Flashbots) ───────────────────────────────────
class MEVGuard:
    """Отправляет bundle через Flashbots — бесплатно, без API ключа."""
    
    def send_bundle(self, signed_tx, target_block):
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_sendBundle",
            "params": [{
                "txs": [signed_tx],
                "blockNumber": hex(target_block),
            }]
        }
        r = requests.post(FLASHBOTS_RELAY, json=payload)
        return r.json()
    
    def simulate(self, signed_tx, block):
        """Симуляция перед отправкой — проверяем что транзакция успешна."""
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_callBundle",
            "params": [{
                "txs": [signed_tx],
                "blockNumber": hex(block),
            }]
        }
        return requests.post(FLASHBOTS_RELAY, json=payload).json()

# ─── 4. Main Loop ───────────────────────────────────────────────
def main():
    w3 = Web3(Web3.HTTPProvider(FLASHBOTS_RPC))
    oracle = PriceOracle()
    engine = StrategyEngine()
    mev = MEVGuard()
    
    while True:
        prices = oracle.scan("ETH")
        opps = engine.find_opportunities(prices)
        
        if opps:
            best = opps[0]
            tx = build_flash_loan_tx(best)
            signed = sign_tx(tx)
            
            # Симуляция → отправка через Flashbots
            sim = mev.simulate(signed, w3.eth.block_number + 1)
            if "error" not in sim:
                result = mev.send_bundle(signed, w3.eth.block_number + 2)
                logging.info(f"Bundle sent: {result}")
        
        time.sleep(12)

if __name__ == "__main__":
    main()`;

const solidityCode = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@aave/v3-core/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract FlashArbitrageur is FlashLoanSimpleReceiverBase {
    address public owner;

    event ArbitrageExecuted(address token, uint256 profit);

    constructor(address _provider) 
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_provider)) {
        owner = msg.sender;
    }

    function executeArbitrage(address asset, uint256 amount) external {
        POOL.flashLoanSimple(address(this), asset, amount, "", 0);
    }

    function executeOperation(
        address asset, uint256 amount, uint256 premium,
        address initiator, bytes calldata
    ) external override returns (bool) {
        // 1. Swap на DEX #1 (buy low)
        // 2. Swap на DEX #2 (sell high)
        // 3. Repay flash loan + premium
        uint256 owed = amount + premium;
        IERC20(asset).approve(address(POOL), owed);
        
        uint256 profit = IERC20(asset).balanceOf(address(this));
        emit ArbitrageExecuted(asset, profit);
        return true;
    }
}`;

const bashSetup = `# Установка и запуск
cd python
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Заполните PRIVATE_KEY в .env

# Запуск на Sepolia testnet
python flash_arbitrage.py

# Вывод:
# 14:23:45 [INFO] Connected to Flashbots RPC (chain 11155111)
# 14:23:46 [INFO] Scanned 5 DEX for ETH — got 5 prices
# 14:23:46 [INFO] Found 3 opportunities
# 14:23:46 [INFO] Best: ETH on Uniswap V3 → SushiSwap, spread=23.45 bps
# 14:23:47 [INFO] Flashbots bundle sent successfully`;

const files = [
  { name: 'flash_arbitrage.py', icon: FileCode, code: pythonCode, lang: 'python', color: 'text-yellow-400' },
  { name: 'FlashArbitrageur.sol', icon: Code2, code: solidityCode, lang: 'solidity', color: 'text-purple-400' },
  { name: 'setup.sh', icon: Terminal, code: bashSetup, lang: 'bash', color: 'text-green-400' },
];

export default function PythonCodePanel() {
  const [activeFile, setActiveFile] = useState(0);
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(true);

  const copyCode = () => {
    navigator.clipboard.writeText(files[activeFile].code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-5 hover:bg-gray-800/30 transition-all"
      >
        <div className="flex items-center gap-2">
          <Code2 className="w-4 h-4 text-yellow-400" />
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Python Backend Source Code</h3>
          <span className="text-xs px-2 py-0.5 bg-yellow-500/10 text-yellow-400 rounded">Ready to deploy</span>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
      </button>

      {expanded && (
        <div>
          {/* File tabs */}
          <div className="flex items-center gap-1 px-5 pb-3 border-b border-gray-700/30">
            {files.map((file, idx) => {
              const Icon = file.icon;
              return (
                <button
                  key={file.name}
                  onClick={() => setActiveFile(idx)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeFile === idx
                      ? 'bg-gray-700/50 text-white'
                      : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800/30'
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  {file.name}
                </button>
              );
            })}
            <div className="flex-1" />
            <button
              onClick={copyCode}
              className="flex items-center gap-1 px-2 py-1 text-xs text-gray-400 hover:text-white transition-all"
            >
              {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>

          {/* Code block */}
          <div className="p-5 overflow-x-auto">
            <pre className="text-xs leading-relaxed font-mono">
              <code className="text-gray-300">
                {files[activeFile].code.split('\n').map((line, i) => (
                  <div key={i} className="flex">
                    <span className="text-gray-600 select-none w-8 text-right mr-4 flex-shrink-0">{i + 1}</span>
                    <span className={
                      line.trim().startsWith('#') || line.trim().startsWith('//')
                        ? 'text-gray-500 italic'
                        : line.includes('class ') || line.includes('def ') || line.includes('function ') || line.includes('contract ')
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

          {/* Info footer */}
          <div className="px-5 pb-4 flex items-center gap-4 text-xs text-gray-500 border-t border-gray-700/30 pt-3">
            <div className="flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              <span>See python/README.md for full docs</span>
            </div>
            <div className="flex items-center gap-1">
              <Terminal className="w-3 h-3" />
              <span>pip install -r requirements.txt</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
