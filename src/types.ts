export interface Token {
  symbol: string;
  name: string;
  icon: string;
}

export interface DexPrice {
  dex: string;
  price: number;
  liquidity: number;
  volume24h: number;
  lastUpdate: number;
}

export interface ArbitrageOpportunity {
  id: string;
  token: string;
  buyDex: string;
  sellDex: string;
  buyPrice: number;
  sellPrice: number;
  spread: number;
  spreadPercent: number;
  estimatedProfit: number;
  gasCost: number;
  netProfit: number;
  confidence: number;
  timestamp: number;
}

export interface FlashLoanStrategy {
  id: string;
  name: string;
  protocol: string;
  status: 'active' | 'paused' | 'testing' | 'error';
  totalExecutions: number;
  successRate: number;
  totalProfit: number;
  lastExecution: number;
  mevProtection: boolean;
}

export interface NetworkStatus {
  network: string;
  chainId: number;
  blockNumber: number;
  gasPrice: number;
  isTestnet: boolean;
  rpcEndpoint: string;
  mevRpcEndpoint: string;
}

export interface MEVProtection {
  provider: string;
  status: 'active' | 'inactive' | 'degraded';
  protectedTxs: number;
  savedFromSandwich: number;
  totalSaved: number;
  rpcEndpoint: string;
}

export interface PriceHistory {
  timestamp: number;
  uniswap: number;
  sushiswap: number;
  pancakeswap: number;
  curve: number;
}
