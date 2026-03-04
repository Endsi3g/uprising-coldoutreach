import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', revenus: 4000, ventes: 2400 },
  { name: 'Fév', revenus: 3000, ventes: 1398 },
  { name: 'Mar', revenus: 2000, ventes: 9800 },
  { name: 'Avr', revenus: 2780, ventes: 3908 },
  { name: 'Mai', revenus: 1890, ventes: 4800 },
  { name: 'Juin', revenus: 2390, ventes: 3800 },
  { name: 'Juil', revenus: 3490, ventes: 4300 },
];

export function Charts() {
  return (
    <div className="w-full h-full min-h-[400px] border border-border bg-surface rounded-2xl p-6 shadow-soft flex flex-col transition-colors duration-300">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-text-primary">Aperçu des Performances</h2>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-primary"></span>
            <span className="text-text-secondary">Revenus</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-secondary"></span>
            <span className="text-text-secondary">Ventes</span>
          </div>
        </div>
      </div>
      
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.15}/>
                <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
            <XAxis 
              dataKey="name" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--color-text-secondary)', fontSize: 12, fontFamily: 'var(--font-sans)' }} 
              dy={10} 
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--color-text-secondary)', fontSize: 12, fontFamily: 'var(--font-sans)' }} 
              dx={-10} 
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'var(--color-surface)', 
                borderRadius: '12px', 
                border: '1px solid var(--color-border)', 
                boxShadow: 'var(--shadow-soft)',
                fontFamily: 'var(--font-sans)',
                padding: '12px'
              }}
              itemStyle={{ color: 'var(--color-text-primary)', fontWeight: 600 }}
            />
            <Area 
              type="monotone" 
              dataKey="revenus" 
              stroke="var(--color-primary)" 
              strokeWidth={3} 
              fillOpacity={1} 
              fill="url(#colorRevenue)" 
              activeDot={{ r: 6, fill: 'var(--color-primary)', stroke: 'var(--color-surface)', strokeWidth: 2 }}
            />
            <Area 
              type="monotone" 
              dataKey="ventes" 
              stroke="var(--color-secondary)" 
              strokeWidth={3} 
              fill="none" 
              activeDot={{ r: 6, fill: 'var(--color-secondary)', stroke: 'var(--color-surface)', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
