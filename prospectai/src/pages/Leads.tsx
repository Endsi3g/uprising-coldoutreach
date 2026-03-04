import { useState } from 'react';
import { Search, Filter, Download, MoreHorizontal, ChevronRight, CheckSquare, Square, Mail, Phone, Building2, Zap, User, Flame, Plus, Upload, Loader2 } from 'lucide-react';
import { useLeads } from '../api/queries';

const stages = {
  'New': 'bg-secondary/10 text-secondary border-secondary/20',
  'Contacted': 'bg-warning/10 text-warning border-warning/20',
  'Replied': 'bg-primary/10 text-primary border-primary/20',
  'Hot': 'bg-danger/10 text-danger border-danger/20',
  'Booked': 'bg-success/10 text-success border-success/20',
};

export function Leads() {
  const { data: leads = [], isLoading } = useLeads();
  const [selectedLeads, setSelectedLeads] = useState<number[]>([]);
  const [selectedLeadDetails, setSelectedLeadDetails] = useState<number | null>(null);
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [enrollProgress, setEnrollProgress] = useState(0);
  const [totalToEnroll, setTotalToEnroll] = useState(0);

  const toggleLead = (id: number) => {
    setSelectedLeads(prev => prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id]);
  };

  const toggleAll = () => {
    if (selectedLeads.length === leads.length) {
      setSelectedLeads([]);
    } else {
      setSelectedLeads(leads.map(l => l.id));
    }
  };

  const handleEnroll = () => {
    if (selectedLeads.length === 0) return;
    setIsEnrolling(true);
    setTotalToEnroll(selectedLeads.length);
    setEnrollProgress(0);

    let progress = 0;
    const interval = setInterval(() => {
      progress += 1;
      setEnrollProgress(progress);
      if (progress >= selectedLeads.length) {
        clearInterval(interval);
        setTimeout(() => {
          setIsEnrolling(false);
          setSelectedLeads([]);
        }, 1000);
      }
    }, 400); // 400ms per lead for visual effect
  };

  const activeLead = leads.find(l => l.id === selectedLeadDetails);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Prospects</h1>
          <p className="text-sm text-text-secondary">Gérez vos prospects et campagnes.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <input type="file" id="csv-upload" className="hidden" accept=".csv" />
            <label htmlFor="csv-upload" title="Import" className="inline-flex items-center justify-center rounded-xl border border-border bg-surface px-4 py-2 text-sm font-medium text-text-primary shadow-sm hover:bg-background transition-colors cursor-pointer">
              <Upload className="mr-2 h-4 w-4" />
              Importer CSV
            </label>
          </div>
          <button title="Export" className="inline-flex items-center justify-center rounded-xl border border-border bg-surface px-4 py-2 text-sm font-medium text-text-primary shadow-sm hover:bg-background transition-colors">
            <Download className="mr-2 h-4 w-4" />
            Exporter CSV
          </button>
          <button title="New lead" className="inline-flex items-center justify-center rounded-xl bg-primary px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-dark transition-colors">
            <Plus className="mr-2 h-4 w-4" />
            Nouveau Prospect
          </button>
          <button 
            title="Enroll"
            onClick={handleEnroll}
            disabled={selectedLeads.length === 0 || isEnrolling}
            className={`inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors ${
              selectedLeads.length === 0 || isEnrolling 
                ? 'bg-primary/50 cursor-not-allowed' 
                : 'bg-primary hover:bg-primary-dark'
            }`}
          >
            <Zap className="mr-2 h-4 w-4" />
            {isEnrolling ? 'Enrôlement...' : 'Enrôler la sélection'}
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      {isEnrolling && (
        <div className="rounded-xl border border-primary/20 bg-primary/5 p-4 shadow-sm transition-all duration-300">
          <div className="flex justify-between text-sm mb-2">
            <span className="font-medium text-primary">Enrôlement en cours...</span>
            <span className="text-text-secondary">{enrollProgress} / {totalToEnroll} prospects</span>
          </div>
          <div className="w-full bg-border rounded-full h-2 overflow-hidden">
            {/* eslint-disable-next-line */}
            {/* NOSONAR */}
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300 ease-out" 
              style={{ width: `${(enrollProgress / totalToEnroll) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center gap-4 rounded-xl border border-border bg-surface p-4 shadow-sm">
        <div className="relative flex-1 min-w-[200px]">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Search className="h-4 w-4 text-text-secondary" />
          </div>
          <input
            type="text"
            title="Search lead"
            className="block w-full rounded-lg border-0 py-2 pl-10 pr-3 text-text-primary ring-1 ring-inset ring-border placeholder:text-text-secondary focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6 bg-background"
            placeholder="Rechercher un lead..."
          />
        </div>
        
        <div className="flex items-center gap-2">
          <button title="Stage filter" className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-text-primary hover:bg-border/50 transition-colors">
            <Filter className="h-4 w-4 text-text-secondary" />
            Étape
          </button>
          <button title="Score filter" className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-text-primary hover:bg-border/50 transition-colors">
            Score ICP
          </button>
          <button title="City filter" className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-text-primary hover:bg-border/50 transition-colors">
            Ville
          </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="flex-1 overflow-hidden rounded-xl border border-border bg-surface shadow-sm flex relative">
        <div className={`flex-1 overflow-auto transition-all duration-300 ${selectedLeadDetails ? 'mr-[400px]' : ''}`}>
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-background sticky top-0 z-10">
              <tr>
                <th scope="col" className="relative px-4 sm:w-12 sm:px-6">
                  <button title="Select all" onClick={toggleAll} className="text-text-secondary hover:text-primary">
                    {selectedLeads.length === leads.length ? (
                      <CheckSquare className="h-5 w-5" />
                    ) : (
                      <Square className="h-5 w-5" />
                    )}
                  </button>
                </th>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">Entreprise</th>
                <th scope="col" className="px-3 py-3.5 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">Contact</th>
                <th scope="col" className="px-3 py-3.5 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">ICP / Chaleur</th>
                <th scope="col" className="px-3 py-3.5 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">Étape</th>
                <th scope="col" className="px-3 py-3.5 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">Tags</th>
                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-surface">
              {leads.map((lead) => (
                <tr 
                  key={lead.id} 
                  className={`hover:bg-background/50 transition-colors cursor-pointer ${selectedLeadDetails === lead.id ? 'bg-background' : ''}`}
                  onClick={() => setSelectedLeadDetails(lead.id)}
                >
                  <td className="relative px-4 sm:w-12 sm:px-6" onClick={(e) => e.stopPropagation()}>
                    <button title="Toggle lead" onClick={() => toggleLead(lead.id)} className="text-text-secondary hover:text-primary">
                      {selectedLeads.includes(lead.id) ? (
                        <CheckSquare className="h-5 w-5 text-primary" />
                      ) : (
                        <Square className="h-5 w-5" />
                      )}
                    </button>
                  </td>
                  <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm">
                    <div className="flex items-center">
                      <div className="h-10 w-10 shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                        {lead.company_name?.charAt(0) || '?'}
                      </div>
                      <div className="ml-4">
                        <div className="font-medium text-text-primary">{lead.company_name}</div>
                        <div className="text-text-secondary">{lead.city}</div>
                      </div>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-text-secondary">
                    <div className="text-text-primary">{lead.contact_name}</div>
                    <div className="text-xs">{lead.email}</div>
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="flex flex-col gap-1 w-16">
                        <div className="flex justify-between text-xs">
                          <span className="text-text-secondary">ICP</span>
                          <span className="font-medium text-text-primary">{lead.icp_score}</span>
                        </div>
                        <div className="w-full bg-border rounded-full h-1.5">
                          {/* eslint-disable-next-line */}
                          {/* NOSONAR */}
                          <div className="bg-primary h-1.5 rounded-full" style={{ width: `${lead.icp_score}%` }}></div>
                        </div>
                      </div>
                      <div className="flex flex-col gap-1 w-16">
                        <div className="flex justify-between text-xs">
                          <span className="text-text-secondary">Chaleur</span>
                          <span className="font-medium text-danger flex items-center gap-0.5"><Flame className="w-3 h-3" /> {lead.heat_score}</span>
                        </div>
                        <div className="w-full bg-border rounded-full h-1.5">
                          {/* eslint-disable-next-line */}
                          {/* NOSONAR */}
                          <div className="bg-danger h-1.5 rounded-full" style={{ width: `${lead.heat_score}%` }}></div>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border ${stages[(lead.status || 'New') as keyof typeof stages] || stages['New']}`}>
                      {lead.status || 'New'}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm">
                    <div className="flex gap-1">
                      {lead.tags?.map(tag => (
                        <span key={tag} className="inline-flex items-center rounded-md bg-background px-2 py-1 text-xs font-medium text-text-secondary ring-1 ring-inset ring-border">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6" onClick={(e) => e.stopPropagation()}>
                    <button title="More actions" className="text-text-secondary hover:text-primary transition-colors p-1 rounded-md hover:bg-background">
                      <MoreHorizontal className="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Sidebar Detail */}
        {activeLead && (
          <div className="absolute top-0 right-0 h-full w-[400px] bg-surface border-l border-border shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col z-20">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h2 className="text-lg font-semibold text-text-primary">Détails du prospect</h2>
              <button 
                title="Fermer"
                onClick={() => setSelectedLeadDetails(null)}
                className="p-1 rounded-md text-text-secondary hover:bg-background hover:text-text-primary transition-colors"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Header Info */}
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-primary text-2xl font-bold uppercase">
                  {activeLead.company_name?.charAt(0) || '?'}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-text-primary">{activeLead.company_name}</h3>
                  <p className="text-sm text-text-secondary flex items-center gap-1 mt-1">
                    <Building2 className="h-4 w-4" /> {activeLead.city}
                  </p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-2 gap-3">
                <button className="flex items-center justify-center gap-2 rounded-xl bg-primary px-3 py-2 text-sm font-medium text-white hover:bg-primary-dark transition-colors">
                  <Zap className="h-4 w-4" /> Enrôler
                </button>
                <button className="flex items-center justify-center gap-2 rounded-xl border border-border bg-surface px-3 py-2 text-sm font-medium text-text-primary hover:bg-background transition-colors">
                  <Mail className="h-4 w-4" /> Email
                </button>
              </div>

              {/* Contact Info */}
              <div className="rounded-xl border border-border p-4 space-y-3">
                <h4 className="text-sm font-semibold text-text-primary uppercase tracking-wider">Contact</h4>
                <div className="flex items-center gap-3 text-sm text-text-secondary">
                  <User className="h-4 w-4 text-text-primary" />
                  <span className="font-medium text-text-primary">{activeLead.contact_name}</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-text-secondary">
                  <Mail className="h-4 w-4 text-text-primary" />
                  <a href={`mailto:${activeLead.email}`} className="hover:text-primary transition-colors">{activeLead.email}</a>
                </div>
                <div className="flex items-center gap-3 text-sm text-text-secondary">
                  <Phone className="h-4 w-4 text-text-primary" />
                  <a href={`tel:${activeLead.phone}`} className="hover:text-primary transition-colors">{activeLead.phone}</a>
                </div>
              </div>

              {/* Scores */}
              <div className="rounded-xl border border-border p-4 space-y-4">
                <h4 className="text-sm font-semibold text-text-primary uppercase tracking-wider">Scores</h4>
                
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Profil Client Idéal (ICP)</span>
                    <span className="font-bold text-text-primary">{activeLead.icp_score}/100</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-2">
                    {/* eslint-disable-next-line */}
                    {/* NOSONAR */}
                    <div className="bg-primary h-2 rounded-full" style={{ width: `${activeLead.icp_score}%` }}></div>
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Score de chaleur</span>
                    <span className="font-bold text-danger flex items-center gap-1"><Flame className="w-4 h-4" /> {activeLead.heat_score}/100</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-2">
                    {/* eslint-disable-next-line */}
                    {/* NOSONAR */}
                    <div className="bg-danger h-2 rounded-full" style={{ width: `${activeLead.heat_score}%` }}></div>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-text-primary uppercase tracking-wider">Historique d'activité</h4>
                <div className="flow-root">
                  <ul role="list" className="-mb-8">
                    <li className="relative pb-8">
                      <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-border" aria-hidden="true" />
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center ring-8 ring-surface">
                            <Mail className="h-4 w-4 text-primary" />
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-text-secondary">Email ouvert <span className="font-medium text-text-primary">Séquence 1</span></p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-text-secondary">
                            <time>il y a 1h</time>
                          </div>
                        </div>
                      </div>
                    </li>
                    <li className="relative pb-8">
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-warning/10 flex items-center justify-center ring-8 ring-surface">
                            <Zap className="h-4 w-4 text-warning" />
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-text-secondary">Enrôlé dans <span className="font-medium text-text-primary">Cold Email Entrepreneurs</span></p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-text-secondary">
                            <time>il y a 2j</time>
                          </div>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
