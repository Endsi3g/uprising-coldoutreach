import { useState, useEffect } from 'react';
import { Loader2, ExternalLink, Calendar, GitCommit } from 'lucide-react';

interface GitHubCommit {
  sha: string;
  commit: {
    message: string;
    author: {
      name: string;
      date: string;
    };
  };
  html_url: string;
}

export function Changelog() {
  const [commits, setCommits] = useState<GitHubCommit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://api.github.com/repos/Endsider/Uprising-coldoutreach/commits?per_page=10')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setCommits(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch changelog commits", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-text-secondary">Chargement de l'historique des modifications...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-8">
      <div>
        <h1 className="text-3xl font-bold text-text-primary tracking-tight">Changelog & Nouveautés</h1>
        <p className="mt-2 text-sm text-text-secondary">
          Suivez toutes les améliorations et corrections apportées à l'application via les dernières mises à jour (Commits).
        </p>
      </div>

      {commits.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-border border-dashed bg-surface/50 p-12 text-center">
          <GitCommit className="h-8 w-8 text-primary mb-4" />
          <h3 className="text-xl font-bold text-text-primary">Aucun commit trouvé</h3>
          <p className="text-text-secondary mt-2">Les mises à jour apparaîtront ici lors du prochain déploiement.</p>
        </div>
      ) : (
        <div className="relative border-l border-border ml-3 md:ml-6 space-y-8 pb-8">
          {commits.map((c) => (
            <div key={c.sha} className="relative pl-8 md:pl-12">
              {/* Timeline dot */}
              <div className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full bg-primary ring-4 ring-background" />

              <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-3">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center rounded-lg bg-primary/10 px-2.5 py-1 text-sm font-mono font-semibold text-primary">
                    <GitCommit className="w-3 h-3 mr-1.5" />
                    {c.sha.substring(0, 7)}
                  </span>
                  <div className="flex items-center text-sm text-text-secondary ml-auto md:ml-0">
                    <Calendar className="w-4 h-4 mr-1.5" />
                    {new Date(c.commit.author.date).toLocaleString('fr-CA', { 
                        year: 'numeric', month: 'long', day: 'numeric', 
                        hour: '2-digit', minute:'2-digit' 
                    })}
                  </div>
                </div>
              </div>

              <div className="prose prose-sm md:prose-base prose-invert prose-p:text-text-secondary max-w-none bg-surface border border-border rounded-xl p-4 shadow-sm">
                <p className="font-medium text-text-primary mb-2 whitespace-pre-wrap">
                  {c.commit.message}
                </p>
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-border">
                  <div className="text-xs text-text-secondary">
                    Par <span className="font-semibold text-text-primary">{c.commit.author.name}</span>
                  </div>
                  <a 
                    href={c.html_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-xs font-medium text-primary hover:text-primary-dark transition-colors"
                  >
                    Voir sur GitHub <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
