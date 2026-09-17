import { useState } from 'react';
import { Code2, Copy, Check, Terminal, FileCode, BookOpen, ChevronDown, ChevronRight } from 'lucide-react';

const pythonCode = `"""
Flash Arbitrage Engine v2.0 — Gas Escalation & MEV Bidding
============================================================
Ключевое: динамическое повышение priority fee чтобы быть ПЕРВЫМ.
Flashbots tip auction — платим валидатору за позицию в блоке.
"""

import os, time, math, logging
from dataclasses import dataclass
from decimal import Decimal
import requests
from web3 import Web3
from eth_account import Account

# ─── Gas Bidding Параметры ──────────────────────────────────────
BASE_PRIORITY_FEE_GWEI = 1.0      # стартуем с 1 gwei
MAX_PRIORITY_FEE_GWEI = 50.0      # потолок — не разоряемся
GAS_ESCALATION_STEP = 1.5         # множитель при конкуренции
FLASHBOTS_TIP_PERCENT = 0.5       # % прибыли → валидатору
MAX_TIP_PERCENT = 5.0             # максимум tip в аукционе
COMPETITION_THRESHOLD = 0.3       # шанс < 30% → SKIP

# ─── 1. Gas Escalation Engine ───────────────────────────────────
class GasEscalationEngine:
    """
    Динамически повышает priority fee чтобы транзакция была первой.
    Чем выше конкуренция — тем больше fee.
    """
    def __init__(self, w3, base_fee=1.0, max_fee=50.0):
        self.w3 = w3
        self.base_fee = base_fee
        self.max_fee = max_fee
    
    def calculate_bid(self, net_profit_usd, competition_level=0.0):
        """
        competition_level: 0.0 (нет конкурентов) — 1.0 (максимум)
        """
        base_fee = self._get_base_fee()
        
        # Priority Fee Escalation
        priority_fee = self.base_fee * (1 + competition_level * 3)
        priority_fee = min(priority_fee, self.max_fee)
        
        # Flashbots Tip (аукцион за позицию)
        tip_percent = 0.5 * (1 + competition_level * 2)
        tip_percent = min(tip_percent, MAX_TIP_PERCENT)
        tip_usd = net_profit_usd * (tip_percent / 100)
        
        # Total gas cost
        gas_eth = 500_000 * (base_fee + priority_fee) * 1e-9
        gas_usd = gas_eth * 3500
        total_cost = gas_usd + tip_usd
        
        return {
            "base_fee": base_fee,
            "priority_fee": priority_fee,
            "tip_usd": tip_usd,
            "tip_percent": tip_percent,
            "total_cost": total_cost,
        }

# ─── 2. Probability Engine ──────────────────────────────────────
class ProbabilityEngine:
    """
    Оценивает шанс что наша tx будет первой.
    Факторы: латентность, tip, priority fee, ликвидность.
    """
    def __init__(self, w3):
        self.w3 = w3
        self.latency_ms = self._measure_latency()
    
    def _measure_latency(self):
        start = time.time()
        requests.post("https://relay.flashbots.net", 
                     json={"jsonrpc":"2.0","method":"eth_blockNumber","id":1})
        return (time.time() - start) * 1000
    
    def estimate_competitors(self, spread_bps):
        """Чем больше спред — тем больше ботов его видят."""
        return max(0, int((spread_bps - 10) / 5))
    
    def calculate(self, opp, gas_bid):
        competitors = self.estimate_competitors(opp["spread_bps"])
        
        # Факторы успеха
        latency_factor = max(0, 1 - self.latency_ms / 1000)
        tip_advantage = min(gas_bid["tip_percent"] / 2.0 / (competitors + 1), 1)
        priority_factor = min(gas_bid["priority_fee"] / 10, 1)
        
        # Win probability
        win_prob = (0.30 * latency_factor + 
                   0.35 * tip_advantage + 
                   0.20 * priority_factor + 
                   0.15 * 1.0)  # liquidity factor
        
        if competitors > 0:
            win_prob *= 1 / (1 + competitors * 0.3)
        
        # Expected Value
        ev = (win_prob * opp["net_profit_usd"] - 
              (1 - win_prob) * gas_bid["total_cost"])
        
        # Recommendation
        if win_prob < 0.3:
            rec = "SKIP"
        elif ev < 0:
            rec = "WAIT"
        else:
            rec = "EXECUTE"
        
        return {
            "win_probability": win_prob,
            "expected_value": ev,
            "competitors": competitors,
            "recommendation": rec,
        }

# ─── 3. Main Loop (v2.0) ───────────────────────────────────────
def main():
    w3 = Web3(Web3.HTTPProvider("https://rpc.flashbots.net"))
    gas_engine = GasEscalationEngine(w3)
    prob_engine = ProbabilityEngine(w3)
    
    while True:
        # 1. Находим возможность
        opp = find_best_opportunity()  # парсинг цен...
        if not opp:
            time.sleep(10)
            continue
        
        # 2. Оцениваем конкуренцию
        competition = min(opp["spread_bps"] / 100, 1.0)
        
        # 3. Gas bid (повышаем fee если конкуренция)
        gas_bid = gas_engine.calculate_bid(opp["net_profit_usd"], competition)
        
        # 4. Вероятность успеха
        prob = prob_engine.calculate(opp, gas_bid)
        
        # 5. Решение
        if prob["recommendation"] == "EXECUTE":
            tx = build_tx(opp, gas_bid)
            signed = sign_tx(tx)
            tip_wei = int(gas_bid["tip_usd"] / 3500 * 1e18)
            send_bundle(signed, w3.eth.block_number + 2, tip_wei)
            logging.info(f"EXECUTED: win={prob['win_probability']:.1%}")
        else:
            logging.info(f"SKIPPED: {prob['recommendation']}")
        
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
