import { useState } from 'react';
import { Plus, Search, FileText, Send, Mail, MessageSquare, MoreHorizontal, Edit2, Trash2 } from 'lucide-react';

interface Template {
  id: string;
  name: string;
  type: 'email' | 'linkedin' | 'sms';
  subject?: string;
  content: string;
  updatedAt: string;
}

const INITIAL_TEMPLATES: Template[] = [
  {
    id: '1',
    name: 'Cold Email - Premier Contact',
    type: 'email',
    subject: 'Opportunité de partenariat pour {{companyName}}',
    content: 'Bonjour {{firstName}},\n\nJ\'ai découvert {{companyName}} et j\'ai été impressionné par votre récente croissance. Nous aidons des entreprises similaires à automatiser leur prospection B2B.\n\nSeriez-vous ouvert à un bref échange cette semaine ?\n\nCordialement,',
    updatedAt: '2023-11-20'
  },
  {
    id: '2',
    name: 'Connexion LinkedIn',
    type: 'linkedin',
    content: 'Bonjour {{firstName}}, je suis de près votre parcours dans le secteur SaaS. J\'aimerais échanger sur nos défis communs. Au plaisir !',
    updatedAt: '2023-11-21'
  },
  {
    id: '3',
    name: 'Relance SMS J+3',
    type: 'sms',
    content: 'Bonjour {{firstName}}, je vous ai envoyé un email en début de semaine concernant {{companyName}}. Avez-vous eu l\'occasion d\'y jeter un œil ?',
    updatedAt: '2023-11-22'
  }
];

export function Templates() {
  const [searchTerm, setSearchTerm] = useState('');
  const [templates, setTemplates] = useState<Template[]>(INITIAL_TEMPLATES);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Partial<Template>>({ type: 'email' });

  const filteredTemplates = templates.filter(t => 
    t.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    t.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSave = () => {
    if (!editingTemplate.name || !editingTemplate.content) return;
    
    if (editingTemplate.id) {
      setTemplates(templates.map(t => t.id === editingTemplate.id ? { ...t, ...editingTemplate } as Template : t));
    } else {
      setTemplates([...templates, { 
        ...editingTemplate, 
        id: Math.random().toString(36).substr(2, 9),
        updatedAt: new Date().toISOString().split('T')[0]
      } as Template]);
    }
    setIsEditorOpen(false);
    setEditingTemplate({ type: 'email' });
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail className="w-4 h-4" />;
      case 'linkedin': return <Send className="w-4 h-4" />;
      case 'sms': return <MessageSquare className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getBadgeColor = (type: string) => {
    switch (type) {
      case 'email': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'linkedin': return 'bg-sky-500/10 text-sky-500 border-sky-500/20';
      case 'sms': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  };

  const insertVariable = (variable: string) => {
    setEditingTemplate(prev => ({
      ...prev,
      content: (prev.content || '') + `{{${variable}}}`
    }));
  };

  return (
    <div className="flex h-full flex-col space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-primary tracking-tight">Modèles</h1>
          <p className="mt-2 text-sm text-text-secondary">Gérez vos modèles d'emails, LinkedIn et SMS pour vos séquences.</p>
        </div>
        <button 
          onClick={() => { setEditingTemplate({ type: 'email' }); setIsEditorOpen(true); }}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Nouveau modèle
        </button>
      </div>

      <div className="flex items-center gap-4 bg-surface p-4 rounded-2xl border border-border shadow-soft">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
          <input
            type="text"
            placeholder="Rechercher un modèle..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
          />
        </div>
        <select title="Filtrer par type de modèle" className="px-4 py-2 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 appearance-none pr-8">
          <option value="all">Tous les types</option>
          <option value="email">Email</option>
          <option value="linkedin">LinkedIn</option>
          <option value="sms">SMS</option>
        </select>
      </div>

      {isEditorOpen ? (
        <div className="bg-surface rounded-2xl border border-border shadow-soft p-6 space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
          <div className="flex justify-between items-center pb-4 border-b border-border">
            <h2 className="text-xl font-semibold text-text-primary">
              {editingTemplate.id ? 'Éditer le modèle' : 'Créer un modèle'}
            </h2>
            <div className="flex gap-2">
              <button 
                onClick={() => setIsEditorOpen(false)}
                className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-background rounded-xl transition-colors"
              >
                Annuler
              </button>
              <button 
                onClick={handleSave}
                className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors shadow-sm"
              >
                Enregistrer
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-4">
              <div className="flex gap-4">
                <div className="flex-1 space-y-2">
                  <label className="text-sm font-medium text-text-primary">Nom du modèle</label>
                  <input 
                    type="text" 
                    value={editingTemplate.name || ''}
                    onChange={e => setEditingTemplate({...editingTemplate, name: e.target.value})}
                    placeholder="Ex: Première approche LinkedIn"
                    className="w-full px-4 py-2 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-primary">Type</label>
                  <select 
                    title="Type de modèle"
                    value={editingTemplate.type || 'email'}
                    onChange={e => setEditingTemplate({...editingTemplate, type: e.target.value as any})}
                    className="w-full px-4 py-2 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                  >
                    <option value="email">Email</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="sms">SMS</option>
                  </select>
                </div>
              </div>

              {editingTemplate.type === 'email' && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-text-primary">Objet de l'email</label>
                  <input 
                    type="text" 
                    value={editingTemplate.subject || ''}
                    onChange={e => setEditingTemplate({...editingTemplate, subject: e.target.value})}
                    placeholder="Ex: Question concernant {{companyName}}"
                    className="w-full px-4 py-2 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-text-primary">Contenu</label>
                <textarea 
                  rows={8}
                  value={editingTemplate.content || ''}
                  onChange={e => setEditingTemplate({...editingTemplate, content: e.target.value})}
                  placeholder="Tapez le contenu de votre message ici..."
                  className="w-full px-4 py-3 bg-background border border-border rounded-xl text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-y"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-background rounded-xl p-4 border border-border">
                <h3 className="text-sm font-medium text-text-primary mb-3">Variables dynamiques</h3>
                <p className="text-xs text-text-secondary mb-4">Cliquez pour insérer une variable dans votre modèle.</p>
                <div className="space-y-2">
                  {['firstName', 'lastName', 'companyName', 'jobTitle', 'industry', 'city'].map(variable => (
                    <button
                      key={variable}
                      onClick={() => insertVariable(variable)}
                      className="w-full text-left px-3 py-2 text-xs font-mono bg-surface border border-border hover:border-primary/50 text-text-secondary hover:text-primary rounded-lg transition-colors"
                    >
                      {`{{${variable}}}`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.length === 0 ? (
            <div className="col-span-full flex flex-col items-center justify-center p-12 text-center bg-surface border border-dashed border-border rounded-2xl">
              <FileText className="w-12 h-12 text-text-secondary mb-4" />
              <h3 className="text-lg font-medium text-text-primary">Aucun modèle trouvé</h3>
              <p className="text-sm text-text-secondary mt-1 max-w-sm">Vous n'avez pas encore de modèles qui correspondent à votre recherche.</p>
              <button 
                onClick={() => { setEditingTemplate({ type: 'email' }); setIsEditorOpen(true); }}
                className="mt-6 px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors"
              >
                Créer un modèle
              </button>
            </div>
          ) : (
            filteredTemplates.map(template => (
              <div key={template.id} className="group bg-surface rounded-2xl border border-border overflow-hidden hover:border-primary/30 hover:shadow-md transition-all duration-300">
                <div className="p-5">
                  <div className="flex justify-between items-start mb-4">
                    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${getBadgeColor(template.type)}`}>
                      {getIcon(template.type)}
                      <span className="capitalize">{template.type}</span>
                    </div>
                    <div className="flex opacity-0 group-hover:opacity-100 transition-opacity gap-1">
                      <button 
                        title="Éditer le modèle"
                        onClick={() => { setEditingTemplate(template); setIsEditorOpen(true); }}
                        className="p-1.5 text-text-secondary hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button 
                        title="Supprimer le modèle"
                        className="p-1.5 text-text-secondary hover:text-error hover:bg-error/10 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <h3 className="text-base font-semibold text-text-primary mb-2 truncate" title={template.name}>
                    {template.name}
                  </h3>
                  {template.subject && (
                    <p className="text-xs font-medium text-text-primary mb-2 line-clamp-1">
                      <span className="text-text-secondary opacity-70">Objet:</span> {template.subject}
                    </p>
                  )}
                  <p className="text-sm text-text-secondary line-clamp-3 leading-relaxed whitespace-pre-wrap font-mono relative opacity-80">
                    {template.content}
                    <div className="absolute bottom-0 left-0 right-0 h-6 bg-linear-to-t from-surface to-transparent" />
                  </p>
                </div>
                <div className="px-5 py-3 border-t border-border bg-background/50 flex justify-between items-center">
                  <span className="text-xs font-medium text-text-secondary/70">
                    Modifié le {template.updatedAt}
                  </span>
                  <button className="text-xs font-medium text-text-primary hover:text-primary transition-colors">
                    Utiliser →
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
