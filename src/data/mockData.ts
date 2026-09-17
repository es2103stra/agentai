import { ArbitrageOpportunity, FlashLoanStrategy, NetworkStatus, MEVProtection, PriceHistory, DexPrice } from '../types';

export const tokens = [
  { symbol: 'ETH', name: 'Ethereum', icon: '⟠' },
  { symbol: 'WBTC', name: 'Wrapped Bitcoin', icon: '₿' },
  { symbol: 'USDC', name: 'USD Coin', icon: '$' },
  { symbol: 'DAI', name: 'Dai', icon: '◈' },
  { symbol: 'LINK', name: 'Chainlink', icon: '⬡' },
  { symbol: 'UNI', name: 'Uniswap', icon: '🦄' },
];

export const dexes = ['Uniswap V3', 'SushiSwap', 'PancakeSwap', 'Curve', 'Balancer', '1inch'];

export function generateDexPrices(token: string): DexPrice[] {
  const basePrice = token === 'ETH' ? 3450 : token === 'WBTC' ? 67500 : token === 'LINK' ? 18.5 : token === 'UNI' ? 12.3 : 1.0;
  
  return dexes.slice(0, 4).map(dex => ({
    dex,
    price: basePrice * (1 + (Math.random() - 0.5) * 0.008),
    liquidity: Math.floor(Math.random() * 50000000) + 5000000,
    volume24h: Math.floor(Math.random() * 100000000) + 10000000,
    lastUpdate: Date.now() - Math.floor(Math.random() * 5000),
  }));
}

export function generateArbitrageOpportunities(): ArbitrageOpportunity[] {
  const opportunities: ArbitrageOpportunity[] = [];
  const tokenPairs = ['ETH', 'WBTC', 'LINK', 'UNI', 'DAI'];
  
  tokenPairs.forEach((token, i) => {
    const buyDex = dexes[Math.floor(Math.random() * dexes.length)];
    let sellDex = dexes[Math.floor(Math.random() * dexes.length)];
    while (sellDex === buyDex) sellDex = dexes[Math.floor(Math.random() * dexes.length)];
    
    const basePrice = token === 'ETH' ? 3450 : token === 'WBTC' ? 67500 : token === 'LINK' ? 18.5 : token === 'UNI' ? 12.3 : 1.0;
    const spread = Math.random() * 0.005 + 0.001;
    const buyPrice = basePrice * (1 - spread / 2);
    const sellPrice = basePrice * (1 + spread / 2);
    const loanAmount = token === 'WBTC' ? 1 : token === 'ETH' ? 50 : 10000;
    const estimatedProfit = loanAmount * spread * basePrice;
    const gasCost = 0.003 * 3450;
    
    opportunities.push({
      id: `arb-${i}-${Date.now()}`,
      token,
      buyDex,
      sellDex,
      buyPrice,
      sellPrice,
      spread,
      spreadPercent: spread * 100,
      estimatedProfit,
      gasCost,
      netProfit: estimatedProfit - gasCost,
      confidence: Math.floor(Math.random() * 30) + 70,
      timestamp: Date.now() - Math.floor(Math.random() * 30000),
    });
  });
  
  return opportunities.sort((a, b) => b.netProfit - a.netProfit);
}

export const flashLoanStrategies: FlashLoanStrategy[] = [
  {
    id: 'strat-1',
    name: 'ETH Cross-DEX Arbitrage',
    protocol: 'Aave V3',
    status: 'testing',
    totalExecutions: 47,
    successRate: 91.5,
    totalProfit: 2.34,
    lastExecution: Date.now() - 120000,
    mevProtection: true,
  },
  {
    id: 'strat-2',
    name: 'Stablecoin Triangular',
    protocol: 'dYdX',
    status: 'active',
    totalExecutions: 128,
    successRate: 96.1,
    totalProfit: 5.67,
    lastExecution: Date.now() - 45000,
    mevProtection: true,
  },
  {
    id: 'strat-3',
    name: 'WBTC Price Convergence',
    protocol: 'Aave V3',
    status: 'paused',
    totalExecutions: 23,
    successRate: 87.0,
    totalProfit: 1.12,
    lastExecution: Date.now() - 3600000,
    mevProtection: true,
  },
  {
    id: 'strat-4',
    name: 'LINK Liquidity Sweep',
    protocol: 'MakerDAO',
    status: 'active',
    totalExecutions: 89,
    successRate: 93.3,
    totalProfit: 3.89,
    lastExecution: Date.now() - 180000,
    mevProtection: true,
  },
];

export const networkStatus: NetworkStatus = {
  network: 'Sepolia Testnet',
  chainId: 11155111,
  blockNumber: 5847291,
  gasPrice: 2.5,
  isTestnet: true,
  rpcEndpoint: 'https://rpc.sepolia.org',
  mevRpcEndpoint: 'https://rpc.flashbots.net',
};

export const mevProtection: MEVProtection = {
  provider: 'Flashbots Protect',
  status: 'active',
  protectedTxs: 156,
  savedFromSandwich: 23,
  totalSaved: 0.847,
  rpcEndpoint: 'https://rpc.flashbots.net',
};

export function generatePriceHistory(): PriceHistory[] {
  const history: PriceHistory[] = [];
  const baseEth = 3450;
  
  for (let i = 60; i >= 0; i--) {
    const timestamp = Date.now() - i * 60000;
    const drift = Math.sin(i / 10) * 5;
    history.push({
      timestamp,
      uniswap: baseEth + drift + (Math.random() - 0.5) * 3,
      sushiswap: baseEth + drift + 2 + (Math.random() - 0.5) * 4,
      pancakeswap: baseEth + drift - 1.5 + (Math.random() - 0.5) * 3,
      curve: baseEth + drift + 0.5 + (Math.random() - 0.5) * 2,
    });
  }
  
  return history;
}
