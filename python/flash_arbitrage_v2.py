"""
Flash Arbitrage Engine v2.0
============================
Добавлено:
  • Gas Price Escalation — динамическое повышение priority fee
  • Flashbots Tip Bidding — аукцион за позицию в блоке
  • Probability Engine — расчёт шанса успеха
  • Competitor Analysis — оценка конкуренции в mempool
"""

from __future__ import annotations

import os
import time
import json
import math
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime

import requests
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account

# ---------------------------------------------------------------------------
# Конфигурация
# ---------------------------------------------------------------------------

SEPOLIA_CHAIN_ID = 11155111
SEPOLIA_RPC = "https://rpc.sepolia.org"
FLASHBOTS_RPC = "https://rpc.flashbots.net"
FLASHBOTS_RELAY = "https://relay.flashbots.net"

AAVE_POOL_V3 = "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff739485"

# ─── Параметры стратегии ─────────────────────────────────────────
MIN_SPREAD_BPS = 15
MIN_NET_PROFIT_USD = 5.0
FLASH_LOAN_FEE_BPS = 9
DEFAULT_GAS_LIMIT = 500_000

# ─── Gas Bidding & MEV ───────────────────────────────────────────
BASE_PRIORITY_FEE_GWEI = 1.0          # базовый priority fee
MAX_PRIORITY_FEE_GWEI = 50.0          # максимум — не разоряемся
GAS_ESCALATION_STEP = 1.5             # множитель повышения при конкуренции
FLASHBOTS_TIP_PERCENT = 0.5           # % от прибыли отдаём валидатору (tip)
MAX_TIP_PERCENT = 5.0                 # максимум tip в аукционе
COMPETITION_THRESHOLD = 0.3           # если шанс успеха < 30% — не входим

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("flash-arb-v2")


# ---------------------------------------------------------------------------
# Модели
# ---------------------------------------------------------------------------

@dataclass
class DexPrice:
    dex: str
    token: str
    price: Decimal
    liquidity_usd: float
    volume_24h: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class ArbitrageOpportunity:
    token: str
    buy_dex: str
    sell_dex: str
    buy_price: Decimal
    sell_price: Decimal
    spread_bps: float
    loan_amount: Decimal
    gross_profit_usd: float
    gas_cost_usd: float
    flash_fee_usd: float
    net_profit_usd: float
    confidence: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class GasBid:
    """Ставка за включение в блок."""
    base_fee_gwei: float
    priority_fee_gwei: float
    flashbots_tip_usd: float
    flashbots_tip_percent: float
    total_gas_cost_usd: float
    escalation_level: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class SuccessProbability:
    """Анализ вероятности успеха."""
    win_probability: float              # 0.0 — 1.0
    expected_value_usd: float           # математическое ожидание прибыли
    competitor_count: int               # оценка числа конкурентов
    latency_ms: float                   # наша латентность до relay
    gas_bid_rank: int                   # позиция в аукционе (1 = первая)
    recommendation: str                 # EXECUTE / SKIP / WAIT
    factors: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. Gas Escalation Engine
# ---------------------------------------------------------------------------

class GasEscalationEngine:
    """
    Динамически повышает priority fee чтобы транзакция была первой.
    
    Логика:
      1. Начинаем с базового priority fee (1 gwei)
      2. Если обнаруживаем конкуренцию — повышаем на GAS_ESCALATION_STEP
      3. Ограничиваем MAX_PRIORITY_FEE_GWEI чтобы не уйти в минус
      4. Flashbots tip = % от прибыли (аукцион за блок-позицию)
    """

    def __init__(
        self,
        w3: Web3,
        base_fee: float = BASE_PRIORITY_FEE_GWEI,
        max_fee: float = MAX_PRIORITY_FEE_GWEI,
        escalation_step: float = GAS_ESCALATION_STEP,
    ):
        self.w3 = w3
        self.base_fee = base_fee
        self.max_fee = max_fee
        self.escalation_step = escalation_step
        self.current_level = 0

    def get_base_fee(self) -> float:
        """Получает текущий base fee из последнего блока."""
        try:
            block = self.w3.eth.get_block("latest")
            base_fee = self.w3.from_wei(block.get("baseFeePerGas", 0), "gwei")
            return float(base_fee)
        except Exception:
            return 1.0  # дефолт для Sepolia

    def calculate_bid(
        self,
        net_profit_usd: float,
        eth_price_usd: float = 3500.0,
        competition_level: float = 0.0,
    ) -> GasBid:
        """
        Рассчитывает оптимальную ставку за блок-позицию.
        
        competition_level: 0.0 (нет конкурентов) — 1.0 (максимальная конкуренция)
        """
        base_fee = self.get_base_fee()
        
        # ─── Priority Fee Escalation ────────────────────────────
        # Чем выше конкуренция, тем больше повышаем fee
        escalation_multiplier = 1.0 + (competition_level * 3.0)
        priority_fee = self.base_fee * escalation_multiplier
        
        # Ограничиваем максимумом
        priority_fee = min(priority_fee, self.max_fee)
        
        # ─── Flashbots Tip (аукцион за позицию) ─────────────────
        # Tip валидатору = % от прибыли (конкурируем с другими ботами)
        tip_percent = FLASHBOTS_TIP_PERCENT
        if competition_level > 0.5:
            # Высокая конкуренция — повышаем tip
            tip_percent = min(
                FLASHBOTS_TIP_PERCENT * (1 + competition_level * 2),
                MAX_TIP_PERCENT
            )
        
        tip_usd = net_profit_usd * (tip_percent / 100)
        
        # ─── Total Gas Cost ─────────────────────────────────────
        gas_eth = (DEFAULT_GAS_LIMIT * (base_fee + priority_fee) * 1e-9)
        gas_usd = gas_eth * eth_price_usd
        total_cost = gas_usd + tip_usd
        
        self.current_level = int(competition_level * 10)
        
        bid = GasBid(
            base_fee_gwei=base_fee,
            priority_fee_gwei=priority_fee,
            flashbots_tip_usd=tip_usd,
            flashbots_tip_percent=tip_percent,
            total_gas_cost_usd=total_cost,
            escalation_level=self.current_level,
        )
        
        log.info(
            "Gas bid: base=%.2f priority=%.2f tip=$%.2f (%.1f%%) total=$%.2f [level=%d]",
            base_fee, priority_fee, tip_usd, tip_percent, total_cost, self.current_level
        )
        
        return bid


# ---------------------------------------------------------------------------
# 2. Probability Engine — расчёт шанса успеха
# ---------------------------------------------------------------------------

class ProbabilityEngine:
    """
    Оценивает вероятность того, что наша транзакция будет первой
    и успешно исполнится.
    
    Факторы:
      • Латентность до Flashbots relay
      • Размер tip (чем больше — тем выше позиция)
      • Число конкурентов (оценивается по активности в mempool)
      • Ликвидность пулов (достаточно ли для исполнения)
      • Спред (больше спред = больше конкурентов)
    """

    def __init__(self, w3: Web3):
        self.w3 = w3
        self.latency_ms = self._measure_latency()
        self.competitor_estimate = 0

    def _measure_latency(self) -> float:
        """Измеряет латентность до Flashbots relay."""
        try:
            start = time.time()
            requests.post(FLASHBOTS_RELAY, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "id": 1}, timeout=5)
            latency = (time.time() - start) * 1000
            return latency
        except Exception:
            return 500.0  # дефолт если relay недоступен

    def estimate_competitors(self, spread_bps: float) -> int:
        """
        Оценивает число конкурентов на основе спреда.
        Эмпирическая формула: чем больше спред, тем больше ботов его видят.
        """
        # На mainnet: ~5-20 ботов на спред > 30 bps
        # На Sepolia: ~0-2 бота (тестнет)
        if self.w3.eth.chain_id == SEPOLIA_CHAIN_ID:
            return max(0, int(spread_bps / 50))  # на тестнете мало конкурентов
        
        # Mainnet оценка
        base_competitors = 3
        spread_factor = max(0, (spread_bps - 10) / 5)
        return int(base_competitors + spread_factor)

    def calculate_probability(
        self,
        opp: ArbitrageOpportunity,
        gas_bid: GasBid,
        eth_price_usd: float = 3500.0,
    ) -> SuccessProbability:
        """
        Рассчитывает вероятность успеха и математическое ожидание.
        """
        competitors = self.estimate_competitors(opp.spread_bps)
        self.competitor_estimate = competitors
        
        # ─── Фактор 1: Латентность ──────────────────────────────
        # Чем ниже латентность, тем выше шанс быть первым
        latency_factor = max(0, 1.0 - (self.latency_ms / 1000))
        
        # ─── Фактор 2: Tip аукцион ──────────────────────────────
        # Если наш tip больше чем у конкурентов — мы первые
        # Предполагаем что конкуренты предлагают 1-3% от прибыли
        avg_competitor_tip_percent = 2.0
        our_tip_advantage = gas_bid.flashbots_tip_percent / max(avg_competitor_tip_percent, 0.1)
        tip_factor = min(our_tip_advantage / (competitors + 1), 1.0)
        
        # ─── Фактор 3: Приорити фи ──────────────────────────────
        # Higher priority fee = выше шанс inclusion
        priority_factor = min(gas_bid.priority_fee_gwei / 10.0, 1.0)
        
        # ─── Фактор 4: Ликвидность ──────────────────────────────
        # Достаточно ли ликвидности для нашего объёма
        liq_factor = min(opp.loan_amount * Decimal(str(eth_price_usd)) / Decimal("1000000"), 1.0)
        
        # ─── Итоговая вероятность ───────────────────────────────
        # Взвешенная сумма факторов
        win_prob = (
            0.30 * latency_factor +
            0.35 * tip_factor +
            0.20 * priority_factor +
            0.15 * float(liq_factor)
        )
        
        # Корректировка на число конкурентов
        if competitors > 0:
            win_prob *= (1.0 / (1.0 + competitors * 0.3))
        
        win_prob = max(0.0, min(1.0, win_prob))
        
        # ─── Expected Value ─────────────────────────────────────
        expected_value = (win_prob * opp.net_profit_usd) - ((1 - win_prob) * gas_bid.total_gas_cost_usd)
        
        # ─── Recommendation ─────────────────────────────────────
        if win_prob < COMPETITION_THRESHOLD:
            recommendation = "SKIP"
        elif expected_value < 0:
            recommendation = "WAIT"
        else:
            recommendation = "EXECUTE"
        
        factors = {
            "latency": latency_factor,
            "tip_advantage": tip_factor,
            "priority_fee": priority_factor,
            "liquidity": float(liq_factor),
            "competitors": competitors,
        }
        
        prob = SuccessProbability(
            win_probability=win_prob,
            expected_value_usd=expected_value,
            competitor_count=competitors,
            latency_ms=self.latency_ms,
            gas_bid_rank=1 if tip_factor > 0.7 else 2 if tip_factor > 0.4 else 3,
            recommendation=recommendation,
            factors=factors,
        )
        
        log.info(
            "Probability: win=%.1f%% EV=$%.2f competitors=%d latency=%.0fms → %s",
            win_prob * 100, expected_value, competitors, self.latency_ms, recommendation
        )
        
        return prob


# ---------------------------------------------------------------------------
# 3. Price Oracle (сокращённая версия)
# ---------------------------------------------------------------------------

class PriceOracle:
    """Парсит цены с DEX."""
    
    def scan(self, token="ETH") -> List[DexPrice]:
        # В реальности — запросы к The Graph / DEX API
        # Здесь — заглушка для демонстрации
        return []


# ---------------------------------------------------------------------------
# 4. Strategy Engine (с Gas Bidding)
# ---------------------------------------------------------------------------

class StrategyEngine:
    """Стратегия с учётом gas bidding и вероятности успеха."""

    def __init__(self, w3: Web3, eth_price_usd: float = 3500.0):
        self.w3 = w3
        self.eth_price = eth_price_usd
        self.gas_engine = GasEscalationEngine(w3)
        self.prob_engine = ProbabilityEngine(w3)

    def evaluate_opportunity(self, opp: ArbitrageOpportunity) -> Tuple[GasBid, SuccessProbability]:
        """
        Полный цикл оценки: gas bid → probability → решение.
        """
        # 1. Оцениваем конкуренцию
        competition_level = min(opp.spread_bps / 100, 1.0)
        
        # 2. Рассчитываем gas bid
        gas_bid = self.gas_engine.calculate_bid(
            net_profit_usd=opp.net_profit_usd,
            eth_price_usd=self.eth_price,
            competition_level=competition_level,
        )
        
        # 3. Пересчитываем net profit с учётом gas bid
        adjusted_net = opp.net_profit_usd - gas_bid.total_gas_cost_usd
        
        # 4. Рассчитываем вероятность
        prob = self.prob_engine.calculate_probability(opp, gas_bid, self.eth_price)
        
        return gas_bid, prob

    def should_execute(self, prob: SuccessProbability) -> bool:
        """Финальное решение: исполнять или нет."""
        return (
            prob.recommendation == "EXECUTE" and
            prob.win_probability >= COMPETITION_THRESHOLD and
            prob.expected_value_usd > 0
        )


# ---------------------------------------------------------------------------
# 5. MEV Guard (с tip bidding)
# ---------------------------------------------------------------------------

class MEVGuard:
    """Flashbots bundle с динамическим tip."""

    def __init__(self, w3: Web3, signer_key: str):
        self.w3 = w3
        self.signer = Account.from_key(signer_key)

    def send_bundle(self, signed_tx_hex: str, target_block: int, tip_wei: int) -> dict:
        """
        Отправляет bundle с указанным tip для валидатора.
        Tip включается в последнюю транзакцию bundle (или отдельной tx).
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": [signed_tx_hex],
                "blockNumber": hex(target_block),
                # В реальном Flashbots SDK tip указывается через
                # отдельную транзакцию на coinbase валидатора
            }]
        }
        try:
            r = requests.post(FLASHBOTS_RELAY, json=payload, timeout=10)
            r.raise_for_status()
            result = r.json()
            log.info("Bundle sent to block %d with tip %d wei", target_block, tip_wei)
            return result
        except Exception as e:
            log.error("Bundle submission failed: %s", e)
            return {"error": str(e)}


# ---------------------------------------------------------------------------
# 6. Главный цикл (v2.0)
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("=" * 70)
    log.info("Flash Arbitrage Engine v2.0 — with Gas Escalation & MEV Bidding")
    log.info("Network: Sepolia Testnet (chain %d)", SEPOLIA_CHAIN_ID)
    log.info("MEV: Flashbots Protect + Tip Auction")
    log.info("=" * 70)

    private_key = os.getenv("PRIVATE_KEY", "0x" + "0" * 64)
    w3 = Web3(Web3.HTTPProvider(FLASHBOTS_RPC))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    oracle = PriceOracle()
    engine = StrategyEngine(w3, eth_price_usd=3500.0)
    mev = MEVGuard(w3, private_key)

    log.info("Ready. Starting scan loop with gas escalation...")

    iteration = 0
    while True:
        iteration += 1
        log.info("\n--- Scan #%d ---", iteration)

        prices = oracle.scan("ETH")
        if not prices:
            time.sleep(10)
            continue

        # Находим лучшую возможность
        # (в реальности — engine.find_opportunities)
        # opp = ...

        # Оцениваем gas bid и вероятность
        # gas_bid, prob = engine.evaluate_opportunity(opp)

        # if engine.should_execute(prob):
        #     tx = build_tx(opp, gas_bid)
        #     signed = sign_tx(tx)
        #     tip_wei = int(gas_bid.flashbots_tip_usd / 3500 * 1e18)
        #     mev.send_bundle(signed, w3.eth.block_number + 2, tip_wei)

        time.sleep(12)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Shutting down...")
    except Exception as e:
        log.exception("Fatal: %s", e)
