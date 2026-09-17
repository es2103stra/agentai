import { useState, useEffect, useCallback } from 'react';
import { 
  Shield, Zap, TrendingUp, Activity, 
  GitBranch, AlertTriangle, ChevronDown, ChevronUp,
  Wifi, WifiOff
} from 'lucide-react';
import NetworkPanel from './components/NetworkPanel';
import ArbitragePanel from './components/ArbitragePanel';
import StrategyPanel from './components/StrategyPanel';
import PriceChart from './components/PriceChart';
import FlashLoanSimulator from './components/FlashLoanSimulator';
import PriceScanner from './components/PriceScanner';
import { 
  generateArbitrageOpportunities, 
  flashLoanStrategies as initialStrategies,
  networkStatus,
  mevProtection,
  generatePriceHistory,
} from './data/mockData';
import { ArbitrageOpportunity, FlashLoanStrategy, PriceHistory } from './types';

function App() {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [strategies, setStrategies] = useState<FlashLoanStrategy[]>(initialStrategies);
  const [priceHistory, setPriceHistory] = useState<PriceHistory[]>([]);
  const [showStrategy, setShowStrategy] = useState(true);
  const [showSimulator, setShowSimulator] = useState(true);
  const [notifications, setNotifications] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(true);

  const addNotification = useCallback((msg: string) => {
    setNotifications(prev => [msg, ...prev].slice(0, 5));
  }, []);

  useEffect(() => {
    setOpportunities(generateArbitrageOpportunities());
    setPriceHistory(generatePriceHistory());
    
    const oppInterval = setInterval(() => {
      setOpportunities(generateArbitrageOpportunities());
    }, 8000);

    const priceInterval = setInterval(() => {
      setPriceHistory(generatePriceHistory());
    }, 15000);

    return () => {
      clearInterval(oppInterval);
      clearInterval(priceInterval);
    };
  }, []);

  const handleExecute = (id: string) => {
    const opp = opportunities.find(o => o.id === id);
    if (opp) {
      addNotification(`⚡ Executing ${opp.token} arbitrage: ${opp.buyDex} → ${opp.sellDex} (est. profit: $${opp.netProfit.toFixed(2)})`);
      setTimeout(() => {
        addNotification(`✅ ${opp.token} arbitrage completed via Flashbots bundle. Protected from MEV.`);
      }, 2000);
    }
  };

  const handleToggleStrategy = (id: string) => {
    setStrategies(prev => prev.map(s => {
      if (s.id === id) {
        const newStatus = s.status === 'active' ? 'paused' : 'active';
        addNotification(`${newStatus === 'active' ? '▶️' : '⏸️'} Strategy "${s.name}" ${newStatus}`);
        return { ...s, status: newStatus as FlashLoanStrategy['status'] };
      }
      return s;
    }));
  };

  const totalProfit = strategies.reduce((sum, s) => sum + s.totalProfit, 0);
  const totalExecutions = strategies.reduce((sum, s) => sum + s.totalExecutions, 0);
  const avgSuccessRate = strategies.reduce((sum, s) => sum + s.successRate, 0) / strategies.length;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 pointer-events-none" />
      <div className="fixed inset-0 opacity-30 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-gray-800/50 backdrop-blur-xl bg-gray-950/80 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <div className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-gray-950 animate-pulse" />
                </div>
                <div>
                  <h1 className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                    Flash Arbitrage
                  </h1>
                  <p className="text-xs text-gray-500">DeFi Flash Loan Strategy Engine</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                {/* Stats */}
                <div className="hidden md:flex items-center gap-6">
                  <div className="text-center">
                    <div className="text-xs text-gray-500">Total Profit</div>
                    <div className="text-sm font-bold text-green-400 font-mono">{totalProfit.toFixed(2)} ETH</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-gray-500">Executions</div>
                    <div className="text-sm font-bold text-cyan-400 font-mono">{totalExecutions}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-gray-500">Success Rate</div>
                    <div className="text-sm font-bold text-purple-400 font-mono">{avgSuccessRate.toFixed(1)}%</div>
                  </div>
                </div>

                {/* Connection status */}
                <button
                  onClick={() => setIsConnected(!isConnected)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                    isConnected 
                      ? 'bg-green-500/10 border-green-500/30 text-green-400' 
                      : 'bg-red-500/10 border-red-500/30 text-red-400'
                  }`}
                >
                  {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                  {isConnected ? 'Connected' : 'Disconnected'}
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
          {/* Top Stats Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <span className="text-xs text-gray-400">Active Opportunities</span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">{opportunities.length}</div>
              <div className="text-xs text-green-400 mt-1">↑ Real-time scanning</div>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-1">
                <Shield className="w-4 h-4 text-purple-400" />
                <span className="text-xs text-gray-400">MEV Protected</span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">{mevProtection.protectedTxs}</div>
              <div className="text-xs text-purple-400 mt-1">Flashbots RPC active</div>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="w-4 h-4 text-green-400" />
                <span className="text-xs text-gray-400">Avg Spread</span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">
                {(opportunities.reduce((s, o) => s + o.spreadPercent, 0) / opportunities.length).toFixed(3)}%
              </div>
              <div className="text-xs text-yellow-400 mt-1">Across {opportunities.length} pairs</div>
            </div>
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-1">
                <GitBranch className="w-4 h-4 text-orange-400" />
                <span className="text-xs text-gray-400">Testnet</span>
              </div>
              <div className="text-2xl font-bold text-white font-mono">Sepolia</div>
              <div className="text-xs text-orange-400 mt-1">Chain ID: 11155111</div>
            </div>
          </div>

          {/* Price Chart */}
          <PriceChart data={priceHistory} />

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Arbitrage Opportunities */}
            <ArbitragePanel opportunities={opportunities} onExecute={handleExecute} />
            
            {/* Price Scanner */}
            <PriceScanner />
          </div>

          {/* Network & MEV */}
          <NetworkPanel network={networkStatus} mev={mevProtection} />

          {/* Strategies Section */}
          <div className="bg-gray-900/30 border border-gray-700/30 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowStrategy(!showStrategy)}
              className="w-full flex items-center justify-between p-5 hover:bg-gray-800/30 transition-all"
            >
              <div className="flex items-center gap-2">
                <GitBranch className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Strategy Management</h3>
              </div>
              {showStrategy ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
            </button>
            {showStrategy && (
              <div className="px-5 pb-5">
                <StrategyPanel strategies={strategies} onToggle={handleToggleStrategy} />
              </div>
            )}
          </div>

          {/* Flash Loan Simulator */}
          <div className="bg-gray-900/30 border border-gray-700/30 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowSimulator(!showSimulator)}
              className="w-full flex items-center justify-between p-5 hover:bg-gray-800/30 transition-all"
            >
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Flash Loan Transaction Simulator</h3>
              </div>
              {showSimulator ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
            </button>
            {showSimulator && (
              <div className="px-5 pb-5">
                <FlashLoanSimulator />
              </div>
            )}
          </div>

          {/* Notifications */}
          {notifications.length > 0 && (
            <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4 text-yellow-400" />
                <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Activity Log</h3>
              </div>
              <div className="space-y-2">
                {notifications.map((notif, idx) => (
                  <div key={idx} className="text-xs text-gray-400 bg-gray-800/30 rounded px-3 py-2 font-mono">
                    {notif}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Architecture Info */}
          <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">System Architecture</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/30">
                <div className="text-cyan-400 font-bold text-sm mb-2">1. Price Oracle</div>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Real-time price feeds from 6 DEXes</li>
                  <li>• Cross-chain price aggregation</li>
                  <li>• Spread detection & ranking</li>
                  <li>• Liquidity depth analysis</li>
                </ul>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/30">
                <div className="text-purple-400 font-bold text-sm mb-2">2. MEV Protection</div>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Flashbots Protect RPC (free)</li>
                  <li>• Private transaction submission</li>
                  <li>• Sandwich attack prevention</li>
                  <li>• Bundle simulation & validation</li>
                </ul>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/30">
                <div className="text-green-400 font-bold text-sm mb-2">3. Flash Loan Execution</div>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Aave V3 / dYdX / MakerDAO</li>
                  <li>• Atomic multi-step transactions</li>
                  <li>• Testnet (Sepolia) deployment</li>
                  <li>• Gas optimization & routing</li>
                </ul>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800/50 mt-8">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <span>Flash Arbitrage Engine v0.1.0 — Testnet Mode</span>
              <span>MEV Protection: Flashbots Protect | Network: Sepolia</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
