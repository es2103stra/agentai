import { useState } from 'react';
import { Zap, ArrowRight, Check, X, Loader2 } from 'lucide-react';

interface SimulationStep {
  id: number;
  label: string;
  status: 'pending' | 'running' | 'success' | 'error';
  detail: string;
}

export default function FlashLoanSimulator() {
  const [isRunning, setIsRunning] = useState(false);
  const [steps, setSteps] = useState<SimulationStep[]>([
    { id: 1, label: 'Request Flash Loan', status: 'pending', detail: 'Borrow 100 ETH from Aave V3' },
    { id: 2, label: 'Buy on Uniswap V3', status: 'pending', detail: 'Swap 100 ETH → 290,000 USDC @ $3,448' },
    { id: 3, label: 'Sell on SushiSwap', status: 'pending', detail: 'Swap 290,000 USDC → 100.15 ETH @ $3,452' },
    { id: 4, label: 'Repay Flash Loan', status: 'pending', detail: 'Repay 100 ETH + 0.09 ETH fee (0.09%)' },
    { id: 5, label: 'Submit via Flashbots', status: 'pending', detail: 'MEV-protected bundle submission' },
    { id: 6, label: 'Profit Distribution', status: 'pending', detail: 'Net profit: 0.06 ETH ($207)' },
  ]);

  const runSimulation = async () => {
    setIsRunning(true);
    
    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800));
      setSteps(prev => prev.map((step, idx) => {
        if (idx === i) return { ...step, status: 'running' };
        if (idx < i) return { ...step, status: 'success' };
        return step;
      }));
    }
    
    await new Promise(resolve => setTimeout(resolve, 600));
    setSteps(prev => prev.map(step => ({ ...step, status: 'success' })));
    setIsRunning(false);
  };

  const resetSimulation = () => {
    setSteps(prev => prev.map(step => ({ ...step, status: 'pending' })));
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Flash Loan Simulator</h3>
        </div>
        <div className="flex gap-2">
          {!isRunning && steps[0].status === 'success' && (
            <button
              onClick={resetSimulation}
              className="px-3 py-1.5 bg-gray-700/50 hover:bg-gray-700 border border-gray-600 text-gray-300 text-xs font-bold rounded transition-all"
            >
              Reset
            </button>
          )}
          <button
            onClick={runSimulation}
            disabled={isRunning}
            className="px-4 py-1.5 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 disabled:opacity-50 text-white text-xs font-bold rounded transition-all hover:scale-105 disabled:hover:scale-100"
          >
            {isRunning ? 'Running...' : 'Run Simulation'}
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {steps.map((step, idx) => (
          <div key={step.id} className="flex items-center gap-3">
            <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center border-2 transition-all
              ${step.status === 'pending' ? 'border-gray-600 text-gray-600' : ''}
              ${step.status === 'running' ? 'border-yellow-400 text-yellow-400 animate-pulse' : ''}
              ${step.status === 'success' ? 'border-green-400 text-green-400' : ''}
              ${step.status === 'error' ? 'border-red-400 text-red-400' : ''}
            `}>
              {step.status === 'pending' && <span className="text-xs">{idx + 1}</span>}
              {step.status === 'running' && <Loader2 className="w-3 h-3 animate-spin" />}
              {step.status === 'success' && <Check className="w-3 h-3" />}
              {step.status === 'error' && <X className="w-3 h-3" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className={`text-sm font-medium ${
                  step.status === 'success' ? 'text-green-400' : 
                  step.status === 'running' ? 'text-yellow-400' : 'text-gray-400'
                }`}>
                  {step.label}
                </span>
                {idx < steps.length - 1 && <ArrowRight className="w-3 h-3 text-gray-600" />}
              </div>
              <div className="text-xs text-gray-500 truncate">{step.detail}</div>
            </div>
          </div>
        ))}
      </div>

      {steps[0].status === 'success' && (
        <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">Simulation Complete</span>
          </div>
          <div className="mt-1 text-xs text-gray-400">
            Flash loan executed successfully. Net profit: <span className="text-green-400 font-bold">0.06 ETH (~$207)</span>
            <br/>
            Transaction protected by Flashbots - no MEV extraction detected.
          </div>
        </div>
      )}
    </div>
  );
}
