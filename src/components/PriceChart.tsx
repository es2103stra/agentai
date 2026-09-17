import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { PriceHistory } from '../types';
import { Activity } from 'lucide-react';

interface Props {
  data: PriceHistory[];
}

export default function PriceChart({ data }: Props) {
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">ETH Price Across DEXes (Live)</h3>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={formatTime}
              stroke="#6B7280"
              fontSize={10}
              interval={10}
            />
            <YAxis 
              stroke="#6B7280" 
              fontSize={10}
              domain={['dataMin - 5', 'dataMax + 5']}
              tickFormatter={(v) => `$${v}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              labelFormatter={formatTime}
              formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
            />
            <Legend 
              wrapperStyle={{ fontSize: '11px' }}
            />
            <Line type="monotone" dataKey="uniswap" stroke="#FF007A" strokeWidth={2} dot={false} name="Uniswap V3" />
            <Line type="monotone" dataKey="sushiswap" stroke="#00D395" strokeWidth={2} dot={false} name="SushiSwap" />
            <Line type="monotone" dataKey="pancakeswap" stroke="#D1884F" strokeWidth={2} dot={false} name="PancakeSwap" />
            <Line type="monotone" dataKey="curve" stroke="#FF6B35" strokeWidth={2} dot={false} name="Curve" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
