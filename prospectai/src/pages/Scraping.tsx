import { useState } from 'react';
import { Search, Plus, Trash2, Play, Loader2, MapPin, CheckCircle2 } from 'lucide-react';
import { useMapsJobs, useStartScraping } from '../api/queries';

export function Scraping() {
  const [queries, setQueries] = useState<string[]>(['plombier à Montréal']);
  const { data: jobs = [] } = useMapsJobs();
  const { mutate: startScrapingAction, isPending: isScraping } = useStartScraping();

  const addQuery = () => {
    setQueries([...queries, '']);
  };

  const updateQuery = (index: number, value: string) => {
    const newQueries = [...queries];
    newQueries[index] = value;
    setQueries(newQueries);
  };

  const removeQuery = (index: number) => {
    const newQueries = [...queries];
    newQueries.splice(index, 1);
    setQueries(newQueries);
  };

  const startScraping = () => {
    const validQueries = queries.filter(q => q.trim() !== '');
    if (validQueries.length === 0) return;

    // Formatting it into expected { query, location } structure
    const formattedQueries = validQueries.map(q => {
      // Very basic extraction logic or just pass entire format to query if location is merged
      const parts = q.split('à');
      if (parts.length > 1) {
          return { query: parts[0].trim(), location: parts[1].trim() };
      }
      return { query: q, location: '' };
    });

    startScrapingAction(formattedQueries);
  };

  return (
    <div className="flex h-full flex-col space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Scraping Google Maps</h1>
          <p className="text-sm text-text-secondary">Extrayez des prospects qualifiés directement depuis Google Maps via Apify.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-4">
          <div className="rounded-2xl border border-border bg-surface p-6 shadow-sm space-y-4">
            <h2 className="font-semibold text-text-primary flex items-center gap-2">
              <MapPin className="w-5 h-5 text-primary" />
              Requêtes de recherche
            </h2>
            <p className="text-xs text-text-secondary">Ajoutez plusieurs requêtes pour lancer un scraping en lot.</p>
            
            <div className="space-y-3">
              {queries.map((query, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="relative flex-1">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <Search className="h-4 w-4 text-text-secondary" />
                    </div>
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => updateQuery(index, e.target.value)}
                      placeholder="ex: plombier à Paris"
                      className="w-full rounded-xl border border-border bg-background pl-9 pr-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>
                  {queries.length > 1 && (
                    <button 
                      title="Remove query"
                      onClick={() => removeQuery(index)}
                      className="p-2 text-text-secondary hover:text-danger hover:bg-danger/10 rounded-xl transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            <button 
              onClick={addQuery}
              className="w-full py-2 border border-dashed border-border rounded-xl text-sm font-medium text-text-secondary hover:border-primary hover:text-primary transition-colors flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Ajouter une requête
            </button>

            <div className="pt-4 border-t border-border">
              <button 
                onClick={startScraping}
                disabled={isScraping || queries.every(q => q.trim() === '')}
                className={`w-full py-2.5 rounded-xl text-sm font-medium text-white flex items-center justify-center gap-2 transition-colors ${
                  isScraping || queries.every(q => q.trim() === '') ? 'bg-primary/50 cursor-not-allowed' : 'bg-primary hover:bg-primary-dark shadow-sm'
                }`}
              >
                {isScraping ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Scraping en cours...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Lancer le Scraping
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-2xl border border-border bg-surface p-6 shadow-sm min-h-[400px]">
            <h2 className="font-semibold text-text-primary mb-4">Historique & Progression</h2>
            
            {jobs.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-center">
                <div className="w-16 h-16 bg-background rounded-full flex items-center justify-center mb-4">
                  <Search className="w-8 h-8 text-text-secondary" />
                </div>
                <h3 className="text-lg font-medium text-text-primary">Aucun job récent</h3>
                <p className="text-sm text-text-secondary mt-2 max-w-sm">
                  Lancez une recherche pour voir la progression et les résultats ici.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {jobs.map(job => (
                  <div key={job.id} className="flex items-center justify-between p-4 border border-border rounded-xl bg-background">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        job.status === 'SUCCEEDED' ? 'bg-success/10 text-success' :
                        job.status === 'RUNNING' ? 'bg-primary/10 text-primary' :
                        job.status === 'FAILED' ? 'bg-danger/10 text-danger' :
                        'bg-secondary/10 text-secondary'
                      }`}>
                        {job.status === 'SUCCEEDED' ? <CheckCircle2 className="w-5 h-5" /> :
                         job.status === 'RUNNING' ? <Loader2 className="w-5 h-5 animate-spin" /> :
                         <Search className="w-5 h-5" />}
                      </div>
                      <div>
                        <h4 className="font-medium text-text-primary text-sm">{job.search_queries?.[0] || 'Recherche'}</h4>
                        <p className="text-xs text-text-secondary mt-0.5">ID: {job.id}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border ${
                          job.status === 'SUCCEEDED' ? 'bg-success/10 text-success border-success/20' :
                          job.status === 'RUNNING' ? 'bg-primary/10 text-primary border-primary/20' :
                          job.status === 'FAILED' ? 'bg-danger/10 text-danger border-danger/20' :
                          'bg-secondary/10 text-secondary border-secondary/20'
                        }`}>
                          {job.status === 'RUNNING' ? 'EN COURS' :
                           job.status === 'SUCCEEDED' ? 'TERMINÉ' :
                           job.status === 'FAILED' ? 'ÉCHOUÉ' : 'EN ATTENTE'}
                        </span>
                        {job.status === 'SUCCEEDED' && (
                          <p className="text-xs font-medium text-text-primary mt-1">{job.total_found} prospects trouvés</p>
                        )}
                      </div>
                      
                      {job.status === 'SUCCEEDED' && (
                        <button className="px-3 py-1.5 bg-surface border border-border text-text-primary rounded-lg text-xs font-medium hover:bg-background transition-colors">
                          Voir les leads
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
