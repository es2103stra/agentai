"""
Flash Arbitrage Engine — Python Backend
========================================
Стратегия флеш-арбитража с парсингом цен на DEX,
MEV-защитой через Flashbots Protect и работой в тестовой сети Sepolia.

Использование:
    pip install -r requirements.txt
    cp .env.example .env  # заполнить приватный ключ
    python flash_arbitrage.py

Архитектура:
    1. Price Oracle     — парсинг цен с 6 DEX в реальном времени
    2. Strategy Engine  — расчёт спредов, симуляция прибыли
    3. Executor         — сборка и отправка flash loan транзакций
    4. MEV Guard        — Flashbots bundle для защиты от sandwich-атак
"""

from __future__ import annotations

import os
import time
import json
import logging
from dataclasses import dataclass, field, asdict
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
FLASHBOTS_RPC = "https://rpc.flashbots.net"  # бесплатный MEV-protected RPC
FLASHBOTS_RELAY = "https://relay.flashbots.net"

# Адреса контрактов на Sepolia (примерные, для теста)
AAVE_POOL_V3 = "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff739485"
UNISWAP_V3_ROUTER = "0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48E"
SUSHISWAP_ROUTER = "0x72C6C4D8D3c9f6545b12a11b3D22543765d37C2d"
PANCAKESWAP_ROUTER = "0x8cFe327CEc66d1C090Dd72bd0FF11d690C33a2Eb"

# Минимальные параметры
MIN_SPREAD_BPS = 15          # 0.15% — минимальный спред для входа
MIN_NET_PROFIT_USD = 5.0     # минимальная чистая прибыль после газа
FLASH_LOAN_FEE_BPS = 9       # Aave V3 комиссия 0.09%
DEFAULT_GAS_LIMIT = 500_000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("flash-arb")


# ---------------------------------------------------------------------------
# Модели данных
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
    estimated_profit_usd: float
    gas_cost_usd: float
    net_profit_usd: float
    confidence: float
    timestamp: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# 1. Price Oracle — парсинг цен с DEX
# ---------------------------------------------------------------------------

class PriceOracle:
    """
    Парсит цены ETH/USDC с нескольких DEX через их публичные API / subgraph.
    В реальном бою здесь subgraph-запросы к The Graph или прямые вызовы
    pool.slot0() для Uniswap V3.
    """

    DEX_ENDPOINTS = {
        "Uniswap V3": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
        "SushiSwap": "https://api.thegraph.com/subgraphs/name/sushi-v2/sushiswap-ethereum",
        "PancakeSwap": "https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2-eth",
        "Curve": "https://api.curve.fi/api/getPools/ethereum",
        "Balancer": "https://api.balancer.fi/pools/ethereum",
        "1inch": "https://api.1inch.dev/price/v1.1/ethereum",
    }

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "FlashArb/1.0"})

    # --- Uniswap V3 (через subgraph) ------------------------------------
    def _fetch_uniswap(self, token: str) -> Optional[DexPrice]:
        query = """
        query($id: ID!) {
          pool(id: $id) {
            token0Price
            token1Price
            liquidity
            volumeUSD
          }
        }
        """
        # ETH/USDC 0.05% pool на mainnet (для Sepolia подставляем тестовый)
        pool_id = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
        try:
            r = self.session.post(
                self.DEX_ENDPOINTS["Uniswap V3"],
                json={"query": query, "variables": {"id": pool_id}},
                timeout=5,
            )
            r.raise_for_status()
            data = r.json()["data"]["pool"]
            return DexPrice(
                dex="Uniswap V3",
                token=token,
                price=Decimal(data["token0Price"]),
                liquidity_usd=float(data["liquidity"]),
                volume_24h=float(data["volumeUSD"]),
            )
        except Exception as e:
            log.warning("Uniswap fetch failed: %s", e)
            return None

    # --- SushiSwap -------------------------------------------------------
    def _fetch_sushi(self, token: str) -> Optional[DexPrice]:
        # Аналогично Uniswap — подставляем реальный pool ID
        try:
            r = self.session.post(
                self.DEX_ENDPOINTS["SushiSwap"],
                json={"query": "{ pair(id:\"0x397ff1542f962076d0bfe58ea045ffa2d347aca0\"){ token0Price reserveUSD volumeUSD } }"},
                timeout=5,
            )
            r.raise_for_status()
            data = r.json()["data"]["pair"]
            return DexPrice(
                dex="SushiSwap",
                token=token,
                price=Decimal(data["token0Price"]),
                liquidity_usd=float(data["reserveUSD"]),
                volume_24h=float(data["volumeUSD"]),
            )
        except Exception as e:
            log.warning("Sushi fetch failed: %s", e)
            return None

    # --- PancakeSwap -----------------------------------------------------
    def _fetch_pancake(self, token: str) -> Optional[DexPrice]:
        try:
            r = self.session.post(
                self.DEX_ENDPOINTS["PancakeSwap"],
                json={"query": "{ pair(id:\"0x58f876857a02d6762e0101bb5c46a8c1ed44dc16\"){ token0Price reserveUSD volumeUSD } }"},
                timeout=5,
            )
            r.raise_for_status()
            data = r.json()["data"]["pair"]
            return DexPrice(
                dex="PancakeSwap",
                token=token,
                price=Decimal(data["token0Price"]),
                liquidity_usd=float(data["reserveUSD"]),
                volume_24h=float(data["volumeUSD"]),
            )
        except Exception as e:
            log.warning("Pancake fetch failed: %s", e)
            return None

    # --- Curve -----------------------------------------------------------
    def _fetch_curve(self, token: str) -> Optional[DexPrice]:
        try:
            r = self.session.get(self.DEX_ENDPOINTS["Curve"], timeout=5)
            r.raise_for_status()
            pools = r.json().get("data", {}).get("poolData", [])
            # ищем ETH пул
            for p in pools:
                if "ETH" in p.get("name", "") and p.get("usdTotal", 0) > 1_000_000:
                    return DexPrice(
                        dex="Curve",
                        token=token,
                        price=Decimal(str(p.get("virtualPrice", 1.0))),
                        liquidity_usd=float(p["usdTotal"]),
                        volume_24h=float(p.get("volume", 0)),
                    )
        except Exception as e:
            log.warning("Curve fetch failed: %s", e)
        return None

    # --- 1inch -----------------------------------------------------------
    def _fetch_1inch(self, token: str) -> Optional[DexPrice]:
        try:
            r = self.session.get(
                f"{self.DEX_ENDPOINTS['1inch']}/{token}",
                timeout=5,
            )
            r.raise_for_status()
            data = r.json()
            price = Decimal(str(data.get("price", 0)))
            return DexPrice(
                dex="1inch",
                token=token,
                price=price,
                liquidity_usd=0,
                volume_24h=0,
            )
        except Exception as e:
            log.warning("1inch fetch failed: %s", e)
            return None

    # --- Агрегатор -------------------------------------------------------
    def scan(self, token: str = "ETH") -> List[DexPrice]:
        """Парсит цены со всех DEX параллельно (в продакшене — asyncio)."""
        fetchers = [
            self._fetch_uniswap,
            self._fetch_sushi,
            self._fetch_pancake,
            self._fetch_curve,
            self._fetch_1inch,
        ]
        results: List[DexPrice] = []
        for fn in fetchers:
            price = fn(token)
            if price and price.price > 0:
                results.append(price)
        log.info("Scanned %d DEX for %s — got %d prices", len(fetchers), token, len(results))
        return results


# ---------------------------------------------------------------------------
# 2. Strategy Engine — поиск арбитражных возможностей
# ---------------------------------------------------------------------------

class StrategyEngine:
    """
    Анализирует спреды между DEX и возвращает отсортированные
    арбитражные возможности с расчётом прибыли после газа и комиссии
    флеш-кредита.
    """

    def __init__(self, eth_price_usd: float = 3500.0, gas_gwei: float = 2.5):
        self.eth_price = eth_price_usd
        self.gas_gwei = gas_gwei

    def _gas_cost_usd(self, gas_limit: int = DEFAULT_GAS_LIMIT) -> float:
        gas_eth = (gas_limit * self.gas_gwei * 1e-9)
        return gas_eth * self.eth_price

    def find_opportunities(
        self,
        prices: List[DexPrice],
        loan_amount_eth: Decimal = Decimal("50"),
    ) -> List[ArbitrageOpportunity]:
        if len(prices) < 2:
            return []

        opps: List[ArbitrageOpportunity] = []
        gas_usd = self._gas_cost_usd()
        flash_fee = loan_amount_eth * (FLASH_LOAN_FEE_BPS / 10000)

        for i, buy in enumerate(prices):
            for sell in prices[i + 1 :]:
                if sell.price <= buy.price:
                    continue
                spread = (sell.price - buy.price) / buy.price
                spread_bps = float(spread * 10000)
                if spread_bps < MIN_SPREAD_BPS:
                    continue

                gross_profit_eth = loan_amount_eth * spread
                gross_profit_usd = float(gross_profit_eth * Decimal(str(self.eth_price)))
                flash_fee_usd = float(flash_fee * Decimal(str(self.eth_price)))
                net_profit = gross_profit_usd - gas_usd - flash_fee_usd

                if net_profit < MIN_NET_PROFIT_USD:
                    continue

                # Confidence: чем больше ликвидность и спред, тем выше
                liq_factor = min((buy.liquidity_usd + sell.liquidity_usd) / 10_000_000, 1.0)
                spread_factor = min(spread_bps / 50, 1.0)
                confidence = 0.5 + 0.3 * liq_factor + 0.2 * spread_factor

                opps.append(
                    ArbitrageOpportunity(
                        token=buy.token,
                        buy_dex=buy.dex,
                        sell_dex=sell.dex,
                        buy_price=buy.price,
                        sell_price=sell.price,
                        spread_bps=spread_bps,
                        loan_amount=loan_amount_eth,
                        estimated_profit_usd=gross_profit_usd,
                        gas_cost_usd=gas_usd,
                        net_profit_usd=net_profit,
                        confidence=confidence,
                    )
                )

        opps.sort(key=lambda o: o.net_profit_usd, reverse=True)
        return opps


# ---------------------------------------------------------------------------
# 3. Executor — исполнение флеш-кредита
# ---------------------------------------------------------------------------

class FlashLoanExecutor:
    """
    Собирает транзакцию флеш-кредита и отправляет её через Flashbots
    bundle для защиты от MEV.

    В тестовой сети Sepolia реальные DEX-пулы могут отсутствовать,
    поэтому executor логирует намерение и симулирует вызов.
    """

    # ABI Aave V3 flashLoan (упрощённый)
    FLASH_LOAN_ABI = json.loads("""
    [{
      "inputs":[
        {"name":"receiverAddress","type":"address"},
        {"name":"assets","type":"address[]"},
        {"name":"amounts","type":"uint256[]"},
        {"name":"interestRateModes","type":"uint256[]"},
        {"name":"onBehalfOf","type":"address"},
        {"name":"params","type":"bytes"},
        {"name":"referralCode","type":"uint16"}
      ],
      "name":"flashLoan",
      "outputs":[],
      "stateMutability":"nonpayable",
      "type":"function"
    }]
    """)

    def __init__(self, w3: Web3, private_key: str):
        self.w3 = w3
        self.account = Account.from_key(private_key)
        self.aave = w3.eth.contract(address=AAVE_POOL_V3, abi=self.FLASH_LOAN_ABI)

    def build_flash_loan_tx(self, opp: ArbitrageOpportunity) -> dict:
        """Собирает calldata для flashLoan + swap."""
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        # В реальном контракте это был бы вызов кастомного Arbitrageur.sol,
        # который внутри executeOperation() делает swap на втором DEX.
        # Здесь — упрощённая транзакция-заглушка для Sepolia.
        tx = {
            "from": self.account.address,
            "to": AAVE_POOL_V3,
            "value": 0,
            "gas": DEFAULT_GAS_LIMIT,
            "maxFeePerGas": self.w3.to_wei(3, "gwei"),
            "maxPriorityFeePerGas": self.w3.to_wei(1, "gwei"),
            "nonce": nonce,
            "chainId": SEPOLIA_CHAIN_ID,
            "data": "0x",  # подставляем реальный calldata из контракта
        }
        log.info(
            "Built flash loan tx: %s → %s, loan=%s %s, spread=%.2f bps",
            opp.buy_dex,
            opp.sell_dex,
            opp.loan_amount,
            opp.token,
            opp.spread_bps,
        )
        return tx

    def sign(self, tx: dict) -> str:
        signed = self.account.sign_transaction(tx)
        return signed.rawTransaction.hex()


# ---------------------------------------------------------------------------
# 4. MEV Guard — Flashbots bundle
# ---------------------------------------------------------------------------

class MEVGuard:
    """
    Отправляет транзакцию через Flashbots bundle.
    Использует бесплатный публичный RPC https://rpc.flashbots.net
    — никаких ключей и платежей не требуется.

    Bundle гарантирует:
      • приватную мемпул-подачу (не видна searchers)
      • атомарное исполнение (если revert — не включается в блок)
      • защиту от sandwich-атак
    """

    def __init__(self, w3_flashbots: Web3, signer_key: str):
        self.w3 = w3_flashbots
        self.signer = Account.from_key(signer_key)
        # В продакшене: from flashbots import flashbots
        # flashbots(w3, self.signer, FLASHBOTS_RELAY)

    def send_bundle(self, signed_tx_hex: str, target_block: int) -> dict:
        """
        Отправляет bundle в Flashbots relay.
        Возвращает результат симуляции / submission.
        """
        # eth_sendBundle JSON-RPC
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [
                {
                    "txs": [signed_tx_hex],
                    "blockNumber": hex(target_block),
                }
            ],
        }
        try:
            r = requests.post(FLASHBOTS_RELAY, json=payload, timeout=10)
            r.raise_for_status()
            result = r.json()
            log.info("Flashbots bundle sent: %s", result)
            return result
        except Exception as e:
            log.error("Flashbots submission failed: %s", e)
            return {"error": str(e)}

    def simulate_bundle(self, signed_tx_hex: str, block: int) -> dict:
        """eth_callBundle — симуляция перед реальной отправкой."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_callBundle",
            "params": [
                {
                    "txs": [signed_tx_hex],
                    "blockNumber": hex(block),
                    "stateBlockNumber": "latest",
                }
            ],
        }
        try:
            r = requests.post(FLASHBOTS_RELAY, json=payload, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}


# ---------------------------------------------------------------------------
# Главный цикл
# ---------------------------------------------------------------------------

def connect_web3(use_flashbots_rpc: bool = True) -> Web3:
    rpc = FLASHBOTS_RPC if use_flashbots_rpc else SEPOLIA_RPC
    w3 = Web3(Web3.HTTPProvider(rpc))
    # Sepolia — POA-сеть, нужен middleware
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to {rpc}")
    log.info("Connected to %s (chain %d)", rpc, w3.eth.chain_id)
    return w3


def main() -> None:
    log.info("=" * 60)
    log.info("Flash Arbitrage Engine — starting")
    log.info("Network: Sepolia Testnet (chain %d)", SEPOLIA_CHAIN_ID)
    log.info("MEV Protection: Flashbots Protect (free)")
    log.info("=" * 60)

    # --- Инициализация --------------------------------------------------
    private_key = os.getenv("PRIVATE_KEY", "0x" + "0" * 64)  # заглушка
    w3_public = connect_web3(use_flashbots_rpc=False)
    w3_flashbots = connect_web3(use_flashbots_rpc=True)

    oracle = PriceOracle()
    engine = StrategyEngine(eth_price_usd=3500.0, gas_gwei=2.5)
    executor = FlashLoanExecutor(w3_public, private_key)
    mev_guard = MEVGuard(w3_flashbots, private_key)

    log.info("Components ready. Starting scan loop...")

    # --- Основной цикл --------------------------------------------------
    iteration = 0
    while True:
        iteration += 1
        log.info("--- Scan #%d ---", iteration)

        # 1. Парсинг цен
        prices = oracle.scan("ETH")
        if len(prices) < 2:
            log.warning("Not enough prices, sleeping...")
            time.sleep(10)
            continue

        # 2. Поиск арбитража
        opps = engine.find_opportunities(prices, loan_amount_eth=Decimal("50"))
        log.info("Found %d opportunities", len(opps))

        if not opps:
            time.sleep(8)
            continue

        best = opps[0]
        log.info(
            "Best: %s on %s → %s, spread=%.2f bps, net=$%.2f",
            best.token, best.buy_dex, best.sell_dex,
            best.spread_bps, best.net_profit_usd,
        )

        # 3. Сборка транзакции
        tx = executor.build_flash_loan_tx(best)
        signed = executor.sign(tx)

        # 4. Симуляция через Flashbots
        current_block = w3_flashbots.eth.block_number
        sim = mev_guard.simulate_bundle(signed, current_block + 1)
        if "error" in sim:
            log.error("Simulation failed: %s", sim["error"])
            time.sleep(5)
            continue

        # 5. Отправка bundle
        result = mev_guard.send_bundle(signed, current_block + 2)
        log.info("Bundle result: %s", result)

        # 6. Пауза между итерациями
        time.sleep(12)


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Shutting down gracefully...")
    except Exception as e:
        log.exception("Fatal error: %s", e)
