import { useState, useEffect } from 'react';
import { Search, Bell, Sun, Moon, ChevronDown } from 'lucide-react';
import { useLocation } from 'react-router-dom';

export function Header() {
  const location = useLocation();
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);
  
  // Format path to title in French
  const getTitle = () => {
    if (location.pathname === '/') return 'Aperçu du Tableau de bord';
    const path = location.pathname.substring(1);
    const titles: Record<string, string> = {
      'leads': 'Prospects',
      'pipelines': 'Pipelines',
      'sequences': 'Séquences',
      'messages': 'Messages',
      'analytics': 'Analyses',
      'settings': 'Paramètres'
    };
    return titles[path] || path.charAt(0).toUpperCase() + path.slice(1);
  };

  return (
    <header className="w-full h-[84px] border-b border-border flex items-center justify-between px-8 bg-surface shrink-0 z-10 transition-colors duration-300">
      <div className="flex flex-col gap-1">
        <h1 className="font-sans text-xl font-bold text-text-primary leading-none tracking-tight">
          {getTitle()}
        </h1>
        <p className="font-sans text-sm text-text-secondary leading-none">
          Bon retour, Jerome ! Voici ce qui se passe aujourd'hui.
        </p>
      </div>

      <div className="flex items-center gap-4">
        {/* Toggle Mode */}
        <button 
          onClick={() => setIsDark(!isDark)}
          className="w-14 h-8 bg-background rounded-full flex items-center p-1 relative cursor-pointer border border-border transition-colors focus:outline-none"
        >
          <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-transform duration-300 ${isDark ? 'translate-x-6 bg-surface' : 'translate-x-0 bg-surface shadow-sm'}`}>
            {isDark ? <Moon className="w-3 h-3 text-text-primary" /> : <Sun className="w-3 h-3 text-text-primary" />}
          </div>
        </button>

        {/* Action Buttons */}
        <button className="w-10 h-10 bg-background rounded-full flex items-center justify-center hover:bg-border transition-colors border border-border">
          <Search className="w-4 h-4 text-text-primary" />
        </button>
        
        <button className="w-10 h-10 bg-background rounded-full flex items-center justify-center relative hover:bg-border transition-colors border border-border">
          <Bell className="w-4 h-4 text-text-primary" />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-danger rounded-full border-2 border-surface"></span>
        </button>

        {/* Account Menu */}
        <button className="flex items-center gap-3 ml-2 hover:opacity-80 transition-opacity pl-4 border-l border-border">
          <img 
            src="https://i.pravatar.cc/150?u=jerome" 
            alt="Jerome B." 
            className="w-10 h-10 rounded-full object-cover ring-2 ring-background"
            referrerPolicy="no-referrer"
          />
          <div className="flex flex-col items-start hidden sm:flex">
            <span className="font-sans text-sm font-semibold text-text-primary">Jerome B.</span>
          </div>
          <ChevronDown className="w-4 h-4 text-text-secondary" />
        </button>
      </div>
    </header>
  );
}
