import { useState, useEffect } from 'react';
import { Loader2, ExternalLink, Calendar, GitPullRequest, Tag } from 'lucide-react';

interface Release {
  id: number;
  name: string;
  tag_name: string;
  body: string;
  published_at: string;
  html_url: string;
}

export function Changelog() {
  const [releases, setReleases] = useState<Release[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://api.github.com/repos/Endsider/Uprising-coldoutreach/releases')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setReleases(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch changelog", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-text-secondary">Chargement de l'historique des versions...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-8">
      <div>
        <h1 className="text-3xl font-bold text-text-primary tracking-tight">Changelog & Nouveautés</h1>
        <p className="mt-2 text-sm text-text-secondary">
          Suivez toutes les améliorations, les corrections de bugs et les nouvelles fonctionnalités ajoutées à Uprising.
        </p>
      </div>

      {releases.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-border border-dashed bg-surface/50 p-12 text-center">
          <GitPullRequest className="h-8 w-8 text-primary mb-4" />
          <h3 className="text-xl font-bold text-text-primary">Aucune note de version</h3>
          <p className="text-text-secondary mt-2">Les mises à jour apparaîtront ici lors du prochain déploiement.</p>
        </div>
      ) : (
        <div className="relative border-l border-border ml-3 md:ml-6 space-y-12 pb-8">
          {releases.map((release) => (
            <div key={release.id} className="relative pl-8 md:pl-12">
              {/* Timeline dot */}
              <div className="absolute -left-[5px] top-1 h-2.5 w-2.5 rounded-full bg-primary ring-4 ring-background" />

              <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center rounded-lg bg-primary/10 px-2.5 py-1 text-sm font-semibold text-primary">
                    <Tag className="w-3 h-3 mr-1.5" />
                    {release.tag_name}
                  </span>
                  <h2 className="text-xl font-bold text-text-primary">{release.name || release.tag_name}</h2>
                </div>
                <div className="flex items-center text-sm text-text-secondary ml-auto md:ml-0">
                  <Calendar className="w-4 h-4 mr-1.5" />
                  {new Date(release.published_at).toLocaleDateString('fr-CA', { year: 'numeric', month: 'long', day: 'numeric' })}
                </div>
              </div>

              <div className="prose prose-sm md:prose-base prose-invert prose-p:text-text-secondary prose-li:text-text-secondary max-w-none bg-surface border border-border rounded-xl p-5 shadow-sm">
                {release.body.split('\n').map((line, i) => {
                  if (line.startsWith('## ')) return <h3 key={i} className="text-lg font-semibold text-text-primary mt-4 mb-2">{line.replace('## ', '')}</h3>;
                  if (line.startsWith('# ')) return <h2 key={i} className="text-xl font-bold text-text-primary mt-5 mb-3">{line.replace('# ', '')}</h2>;
                  if (line.startsWith('- ')) return <div key={i} className="ml-4 mb-1 flex items-start"><span className="mr-2">•</span><span>{line.replace('- ', '')}</span></div>;
                  if (line.startsWith('* ')) return <div key={i} className="ml-4 mb-1 flex items-start"><span className="mr-2">•</span><span>{line.replace('* ', '')}</span></div>;
                  if (line.trim() === '') return <br key={i} />;
                  return <p key={i} className="mb-2">{line}</p>;
                })}
              </div>

              <a 
                href={release.html_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center text-sm font-medium text-primary hover:text-primary-dark mt-4 transition-colors"
              >
                Voir sur GitHub <ExternalLink className="w-4 h-4 ml-1.5" />
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
