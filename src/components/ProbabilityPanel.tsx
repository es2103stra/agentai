import { useState, useEffect } from 'react';
import { Target, Zap, TrendingUp, AlertTriangle, DollarSign, Clock, Users, BarChart3 } from 'lucide-react';

interface SuccessFactor {
  name: string;
  value: number; // 0-1
  weight: number;
  color: string;
}

interface GasBid {
  baseFee: number;
  priorityFee: number;
  tipUSD: number;
  tipPercent: number;
  totalCost: number;
  escalationLevel: number;
}

interface ProbabilityResult {
  winProbability: number;
  expectedValue: number;
  competitors: number;
  latency: number;
  gasBidRank: number;
  recommendation: 'EXECUTE' | 'SKIP' | 'WAIT';
  factors: SuccessFactor[];
  gasBid: GasBid;
}

export default function ProbabilityPanel() {
  const [spread, setSpread] = useState(25); // bps
  const [liquidity, setLiquidity] = useState(5); // millions
  const [result, setResult] = useState<ProbabilityResult | null>(null);

  useEffect(() => {
    calculateProbability();
  }, [spread, liquidity]);

  const calculateProbability = () => {
    // Эмпирическая модель вероятности успеха
    const competitors = Math.max(0, Math.floor((spread - 10) / 5));
    const latency = 150 + Math.random() * 100; // ms
    
    // Факторы
    const latencyFactor = Math.max(0, 1 - latency / 1000);
    const competitionLevel = Math.min(spread / 100, 1);
    
    // Gas escalation
    const baseFee = 1.0 + Math.random() * 2;
    const priorityFee = 1.0 * (1 + competitionLevel * 3);
    const tipPercent = 0.5 * (1 + competitionLevel * 2);
    const grossProfit = spread * 0.01 * 50 * 3500; // 50 ETH loan
    const tipUSD = grossProfit * (tipPercent / 100);
    const gasUSD = (500000 * (baseFee + priorityFee) * 1e-9) * 3500;
    const totalCost = gasUSD + tipUSD;
    
    // Tip advantage
    const avgCompetitorTip = 2.0;
    const tipAdvantage = Math.min(tipPercent / avgCompetitorTip / (competitors + 1), 1);
    const priorityFactor = Math.min(priorityFee / 10, 1);
    const liqFactor = Math.min(liquidity / 1, 1);
    
    // Win probability
    let winProb = 0.30 * latencyFactor + 0.35 * tipAdvantage + 0.20 * priorityFactor + 0.15 * liqFactor;
    if (competitors > 0) {
      winProb *= 1 / (1 + competitors * 0.3);
    }
    winProb = Math.max(0, Math.min(1, winProb));
    
    const netProfit = grossProfit - totalCost;
    const expectedValue = winProb * netProfit - (1 - winProb) * totalCost;
    
    const recommendation: 'EXECUTE' | 'SKIP' | 'WAIT' = 
      winProb < 0.3 ? 'SKIP' : expectedValue < 0 ? 'WAIT' : 'EXECUTE';
    
    const factors: SuccessFactor[] = [
      { name: 'Latency', value: latencyFactor, weight: 0.30, color: 'cyan' },
      { name: 'Tip Advantage', value: tipAdvantage, weight: 0.35, color: 'purple' },
      { name: 'Priority Fee', value: priorityFactor, weight: 0.20, color: 'yellow' },
      { name: 'Liquidity', value: liqFactor, weight: 0.15, color: 'green' },
    ];
    
    setResult({
      winProbability: winProb,
      expectedValue,
      competitors,
      latency,
      gasBidRank: tipAdvantage > 0.7 ? 1 : tipAdvantage > 0.4 ? 2 : 3,
      recommendation,
      factors,
      gasBid: {
        baseFee,
        priorityFee,
        tipUSD,
        tipPercent,
        totalCost,
        escalationLevel: Math.floor(competitionLevel * 10),
      },
    });
  };

  if (!result) return null;

  const recColor = {
    EXECUTE: 'bg-green-500/20 text-green-400 border-green-500/30',
    SKIP: 'bg-red-500/20 text-red-400 border-red-500/30',
    WAIT: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Success Probability Engine
        </h3>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="text-xs text-gray-400 block mb-1">Spread (bps)</label>
          <input
            type="range"
            min="10"
            max="100"
            value={spread}
            onChange={(e) => setSpread(Number(e.target.value))}
            className="w-full accent-cyan-500"
          />
          <div className="text-xs text-cyan-400 font-mono mt-1">{spread} bps ({(spread / 100).toFixed(2)}%)</div>
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Liquidity ($M)</label>
          <input
            type="range"
            min="1"
            max="10"
            value={liquidity}
            onChange={(e) => setLiquidity(Number(e.target.value))}
            className="w-full accent-purple-500"
          />
          <div className="text-xs text-purple-400 font-mono mt-1">${liquidity}M</div>
        </div>
      </div>

      {/* Main Result */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/30">
          <div className="flex items-center gap-1 mb-1">
            <Target className="w-3 h-3 text-cyan-400" />
            <span className="text-xs text-gray-400">Win Probability</span>
          </div>
          <div className={`text-xl font-bold font-mono ${
            result.winProbability > 0.7 ? 'text-green-400' :
            result.winProbability > 0.4 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {(result.winProbability * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/30">
          <div className="flex items-center gap-1 mb-1">
            <TrendingUp className="w-3 h-3 text-green-400" />
            <span className="text-xs text-gray-400">Expected Value</span>
          </div>
          <div className={`text-xl font-bold font-mono ${
            result.expectedValue > 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            ${result.expectedValue.toFixed(2)}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/30">
          <div className="flex items-center gap-1 mb-1">
            <Users className="w-3 h-3 text-orange-400" />
            <span className="text-xs text-gray-400">Competitors</span>
          </div>
          <div className="text-xl font-bold font-mono text-orange-400">
            {result.competitors}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/30">
          <div className="flex items-center gap-1 mb-1">
            <BarChart3 className="w-3 h-3 text-purple-400" />
            <span className="text-xs text-gray-400">Bid Rank</span>
          </div>
          <div className="text-xl font-bold font-mono text-purple-400">
            #{result.gasBidRank}
          </div>
        </div>
      </div>

      {/* Recommendation */}
      <div className={`mb-4 p-3 rounded-lg border ${recColor[result.recommendation]}`}>
        <div className="flex items-center gap-2">
          {result.recommendation === 'EXECUTE' && <Zap className="w-4 h-4" />}
          {result.recommendation === 'SKIP' && <AlertTriangle className="w-4 h-4" />}
          {result.recommendation === 'WAIT' && <Clock className="w-4 h-4" />}
          <span className="text-sm font-bold">
            {result.recommendation === 'EXECUTE' && 'EXECUTE — High probability, positive EV'}
            {result.recommendation === 'SKIP' && 'SKIP — Low probability, too much competition'}
            {result.recommendation === 'WAIT' && 'WAIT — Negative EV, adjust parameters'}
          </span>
        </div>
      </div>

      {/* Factors Breakdown */}
      <div className="mb-4">
        <div className="text-xs text-gray-400 mb-2">Success Factors</div>
        <div className="space-y-2">
          {result.factors.map((factor) => (
            <div key={factor.name} className="flex items-center gap-2">
              <span className="text-xs text-gray-400 w-24">{factor.name}</span>
              <div className="flex-1 bg-gray-800/50 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full bg-${factor.color}-500 transition-all`}
                  style={{ width: `${factor.value * 100}%` }}
                />
              </div>
              <span className={`text-xs font-mono text-${factor.color}-400 w-12 text-right`}>
                {(factor.value * 100).toFixed(0)}%
              </span>
              <span className="text-xs text-gray-500 w-8 text-right">
                {(factor.weight * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Gas Bid Details */}
      <div className="bg-gray-800/30 rounded-lg p-3 border border-gray-700/30">
        <div className="flex items-center gap-1 mb-2">
          <Zap className="w-3 h-3 text-yellow-400" />
          <span className="text-xs text-gray-400">Gas Bid (Escalation Level {result.gasBid.escalationLevel})</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs">
          <div>
            <div className="text-gray-500">Base Fee</div>
            <div className="text-white font-mono">{result.gasBid.baseFee.toFixed(2)} gwei</div>
          </div>
          <div>
            <div className="text-gray-500">Priority Fee</div>
            <div className="text-yellow-400 font-mono">{result.gasBid.priorityFee.toFixed(2)} gwei</div>
          </div>
          <div>
            <div className="text-gray-500">Tip</div>
            <div className="text-purple-400 font-mono">${result.gasBid.tipUSD.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-gray-500">Tip %</div>
            <div className="text-purple-400 font-mono">{result.gasBid.tipPercent.toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-gray-500">Total Cost</div>
            <div className="text-red-400 font-mono">${result.gasBid.totalCost.toFixed(2)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
