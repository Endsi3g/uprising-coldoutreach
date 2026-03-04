import { useState } from 'react';
import { Save, User, Mail, Lock, Bell, Link2, Webhook, CheckCircle2 } from 'lucide-react';

export function Settings() {
  const [activeTab, setActiveTab] = useState('profile');

  const tabs = [
    { id: 'profile', name: 'Profil', icon: User },
    { id: 'account', name: 'Compte', icon: Mail },
    { id: 'security', name: 'Sécurité', icon: Lock },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'integrations', name: 'Intégrations', icon: Link2 },
    { id: 'webhooks', name: 'Webhooks', icon: Webhook },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-8">
      <div>
        <h1 className="text-3xl font-bold text-text-primary tracking-tight">Paramètres</h1>
        <p className="mt-2 text-sm text-text-secondary">Gérez les paramètres de votre compte et vos préférences.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar Navigation */}
        <div className="w-full md:w-64 shrink-0">
          <nav className="flex md:flex-col gap-2 overflow-x-auto md:overflow-visible pb-2 md:pb-0">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors whitespace-nowrap ${
                    isActive 
                      ? 'bg-primary text-white shadow-soft' 
                      : 'text-text-secondary hover:bg-background hover:text-text-primary'
                  }`}
                >
                  <tab.icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-text-secondary'}`} />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content Area */}
        <div className="flex-1 bg-surface border border-border rounded-2xl shadow-soft p-6 md:p-8 transition-colors duration-300">
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-text-primary">Profil Public</h2>
              <p className="text-sm text-text-secondary">Ces informations seront affichées publiquement sur votre profil.</p>
              
              <div className="flex items-center gap-6 py-4">
                <img 
                  src="https://i.pravatar.cc/150?u=emily" 
                  alt="Profile" 
                  className="w-20 h-20 rounded-full object-cover border-4 border-background shadow-sm"
                />
                <div className="flex gap-3">
                  <button className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors shadow-sm">
                    Changer l'avatar
                  </button>
                  <button className="px-4 py-2 bg-background text-text-primary border border-border rounded-xl text-sm font-medium hover:bg-border transition-colors">
                    Supprimer
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label htmlFor="profile-firstname" className="text-sm font-medium text-text-primary">Prénom</label>
                  <input 
                    id="profile-firstname"
                    title="Prénom"
                    type="text" 
                    defaultValue="Emily"
                    className="w-full px-4 py-2.5 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="profile-lastname" className="text-sm font-medium text-text-primary">Nom</label>
                  <input 
                    id="profile-lastname"
                    title="Nom"
                    type="text" 
                    defaultValue="Johnson"
                    className="w-full px-4 py-2.5 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <label htmlFor="profile-jobtitle" className="text-sm font-medium text-text-primary">Titre professionnel</label>
                  <input 
                    id="profile-jobtitle"
                    title="Titre professionnel"
                    type="text" 
                    defaultValue="Designer UI/UX Senior"
                    className="w-full px-4 py-2.5 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <label htmlFor="profile-bio" className="text-sm font-medium text-text-primary">Bio</label>
                  <textarea 
                    id="profile-bio"
                    title="Bio"
                    rows={4}
                    defaultValue="Passionnée par la création d'interfaces utilisateur intuitives et esthétiques. Plus de 5 ans d'expérience dans le design de produits SaaS."
                    className="w-full px-4 py-2.5 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
                  />
                </div>
              </div>

              <div className="pt-6 border-t border-border flex justify-end">
                <button className="flex items-center gap-2 px-6 py-2.5 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors shadow-sm">
                  <Save className="w-4 h-4" />
                  Enregistrer les modifications
                </button>
              </div>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-text-primary">Clés API & Intégrations</h2>
              <p className="text-sm text-text-secondary">Ajoutez vos propres clés API pour débloquer les fonctionnalités avancées sans toucher au code.</p>
              
              <div className="space-y-4 pt-4">
                {/* Apify */}
                <div className="flex flex-col p-4 border border-border rounded-xl bg-background gap-4 transition-all hover:border-primary/50">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-surface border border-border rounded-full flex items-center justify-center shadow-sm">
                      <span className="font-bold text-text-primary">A</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">Apify API (Recherche Google Maps)</h3>
                      <p className="text-xs text-text-secondary">Permet de trouver automatiquement des prospects locaux.</p>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <div className="flex gap-3">
                      <input 
                        type="password" 
                        value={localStorage.getItem('APIFY_API_TOKEN') || ''}
                        onChange={(e) => localStorage.setItem('APIFY_API_TOKEN', e.target.value)}
                        placeholder="Collez votre clé ici (commence par apify_api_...)"
                        className="flex-1 px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                      />
                      <button 
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors"
                      >
                        Sauvegarder
                      </button>
                    </div>
                    <a href="https://console.apify.com/account/integrations" target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline ml-1">
                      Trouver ma clé Apify ici →
                    </a>
                  </div>
                </div>

                {/* TextBelt */}
                <div className="flex flex-col p-4 border border-border rounded-xl bg-background gap-4 transition-all hover:border-primary/50">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-surface border border-border rounded-full flex items-center justify-center shadow-sm">
                      <span className="font-bold text-text-primary">T</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">TextBelt API (SMS Automatiques)</h3>
                      <p className="text-xs text-text-secondary">Envoi de relances par SMS à vos prospects.</p>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <div className="flex gap-3">
                      <input 
                        type="password" 
                        value={localStorage.getItem('TEXTBELT_KEY') || ''}
                        onChange={(e) => localStorage.setItem('TEXTBELT_KEY', e.target.value)}
                        placeholder="Collez votre clé TextBelt ici..."
                        className="flex-1 px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                      />
                      <button 
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors"
                      >
                        Sauvegarder
                      </button>
                    </div>
                    <a href="https://textbelt.com/" target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline ml-1">
                      Générer une clé TextBelt →
                    </a>
                  </div>
                </div>

                {/* Jasmin SMS Gateway */}
                <div className="flex flex-col p-4 border border-border rounded-xl bg-background gap-4 transition-all hover:border-primary/50">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-surface border border-border rounded-full flex items-center justify-center shadow-sm">
                      <span className="font-bold text-text-primary text-xs">Jasmin</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">Jasmin SMS Gateway</h3>
                      <p className="text-xs text-text-secondary">Routage SMS avancé (SMPP, HTTP, failover).</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="text-[10px] uppercase font-bold text-text-secondary ml-1">URL API</label>
                      <input 
                        type="text" 
                        value={localStorage.getItem('JASMIN_API_URL') || ''}
                        onChange={(e) => localStorage.setItem('JASMIN_API_URL', e.target.value)}
                        placeholder="http://localhost:8080"
                        className="w-full px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] uppercase font-bold text-text-secondary ml-1">Utilisateur</label>
                      <input 
                        type="text" 
                        value={localStorage.getItem('JASMIN_USER') || ''}
                        onChange={(e) => localStorage.setItem('JASMIN_USER', e.target.value)}
                        placeholder="jookers"
                        className="w-full px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                      />
                    </div>
                    <div className="space-y-1 md:col-span-2">
                      <label className="text-[10px] uppercase font-bold text-text-secondary ml-1">Mot de passe</label>
                      <div className="flex gap-3">
                        <input 
                          type="password" 
                          value={localStorage.getItem('JASMIN_PASSWORD') || ''}
                          onChange={(e) => localStorage.setItem('JASMIN_PASSWORD', e.target.value)}
                          placeholder="••••••••"
                          className="flex-1 px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                        />
                        <button 
                          onClick={() => window.location.reload()}
                          className="px-6 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors whitespace-nowrap"
                        >
                          Appliquer
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center px-1">
                    <a href="http://jasminsms.com/" target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline">
                      Documentation Jasmin →
                    </a>
                  </div>
                </div>
                
                {/* Gmail Placeholder */}
                <div className="flex items-center justify-between p-4 border border-border rounded-xl bg-background opacity-75">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm">
                      <Mail className="w-5 h-5 text-gray-500" />
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">Gmail API</h3>
                      <p className="text-xs text-text-secondary">Envoi d'emails via votre compte pro (Bientôt disponible)</p>
                    </div>
                  </div>
                  <button disabled className="px-4 py-2 bg-surface border border-border text-text-secondary rounded-xl text-sm font-medium cursor-not-allowed">
                    Prochainement
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'webhooks' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-text-primary">Webhooks & Automatisation</h2>
              <p className="text-sm text-text-secondary">Configurez des webhooks sortants pour Zapier, Make ou votre propre backend.</p>
              
              <div className="space-y-4 pt-4">
                <div className="flex flex-col p-4 border border-border rounded-xl bg-background gap-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-text-primary">Webhook de réception (Catch Hook)</h3>
                      <p className="text-xs text-text-secondary mt-1">Déclenché lors d'une réponse entrante d'un prospect.</p>
                    </div>
                    <div className="flex items-center gap-2 text-success text-sm font-medium">
                      <CheckCircle2 className="w-4 h-4" /> Actif
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <input 
                      type="url" 
                      defaultValue="https://hooks.zapier.com/hooks/catch/123456/abcde/"
                      placeholder="https://..."
                      className="flex-1 px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                    />
                    <button className="px-4 py-2 bg-surface border border-border text-text-primary rounded-xl text-sm font-medium hover:bg-background transition-colors">
                      Tester
                    </button>
                    <button className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors">
                      Sauvegarder
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab !== 'profile' && activeTab !== 'integrations' && activeTab !== 'webhooks' && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-16 h-16 bg-background rounded-full flex items-center justify-center mb-4">
                <Lock className="w-8 h-8 text-text-secondary" />
              </div>
              <h3 className="text-lg font-medium text-text-primary">Section en construction</h3>
              <p className="text-sm text-text-secondary mt-2 max-w-sm">
                Les paramètres de cette section seront bientôt disponibles.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
