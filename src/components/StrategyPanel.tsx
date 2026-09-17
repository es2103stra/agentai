import { FlashLoanStrategy } from '../types';
import { Play, Pause, TestTube, AlertCircle, Shield } from 'lucide-react';

interface Props {
  strategies: FlashLoanStrategy[];
  onToggle: (id: string) => void;
}

export default function StrategyPanel({ strategies, onToggle }: Props) {
  const statusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Play className="w-3 h-3 text-green-400" />;
      case 'paused': return <Pause className="w-3 h-3 text-yellow-400" />;
      case 'testing': return <TestTube className="w-3 h-3 text-blue-400" />;
      case 'error': return <AlertCircle className="w-3 h-3 text-red-400" />;
      default: return null;
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-500/10';
      case 'paused': return 'text-yellow-400 bg-yellow-500/10';
      case 'testing': return 'text-blue-400 bg-blue-500/10';
      case 'error': return 'text-red-400 bg-red-500/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Flash Loan Strategies</h3>
        </div>
        <span className="text-xs text-gray-500">{strategies.filter(s => s.status === 'active').length} active</span>
      </div>
      
      <div className="space-y-3">
        {strategies.map((strat) => (
          <div key={strat.id} className="bg-gray-800/50 border border-gray-700/30 rounded-lg p-4 hover:border-purple-500/30 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                {statusIcon(strat.status)}
                <span className="text-white font-medium text-sm">{strat.name}</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${statusColor(strat.status)}`}>
                {strat.status.toUpperCase()}
              </span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
              <div>
                <div className="text-xs text-gray-500">Protocol</div>
                <div className="text-sm text-white font-mono">{strat.protocol}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Executions</div>
                <div className="text-sm text-cyan-400 font-mono">{strat.totalExecutions}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Success Rate</div>
                <div className="text-sm text-green-400 font-mono">{strat.successRate}%</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Total Profit</div>
                <div className="text-sm text-green-400 font-mono">{strat.totalProfit} ETH</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {strat.mevProtection && (
                  <span className="flex items-center gap-1 text-xs text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded">
                    <Shield className="w-3 h-3" />
                    MEV Protected
                  </span>
                )}
                <span className="text-xs text-gray-500">
                  Last: {Math.floor((Date.now() - strat.lastExecution) / 60000)}m ago
                </span>
              </div>
              <button
                onClick={() => onToggle(strat.id)}
                className={`px-3 py-1.5 text-xs font-bold rounded transition-all hover:scale-105 ${
                  strat.status === 'active'
                    ? 'bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/30'
                    : 'bg-green-500/20 border border-green-500/30 text-green-400 hover:bg-green-500/30'
                }`}
              >
                {strat.status === 'active' ? 'Pause' : 'Start'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
