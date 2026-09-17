import { useState, useEffect } from 'react';
import { NetworkStatus, MEVProtection } from '../types';

interface Props {
  network: NetworkStatus;
  mev: MEVProtection;
}

export default function NetworkPanel({ network, mev }: Props) {
  const [block, setBlock] = useState(network.blockNumber);
  const [gas, setGas] = useState(network.gasPrice);

  useEffect(() => {
    const interval = setInterval(() => {
      setBlock(b => b + 1);
      setGas(2 + Math.random() * 3);
    }, 12000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Network Status */}
      <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Testnet Status</h3>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Network</span>
            <span className="text-white font-mono text-sm">{network.network}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Chain ID</span>
            <span className="text-white font-mono text-sm">{network.chainId}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Block</span>
            <span className="text-cyan-400 font-mono text-sm">{block.toLocaleString()}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Gas Price</span>
            <span className="text-yellow-400 font-mono text-sm">{gas.toFixed(2)} Gwei</span>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-700/50">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-xs">RPC Endpoint</span>
              <code className="text-xs text-gray-500 truncate ml-2 max-w-[200px]">{network.rpcEndpoint}</code>
            </div>
          </div>
        </div>
      </div>

      {/* MEV Protection */}
      <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></div>
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">MEV Protection</h3>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Provider</span>
            <span className="text-white font-mono text-sm">{mev.provider}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Status</span>
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${
              mev.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
              {mev.status.toUpperCase()}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Protected Txs</span>
            <span className="text-purple-400 font-mono text-sm">{mev.protectedTxs}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Sandwich Attacks Blocked</span>
            <span className="text-red-400 font-mono text-sm">{mev.savedFromSandwich}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-sm">Total Saved</span>
            <span className="text-green-400 font-mono text-sm">{mev.totalSaved.toFixed(3)} ETH</span>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-700/50">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-xs">MEV RPC</span>
              <code className="text-xs text-purple-400 truncate ml-2 max-w-[200px]">{mev.rpcEndpoint}</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
