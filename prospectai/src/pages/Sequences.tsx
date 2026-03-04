import { useState } from 'react';
import { Plus, Zap, Mail, Clock, MessageSquare, ArrowRight, MoreHorizontal, Play, Pause, Settings, Instagram, Loader2 } from 'lucide-react';
import { useSequences } from '../api/queries';

const steps = [
  { id: 1, type: 'email', title: 'Email 1: Introduction', content: 'Objet : Plus de chantiers pour {{company_name}} dans la région de {{city}} ?\n\nBonjour {{first_name}},\n\nJ\'ai remarqué que {{company_name}} fait de l\'excellent travail en {{specific_service}} à {{city}}.\n\nEn tant qu\'entrepreneur, je sais que votre temps est précieux et que trouver des leads qualifiés peut être un vrai défi. Nous aidons des entrepreneurs spécialisés comme vous à générer des soumissions régulières.\n\nSeriez-vous ouvert à un court appel de 10 minutes la semaine prochaine ?\n\nAu plaisir,\n\n{{my_name}}' },
  { id: 2, type: 'wait', title: 'Attente 48h', content: 'Attendre 2 jours avant la prochaine étape.' },
  { id: 3, type: 'sms', title: 'SMS 1: Premier contact', content: 'Salut {{first_name}}, c\'est {{my_name}}. J\'ai vu le beau travail de {{company_name}} en {{specific_service}}. Prenez-vous de nouveaux chantiers à {{city}} en ce moment ?' },
  { id: 4, type: 'wait', title: 'Attente 3 jours', content: 'Attendre 3 jours avant la prochaine étape.' },
  { id: 5, type: 'instagram', title: 'Instagram DM: Suivi', content: 'Salut {{first_name}}, je vous ai envoyé un email récemment. Superbes réalisations sur votre page !' },
  { id: 6, type: 'email', title: 'Email 2: Relance', content: 'Objet : Re: Plus de chantiers pour {{company_name}} dans la région de {{city}} ?\n\nSalut {{first_name}},\n\nJe vous relance brièvement. Récemment, nous avons aidé un autre entrepreneur en {{specific_service}} à obtenir 15 nouvelles soumissions qualifiées en moins d\'un mois.\n\nNotre approche est simple : on s\'occupe de vous trouver des clients sérieux, et vous vous concentrez sur vos chantiers.\n\nAvez-vous des disponibilités ce jeudi pour en jaser rapidement ?\n\nBonne journée,\n\n{{my_name}}' },
  { id: 7, type: 'condition', title: 'Condition: Si réponse', content: 'Arrêter la séquence si le prospect répond.' },
];

export function Sequences() {
  const [activeTab, setActiveTab] = useState('list');
  const [activeStep, setActiveStep] = useState(steps[0]);

  const { data: sequences = [], isLoading, isError } = useSequences();

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-text-secondary">Chargement de vos séquences...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex h-full flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary tracking-tight">Séquences</h1>
            <p className="text-sm text-text-secondary">Automatisez votre prospection multi-canal.</p>
          </div>
        </div>
        <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-border border-dashed bg-surface/50 p-6 text-center">
            <div className="rounded-full bg-danger/10 p-4 mb-4">
              <Zap className="h-8 w-8 text-danger" />
            </div>
            <h3 className="text-xl font-bold text-text-primary">Erreur de Récupération</h3>
            <p className="text-text-secondary max-w-sm mt-2">Impossible de charger vos séquences actuellement.</p>
        </div>
      </div>
    );
  }
  return (
    <div className="flex h-full flex-col space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Séquences</h1>
          <p className="text-sm text-text-secondary">Automatisez votre prospection multi-canal.</p>
        </div>
        <button 
          onClick={() => setActiveTab('builder')}
          className="inline-flex items-center justify-center rounded-xl bg-primary px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-dark transition-colors"
        >
          <Plus className="mr-2 h-4 w-4" />
          Nouvelle Séquence
        </button>
      </div>

      <div className="flex gap-4 border-b border-border">
        <button 
          onClick={() => setActiveTab('list')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'list' ? 'border-primary text-primary' : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border'}`}
        >
          Toutes les Séquences
        </button>
        <button 
          onClick={() => setActiveTab('builder')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'builder' ? 'border-primary text-primary' : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border'}`}
        >
          Éditeur de Séquence
        </button>
      </div>

      {activeTab === 'list' ? (
        sequences.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-border border-dashed bg-surface/50 p-12 text-center mt-6">
             <div className="rounded-full bg-primary/10 p-4 mb-4">
                <Zap className="h-8 w-8 text-primary" />
             </div>
             <h3 className="text-xl font-bold text-text-primary">Aucune Séquence</h3>
             <p className="text-text-secondary max-w-sm mt-2">Vous n'avez pas encore configuré de séquence d'outreach. Créez-en une pour automatiser votre prospection.</p>
             <button 
               onClick={() => setActiveTab('builder')}
               className="mt-4 inline-flex items-center justify-center rounded-xl bg-primary px-6 py-2 font-medium text-white transition-colors hover:bg-primary-dark"
             >
               <Plus className="mr-2 h-4 w-4" />
               Créer une Séquence
             </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mt-6">
          {sequences.map((seq) => (
            <div key={seq.id} className="rounded-xl border border-border bg-surface shadow-sm hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`rounded-lg p-2 ${seq.status === 'active' ? 'bg-success/10 text-success' : seq.status === 'paused' ? 'bg-warning/10 text-warning' : 'bg-secondary/10 text-secondary'}`}>
                      <Zap className="h-5 w-5" />
                    </div>
                    <h3 className="font-semibold text-text-primary">{seq.name}</h3>
                  </div>
                  <button title="More actions" className="text-text-secondary hover:text-primary transition-colors p-1 rounded-md hover:bg-background">
                    <MoreHorizontal className="h-5 w-5" />
                  </button>
                </div>
                
                <div className="mt-4 flex items-center gap-2">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border ${seq.status === 'active' ? 'bg-success/10 text-success border-success/20' : seq.status === 'paused' ? 'bg-warning/10 text-warning border-warning/20' : 'bg-secondary/10 text-secondary border-secondary/20'}`}>
                    {seq.status === 'active' && <Play className="mr-1 h-3 w-3" />}
                    {seq.status === 'paused' && <Pause className="mr-1 h-3 w-3" />}
                    {seq.status}
                  </span>
                  <span className="text-sm text-text-secondary">{seq.schedule}</span>
                </div>

                <div className="mt-6 grid grid-cols-2 gap-4 border-t border-border pt-4">
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">Taux d'ouverture</p>
                    <p className="mt-1 text-lg font-semibold text-text-primary">N/A</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">Taux de réponse</p>
                    <p className="mt-1 text-lg font-semibold text-text-primary">N/A</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        )
      ) : (
        <div className="flex flex-1 gap-6 overflow-hidden">
          {/* Builder Canvas */}
          <div className="flex-1 rounded-xl border border-border bg-background/50 p-6 overflow-y-auto flex flex-col items-center">
            <div className="w-full max-w-2xl space-y-4">
              {steps.map((step, index) => (
                <div key={step.id} className="relative">
                  {index > 0 && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 h-4 w-px bg-border flex items-center justify-center">
                      <ArrowRight className="h-3 w-3 text-text-secondary rotate-90 bg-background" />
                    </div>
                  )}
                  <div 
                    className={`rounded-xl border bg-surface p-4 shadow-sm transition-colors group cursor-pointer ${activeStep.id === step.id ? 'border-primary ring-1 ring-primary' : 'border-border hover:border-primary/50'}`}
                    onClick={() => setActiveStep(step)}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`rounded-lg p-2 shrink-0 ${
                        step.type === 'email' ? 'bg-primary/10 text-primary' :
                        step.type === 'wait' ? 'bg-warning/10 text-warning' :
                        step.type === 'sms' ? 'bg-secondary/10 text-secondary' :
                        step.type === 'instagram' ? 'bg-pink-500/10 text-pink-500' :
                        'bg-danger/10 text-danger'
                      }`}>
                        {step.type === 'email' && <Mail className="h-5 w-5" />}
                        {step.type === 'wait' && <Clock className="h-5 w-5" />}
                        {step.type === 'sms' && <MessageSquare className="h-5 w-5" />}
                        {step.type === 'instagram' && <Instagram className="h-5 w-5" />}
                        {step.type === 'condition' && <Settings className="h-5 w-5" />}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-text-primary">{step.title}</h4>
                        <p className="mt-1 text-sm text-text-secondary line-clamp-2 whitespace-pre-wrap font-mono bg-background p-2 rounded-md border border-border/50">
                          {step.content}
                        </p>
                      </div>
                      <button title="More actions" className="opacity-0 group-hover:opacity-100 text-text-secondary hover:text-primary transition-opacity p-1 rounded-md hover:bg-background">
                        <MoreHorizontal className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              
              <div className="flex justify-center pt-4">
                <button title="Add step" className="inline-flex items-center justify-center rounded-full border border-dashed border-border bg-surface p-3 text-text-secondary hover:border-primary hover:text-primary transition-colors shadow-sm">
                  <Plus className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Editor Sidebar */}
          <div className="w-96 rounded-xl border border-border bg-surface shadow-sm flex flex-col">
            <div className="border-b border-border p-4">
              <h3 className="font-semibold text-text-primary">Éditer l'étape: {activeStep.title}</h3>
            </div>
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              {activeStep.type === 'email' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-text-primary">Sujet (A/B Testing)</label>
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-md font-medium">A/B Activé</span>
                  </div>
                  <div className="space-y-3">
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <span className="text-xs font-bold text-text-secondary">A</span>
                      </div>
                      <input 
                        type="text" 
                        title="Variante A"
                        defaultValue={activeStep.content.split('\n\n')[0].replace('Objet : ', '')}
                        className="w-full rounded-lg border border-border bg-background pl-8 pr-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder="Variante A"
                      />
                    </div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <span className="text-xs font-bold text-text-secondary">B</span>
                      </div>
                      <input 
                        type="text" 
                        title="Variante B"
                        defaultValue="Question pour {{company_name}}"
                        className="w-full rounded-lg border border-border bg-background pl-8 pr-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder="Variante B"
                      />
                    </div>
                  </div>
                </div>
              )}
              <div className="space-y-2 flex-1 flex flex-col">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-text-primary">Contenu</label>
                  <button className="text-xs text-primary hover:underline">Insérer Variable</button>
                </div>
                <div className="rounded-lg border border-border bg-background flex-1 flex flex-col overflow-hidden">
                  {/* WYSIWYG Toolbar Mock */}
                  {(activeStep.type === 'email' || activeStep.type === 'sms' || activeStep.type === 'instagram') && (
                    <div className="flex items-center gap-2 border-b border-border p-2 bg-surface">
                      <button title="Bold" className="p-1 rounded hover:bg-background text-text-secondary font-bold">B</button>
                      <button title="Italic" className="p-1 rounded hover:bg-background text-text-secondary italic">I</button>
                      <button title="Underline" className="p-1 rounded hover:bg-background text-text-secondary underline">U</button>
                      <div className="w-px h-4 bg-border mx-1"></div>
                      <button title="Link" className="p-1 rounded hover:bg-background text-text-secondary">🔗</button>
                    </div>
                  )}
                  <textarea 
                    title="Contenu"
                    className="w-full flex-1 resize-none bg-transparent p-3 text-sm text-text-primary focus:outline-none font-mono"
                    defaultValue={activeStep.type === 'email' ? activeStep.content.split('\n\n').slice(1).join('\n\n') : activeStep.content}
                  />
                </div>
              </div>
            </div>
            <div className="border-t border-border p-4 flex justify-end gap-3">
              <button className="rounded-xl border border-border bg-surface px-4 py-2 text-sm font-medium text-text-primary hover:bg-background transition-colors">
                Annuler
              </button>
              <button className="rounded-xl bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark transition-colors">
                Sauvegarder
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
