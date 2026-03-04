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
                  <label className="text-sm font-medium text-text-primary">Prénom</label>
                  <input 
                    type="text" 
                    defaultValue="Emily"
                    className="w-full px-4 py-2.5 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-primary">Nom</label>
                  <input 
                    type="text" 
                    defaultValue="Johnson"
                    className="w-full px-4 py-2.5 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-text-primary">Titre professionnel</label>
                  <input 
                    type="text" 
                    defaultValue="Designer UI/UX Senior"
                    className="w-full px-4 py-2.5 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium text-text-primary">Bio</label>
                  <textarea 
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
              <h2 className="text-xl font-semibold text-text-primary">Intégrations</h2>
              <p className="text-sm text-text-secondary">Connectez vos comptes externes pour automatiser votre prospection.</p>
              
              <div className="space-y-4 pt-4">
                {/* Gmail */}
                <div className="flex items-center justify-between p-4 border border-border rounded-xl bg-background">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm">
                      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Gmail_icon_%282020%29.svg/512px-Gmail_icon_%282020%29.svg.png" alt="Gmail" className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">Gmail API</h3>
                      <p className="text-xs text-text-secondary">Envoi d'emails automatisés</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors">
                    Se connecter avec Google
                  </button>
                </div>

                {/* Instagram */}
                <div className="flex items-center justify-between p-4 border border-border rounded-xl bg-background">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gradient-to-tr from-yellow-400 via-pink-500 to-purple-500 rounded-full flex items-center justify-center shadow-sm text-white">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">Instagram DM</h3>
                      <p className="text-xs text-text-secondary">Prospection via messages directs</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 border border-border bg-surface text-text-primary rounded-xl text-sm font-medium hover:bg-background transition-colors">
                    Connecter Instagram
                  </button>
                </div>

                {/* Apify */}
                <div className="flex flex-col p-4 border border-border rounded-xl bg-background gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-surface border border-border rounded-full flex items-center justify-center shadow-sm">
                      <span className="font-bold text-text-primary">A</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">Apify API</h3>
                      <p className="text-xs text-text-secondary">Scraping Google Maps</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <input 
                      type="password" 
                      placeholder="Clé API Apify (apify_api_...)"
                      className="flex-1 px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                    />
                    <button className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors">
                      Sauvegarder
                    </button>
                  </div>
                </div>

                {/* TextBelt */}
                <div className="flex flex-col p-4 border border-border rounded-xl bg-background gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-surface border border-border rounded-full flex items-center justify-center shadow-sm">
                      <span className="font-bold text-text-primary">T</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">TextBelt API</h3>
                      <p className="text-xs text-text-secondary">Envoi de SMS</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <input 
                      type="password" 
                      placeholder="Clé API TextBelt"
                      className="flex-1 px-4 py-2 bg-surface border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                    />
                    <button className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors">
                      Sauvegarder
                    </button>
                  </div>
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
