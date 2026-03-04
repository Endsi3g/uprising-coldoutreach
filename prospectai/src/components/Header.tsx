import { useState, useEffect } from 'react';
import { Search, Bell, Sun, Moon, ChevronDown, X, Upload } from 'lucide-react';
import { useLocation } from 'react-router-dom';

export function Header() {
  const location = useLocation();
  const [isDark, setIsDark] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  // Profile State
  const [profileName, setProfileName] = useState(() => {
    return localStorage.getItem('profileName') || 'Jerome B.';
  });
  const [profileAvatar, setProfileAvatar] = useState(() => {
    return localStorage.getItem('profileAvatar') || 'https://i.pravatar.cc/150?u=jerome';
  });

  // Edit State
  const [editName, setEditName] = useState(profileName);
  const [editAvatar, setEditAvatar] = useState(profileAvatar);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  useEffect(() => {
    localStorage.setItem('profileName', profileName);
  }, [profileName]);

  useEffect(() => {
    localStorage.setItem('profileAvatar', profileAvatar);
  }, [profileAvatar]);
  
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

  const handleSaveProfile = () => {
    setProfileName(editName);
    setProfileAvatar(editAvatar);
    setIsProfileModalOpen(false);
  };

  return (
    <>
      <header className="w-full h-[84px] border-b border-border flex items-center justify-between px-8 bg-surface shrink-0 z-10 transition-colors duration-300">
        <div className="flex flex-col gap-1">
          <h1 className="font-sans text-xl font-bold text-text-primary leading-none tracking-tight">
            {getTitle()}
          </h1>
          <p className="font-sans text-sm text-text-secondary leading-none">
            Bon retour, {profileName.split(' ')[0]} ! Voici ce qui se passe aujourd'hui.
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
          <button title="Rechercher" className="w-10 h-10 bg-background rounded-full flex items-center justify-center hover:bg-border transition-colors border border-border">
            <Search className="w-4 h-4 text-text-primary" />
          </button>
          
          <button title="Notifications" className="w-10 h-10 bg-background rounded-full flex items-center justify-center relative hover:bg-border transition-colors border border-border">
            <Bell className="w-4 h-4 text-text-primary" />
            <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-danger rounded-full border-2 border-surface"></span>
          </button>

          {/* Account Menu */}
          <button onClick={() => {
              setEditName(profileName);
              setEditAvatar(profileAvatar);
              setIsProfileModalOpen(true);
            }} 
            className="flex items-center gap-3 ml-2 hover:opacity-80 transition-opacity pl-4 border-l border-border"
          >
            <img 
              src={profileAvatar} 
              alt={profileName} 
              className="w-10 h-10 rounded-full object-cover ring-2 ring-background"
              referrerPolicy="no-referrer"
            />
            <div className="max-sm:hidden flex flex-col items-start">
              <span className="font-sans text-sm font-semibold text-text-primary">{profileName}</span>
            </div>
            <ChevronDown className="w-4 h-4 text-text-secondary" />
          </button>
        </div>
      </header>

      {/* Edit Profile Modal */}
      {isProfileModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-xl border border-border mt-10">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-text-primary">Modifier le Profil</h2>
              <button 
                title="Fermer"
                onClick={() => setIsProfileModalOpen(false)}
                className="rounded-full p-2 hover:bg-background text-text-secondary transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-5">
              <div className="flex flex-col items-center gap-3 mb-6">
                <div className="relative group">
                  <img 
                    src={editAvatar} 
                    alt="Preview" 
                    onError={(e) => { (e.target as HTMLImageElement).src = 'https://ui-avatars.com/api/?name=Unknown&background=random' }}
                    className="w-24 h-24 rounded-full object-cover ring-4 ring-primary/20"
                  />
                  <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                     <Upload className="w-6 h-6 text-white" />
                  </div>
                </div>
                <p className="text-xs text-text-secondary">Aperçu de la photo</p>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-text-primary">URL de la Photo</label>
                <input 
                  type="text" 
                  value={editAvatar}
                  onChange={(e) => setEditAvatar(e.target.value)}
                  className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-text-primary placeholder:text-text-secondary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-colors"
                  placeholder="https://..."
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-text-primary">Nom d'affichage</label>
                <input 
                  type="text" 
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-text-primary placeholder:text-text-secondary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-colors"
                  placeholder="Votre nom"
                />
              </div>
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <button 
                onClick={() => setIsProfileModalOpen(false)}
                className="rounded-xl px-5 py-2.5 text-sm font-medium text-text-secondary hover:bg-background transition-colors"
              >
                Annuler
              </button>
              <button 
                onClick={handleSaveProfile}
                className="rounded-xl bg-primary px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-dark transition-colors shadow-sm"
              >
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
