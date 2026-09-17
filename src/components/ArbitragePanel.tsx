import { ArbitrageOpportunity } from '../types';
import { ArrowRight, Zap, DollarSign, TrendingUp } from 'lucide-react';

interface Props {
  opportunities: ArbitrageOpportunity[];
  onExecute: (id: string) => void;
}

export default function ArbitragePanel({ opportunities, onExecute }: Props) {
  return (
    <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Arbitrage Opportunities</h3>
        </div>
        <span className="text-xs text-gray-500">{opportunities.length} found</span>
      </div>
      
      <div className="space-y-3">
        {opportunities.map((opp) => (
          <div key={opp.id} className="bg-gray-800/50 border border-gray-700/30 rounded-lg p-4 hover:border-cyan-500/30 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-white">{opp.token}</span>
                <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400">
                  {opp.spreadPercent.toFixed(3)}% spread
                </span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></div>
                <span className="text-xs text-gray-400">
                  {Math.floor((Date.now() - opp.timestamp) / 1000)}s ago
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-2 mb-3">
              <div className="flex-1 bg-gray-900/50 rounded px-3 py-2">
                <div className="text-xs text-gray-500">Buy</div>
                <div className="text-sm text-white font-mono">{opp.buyDex}</div>
                <div className="text-xs text-green-400 font-mono">${opp.buyPrice.toFixed(2)}</div>
              </div>
              <ArrowRight className="w-4 h-4 text-cyan-400 flex-shrink-0" />
              <div className="flex-1 bg-gray-900/50 rounded px-3 py-2">
                <div className="text-xs text-gray-500">Sell</div>
                <div className="text-sm text-white font-mono">{opp.sellDex}</div>
                <div className="text-xs text-red-400 font-mono">${opp.sellPrice.toFixed(2)}</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <DollarSign className="w-3 h-3 text-green-400" />
                  <span className="text-xs text-gray-400">Net:</span>
                  <span className={`text-sm font-bold font-mono ${opp.netProfit > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${opp.netProfit.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Zap className="w-3 h-3 text-yellow-400" />
                  <span className="text-xs text-gray-400">Gas:</span>
                  <span className="text-xs text-yellow-400 font-mono">${opp.gasCost.toFixed(2)}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-xs text-gray-400">
                  Confidence: <span className={`font-bold ${opp.confidence > 85 ? 'text-green-400' : opp.confidence > 70 ? 'text-yellow-400' : 'text-red-400'}`}>{opp.confidence}%</span>
                </div>
                <button
                  onClick={() => onExecute(opp.id)}
                  className="px-3 py-1.5 bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 text-cyan-400 text-xs font-bold rounded transition-all hover:scale-105"
                >
                  Execute
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
