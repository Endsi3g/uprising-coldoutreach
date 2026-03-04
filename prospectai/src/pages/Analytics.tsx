import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, AreaChart, Area } from 'recharts';
import { Calendar, Download, TrendingUp, Users, Mail, MousePointerClick } from 'lucide-react';

const data = [
  { name: 'Jan', leads: 400, replies: 24, booked: 10 },
  { name: 'Fév', leads: 300, replies: 13, booked: 5 },
  { name: 'Mar', leads: 200, replies: 98, booked: 20 },
  { name: 'Avr', leads: 278, replies: 39, booked: 15 },
  { name: 'Mai', leads: 189, replies: 48, booked: 12 },
  { name: 'Juin', leads: 239, replies: 38, booked: 8 },
  { name: 'Juil', leads: 349, replies: 43, booked: 18 },
];

const funnelData = [
  { name: 'Total Prospects', value: 1247, fill: '#1E40AF' },
  { name: 'Contactés', value: 854, fill: '#0EA5E9' },
  { name: 'Ouverts', value: 432, fill: '#10B981' },
  { name: 'Répondus', value: 124, fill: '#F59E0B' },
  { name: 'Rendez-vous', value: 47, fill: '#EF4444' },
];

export function Analytics() {
  return (
    <div className="flex h-full flex-col space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Analyses</h1>
          <p className="text-sm text-text-secondary">Analysez les performances de vos campagnes.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center justify-center rounded-xl border border-border bg-surface px-4 py-2 text-sm font-medium text-text-primary shadow-sm hover:bg-background transition-colors">
            <Calendar className="mr-2 h-4 w-4" />
            30 derniers jours
          </button>
          <button className="inline-flex items-center justify-center rounded-xl bg-primary px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-dark transition-colors">
            <Download className="mr-2 h-4 w-4" />
            Exporter le rapport
          </button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { name: 'Prospects générés', value: '1,247', icon: Users, color: 'text-primary bg-primary/10' },
          { name: 'Emails envoyés', value: '8,432', icon: Mail, color: 'text-secondary bg-secondary/10' },
          { name: 'Taux d\'ouverture moyen', value: '42.8%', icon: MousePointerClick, color: 'text-warning bg-warning/10' },
          { name: 'Rendez-vous pris', value: '47', icon: TrendingUp, color: 'text-success bg-success/10' },
        ].map((stat) => (
          <div key={stat.name} className="rounded-xl border border-border bg-surface p-6 shadow-sm flex items-center gap-4">
            <div className={`rounded-lg p-3 ${stat.color}`}>
              <stat.icon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-secondary">{stat.name}</p>
              <p className="text-2xl font-bold text-text-primary">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Leads Over Time */}
        <div className="rounded-xl border border-border bg-surface p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-text-primary mb-6">Prospects & Engagement dans le temps</h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1E40AF" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#1E40AF" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorReplies" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0EA5E9" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} dx={-10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 10px 25px -3px rgb(0 0 0 / 0.1)' }}
                  itemStyle={{ color: '#0F172A', fontWeight: 500 }}
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                <Area type="monotone" dataKey="leads" stroke="#1E40AF" strokeWidth={2} fillOpacity={1} fill="url(#colorLeads)" name="Nouveaux prospects" />
                <Area type="monotone" dataKey="replies" stroke="#0EA5E9" strokeWidth={2} fillOpacity={1} fill="url(#colorReplies)" name="Réponses" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Conversion Funnel */}
        <div className="rounded-xl border border-border bg-surface p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-text-primary mb-6">Entonnoir de conversion</h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnelData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#E2E8F0" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#0F172A', fontWeight: 500, fontSize: 13 }} />
                <Tooltip 
                  cursor={{ fill: '#F8FAFC' }}
                  contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '12px', border: '1px solid #E2E8F0' }}
                />
                <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={32}>
                  {funnelData.map((entry, index) => (
                    <cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
