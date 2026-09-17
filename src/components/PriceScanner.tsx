import { useState, useEffect } from 'react';
import { DexPrice } from '../types';
import { BarChart3, RefreshCw } from 'lucide-react';
import { generateDexPrices, tokens } from '../data/mockData';

export default function PriceScanner() {
  const [selectedToken, setSelectedToken] = useState('ETH');
  const [prices, setPrices] = useState<DexPrice[]>(generateDexPrices('ETH'));
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    setPrices(generateDexPrices(selectedToken));
  }, [selectedToken]);

  const refresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setPrices(generateDexPrices(selectedToken));
      setIsRefreshing(false);
    }, 500);
  };

  const maxPrice = Math.max(...prices.map(p => p.price));
  const minPrice = Math.min(...prices.map(p => p.price));
  const spread = ((maxPrice - minPrice) / minPrice) * 100;

  return (
    <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-green-400" />
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Price Scanner</h3>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedToken}
            onChange={(e) => setSelectedToken(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-white text-xs rounded px-2 py-1 focus:outline-none focus:border-cyan-500"
          >
            {tokens.map(t => (
              <option key={t.symbol} value={t.symbol}>{t.icon} {t.symbol}</option>
            ))}
          </select>
          <button
            onClick={refresh}
            className={`p-1.5 bg-gray-800 border border-gray-700 rounded hover:border-cyan-500 transition-all ${isRefreshing ? 'animate-spin' : ''}`}
          >
            <RefreshCw className="w-3 h-3 text-gray-400" />
          </button>
        </div>
      </div>

      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs text-gray-400">Cross-DEX Spread</span>
        <span className={`text-sm font-bold font-mono ${spread > 0.3 ? 'text-green-400' : spread > 0.1 ? 'text-yellow-400' : 'text-gray-400'}`}>
          {spread.toFixed(4)}%
        </span>
      </div>

      <div className="space-y-2">
        {prices.map((p) => {
          const isMax = p.price === maxPrice;
          const isMin = p.price === minPrice;
          return (
            <div key={p.dex} className="flex items-center gap-3 bg-gray-800/30 rounded-lg px-3 py-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white font-medium">{p.dex}</span>
                  <span className={`font-mono text-sm font-bold ${isMax ? 'text-red-400' : isMin ? 'text-green-400' : 'text-gray-300'}`}>
                    ${p.price.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-gray-500">
                    Liq: ${(p.liquidity / 1000000).toFixed(1)}M
                  </span>
                  <span className="text-xs text-gray-500">
                    24h: ${(p.volume24h / 1000000).toFixed(1)}M
                  </span>
                </div>
              </div>
              <div className="flex-shrink-0">
                {isMax && <span className="text-xs px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded">HIGH</span>}
                {isMin && <span className="text-xs px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded">LOW</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
