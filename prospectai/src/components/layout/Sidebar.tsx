import { Link, useLocation } from 'react-router-dom';
import { Home, Users, GitBranch, Zap, Mail, BarChart3, Settings, MapPin, History } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navigation = [
  { name: 'Tableau de bord', href: '/', icon: Home },
  { name: 'Prospects', href: '/leads', icon: Users },
  { name: 'Scraping Maps', href: '/scraping', icon: MapPin },
  { name: 'Pipelines', href: '/pipelines', icon: GitBranch },
  { name: 'Séquences', href: '/sequences', icon: Zap },
  { name: 'Messages', href: '/messages', icon: Mail },
  { name: 'Analyses', href: '/analytics', icon: BarChart3 },
  { name: 'Nouveautés', href: '/changelog', icon: History },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <div className="flex h-full w-[280px] flex-col border-r border-border bg-surface shadow-sm z-10 transition-colors duration-300">
      <div className="flex h-[84px] shrink-0 items-center px-8 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-white shadow-soft">
            <Zap className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold text-text-primary tracking-tight">Uprising Prospection</span>
        </div>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto px-4 py-6">
        <nav className="flex-1 space-y-1.5">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || (item.href !== '/' && location.pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  isActive
                    ? 'bg-primary text-white shadow-soft'
                    : 'text-text-secondary hover:bg-background hover:text-text-primary',
                  'group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200'
                )}
              >
                <item.icon
                  className={cn(
                    isActive ? 'text-white' : 'text-text-secondary group-hover:text-text-primary',
                    'h-5 w-5 shrink-0 transition-colors'
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
        
        <div className="mt-auto pt-6 border-t border-border">
          <Link
            to="/settings"
            className="group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-text-secondary transition-all duration-200 hover:bg-background hover:text-text-primary"
          >
            <Settings className="h-5 w-5 shrink-0 text-text-secondary group-hover:text-text-primary transition-colors" />
            Paramètres
          </Link>
        </div>
      </div>
    </div>
  );
}
