import { motion } from 'framer-motion';
import { Users, Mail, DollarSign, TrendingUp, ArrowUpRight, Zap, Loader2 } from 'lucide-react';
import { Charts } from '../components/Charts';
import { ProfileWidget } from '../components/ProfileWidget';
import { useDashboardOverview } from '../api/queries';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export function Dashboard() {
  const { data: analytics, isLoading } = useDashboardOverview();

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const overview = analytics?.current || { total_leads: 0, active_sequences: 0, total_sent: 0, response_rate: 0 };
  const change = analytics?.percent_change || { leads: 0, sequences: 0, sent: 0, response: 0 };

  const stats = [
    { name: 'Total Prospects', value: overview.total_leads.toString(), change: `${change.leads >= 0 ? '+' : ''}${change.leads}%`, icon: Users, color: change.leads >= 0 ? 'text-success' : 'text-danger', bg: change.leads >= 0 ? 'bg-success/10' : 'bg-danger/10' },
    { name: 'Séquences Actives', value: overview.active_sequences.toString(), change: `${change.sequences >= 0 ? '+' : ''}${change.sequences}%`, icon: Zap, color: change.sequences >= 0 ? 'text-success' : 'text-danger', bg: change.sequences >= 0 ? 'bg-success/10' : 'bg-danger/10' },
    { name: 'Emails Envoyés', value: overview.total_sent.toString(), change: `${change.sent >= 0 ? '+' : ''}${change.sent}%`, icon: Mail, color: change.sent >= 0 ? 'text-success' : 'text-danger', bg: change.sent >= 0 ? 'bg-success/10' : 'bg-danger/10' },
    { name: 'Taux de Réponse', value: `${overview.response_rate.toFixed(1)}%`, change: `${change.response >= 0 ? '+' : ''}${change.response}%`, icon: TrendingUp, color: change.response >= 0 ? 'text-success' : 'text-danger', bg: change.response >= 0 ? 'bg-success/10' : 'bg-danger/10' },
  ];

  return (
    <div className="space-y-8 pb-8">
      {/* KPI Cards */}
      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
      >
        {stats.map((stat) => (
          <motion.div
            key={stat.name}
            variants={item}
            className="relative overflow-hidden rounded-2xl bg-surface p-6 shadow-soft border border-border group hover:shadow-float transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 text-primary group-hover:scale-110 transition-transform duration-300">
                <stat.icon className="h-6 w-6" />
              </div>
              <div className={`flex items-center gap-1 ${stat.color} ${stat.bg} px-2.5 py-1 rounded-full text-xs font-medium`}>
                <ArrowUpRight className={`w-3 h-3 ${stat.change.startsWith('-') ? 'rotate-90' : ''}`} />
                {stat.change}
              </div>
            </div>
            <div className="mt-4">
              <h3 className="text-text-secondary text-sm font-medium">{stat.name}</h3>
              <p className="text-3xl font-bold text-text-primary mt-1 tracking-tight">{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Main Content Grid */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, type: "spring", stiffness: 300, damping: 24 }}
        className="grid grid-cols-1 xl:grid-cols-3 gap-8"
      >
        <div className="xl:col-span-2 h-full">
          <Charts />
        </div>
        <div className="xl:col-span-1 h-full">
          <ProfileWidget />
        </div>
      </motion.div>
    </div>
  );
}
