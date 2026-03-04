import { Link } from 'react-router-dom';

export function ProfileWidget() {
  return (
    <div className="w-full h-full min-h-[400px] bg-surface rounded-2xl shadow-soft overflow-hidden border border-border flex flex-col font-sans transition-colors duration-300">
      
      {/* Header Cover */}
      <div className="h-[120px] w-full relative bg-gradient-to-b from-primary/20 to-surface">
        <div className="absolute inset-0 opacity-30 bg-[url('https://picsum.photos/seed/cover/400/200')] bg-cover bg-center mix-blend-overlay"></div>
      </div>

      {/* Avatar & Info */}
      <div className="flex flex-col items-center px-6 -mt-[40px] relative z-10">
        <div className="relative">
          <img 
            src="https://i.pravatar.cc/150?u=emily" 
            alt="Emily Johnson" 
            className="w-[80px] h-[80px] rounded-full object-cover border-[4px] border-surface bg-background shadow-sm transition-colors duration-300"
            referrerPolicy="no-referrer"
          />
          <div className="absolute bottom-1 right-1 w-4 h-4 bg-success rounded-full border-2 border-surface"></div>
        </div>
        
        <h2 className="mt-3 text-xl font-bold text-text-primary leading-none">Emily Johnson</h2>
        <p className="mt-1 text-sm text-text-secondary">Designer UI/UX Senior</p>
      </div>

      {/* Stats (Metadata) */}
      <div className="mt-6 mx-6 bg-background rounded-xl p-4 flex justify-between items-center border border-border transition-colors duration-300">
        <div className="flex flex-col items-center gap-1 w-1/3">
          <span className="text-xs text-text-secondary">Expérience</span>
          <span className="font-semibold text-base text-text-primary">5 ans+</span>
        </div>
        <div className="w-px h-8 bg-border"></div>
        <div className="flex flex-col items-center gap-1 w-1/3">
          <span className="text-xs text-text-secondary">Projets</span>
          <span className="font-semibold text-base text-text-primary">400+</span>
        </div>
        <div className="w-px h-8 bg-border"></div>
        <div className="flex flex-col items-center gap-1 w-1/3">
          <span className="text-xs text-text-secondary">Abonnés</span>
          <span className="font-semibold text-base text-text-primary">1.9k</span>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-auto p-6 flex items-center gap-3">
        <Link to="/settings" className="flex-1 h-11 bg-primary text-white rounded-xl font-medium text-sm hover:bg-primary-dark transition-colors shadow-sm flex items-center justify-center">
          Voir le compte
        </Link>
        <Link to="/settings" className="flex-1 h-11 bg-surface text-text-primary border border-border rounded-xl font-medium text-sm hover:bg-background transition-colors flex items-center justify-center">
          Mon compte
        </Link>
      </div>

    </div>
  );
}
