# Guide d'Intégration Frontend — Uprising ColdOutreach

Ce guide explique comment construire un frontend pour interagir avec le backend FastAPI de **Uprising ColdOutreach**.

## 🏗️ Architecture Recommandée

- **Framework** : React 18+ (généré avec Vite)
- **Routage** : React Router v6
- **Styling** : Tailwind CSS + shadcn/ui
- **Appels API** : Axios ou Fetch + React Query (TanStack Query)
- **State Management** : Zustand (pour l'état global ex: auth)
- **Formulaires** : React Hook Form + Zod

### 🚀 Commandes d'initialisation (React + Vite)

```bash
npm create vite@latest uprising-frontend -- --template react-ts
cd uprising-frontend
npm install
npm install axios @tanstack/react-query react-router-dom zustand
npm install react-hook-form @hookform/resolvers zod
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

*(Après ça, vous pouvez installer shadcn/ui via `npx shadcn@latest init`)*

## 1. Authentification (JWT)

Le backend utilise des tokens JWT pour sécuriser l'API.

- **Inscription** : `POST /api/v1/auth/register`
- **Connexion** : `POST /api/v1/auth/login` (retourne `access_token`)
- **Stockage du Token** : Stockez le token dans le `localStorage` ou un cookie HttpOnly sécurisé. Ce token doit être envoyé dans l'en-tête `Authorization: Bearer <TOKEN>` pour chaque requête protégée.

## 2. Tableau de Bord (Dashboard)

Utilisez des cartes analytiques (shadcn/ui `Card`) pour afficher les métriques clés.

- **Endpoints** :
  - `GET /api/v1/analytics/overview` : Récupère les totaux (leads, séquences actives, emails envoyés, taux de réponse).

## 3. Gestion des Leads (Leads Management)

Un tableau avec recherche, pagination et filtrage pour gérer les prospects.

- **Endpoints** :
  - `GET /api/v1/leads/` : Liste paginée des leads.
  - `POST /api/v1/leads/` : Créer un lead manuellement.
  - `POST /api/v1/leads/csv-import` : Importer via un fichier CSV (utilisez un champ `<input type="file">` upload).
  - `GET /api/v1/leads/csv-export` : Télécharger un export CSV.

## 4. Scraping Google Maps Multi-Recherche

Créez une interface pour lancer des jobs de scraping via Apify.

- **Interface** : Un formulaire dynamique permettant d'ajouter plusieurs lignes de recherche (ex: "plombier à Paris", "électricien à Lyon").
- **Endpoints** :
  - `POST /api/v1/multi-search/` : Envoie la requête batch pour scraping.
  - `GET /api/v1/multi-search/{job_id}` : Polling pour afficher la progression (status: `RUNNING` -> `SUCCEEDED`). L'interface devrait faire un polling toutes les 5-10 secondes.

## 5. Pipelines & CRM

Une vue Kanban (façon Trello/GoHighLevel) pour visualiser les étapes de vente.

- **Composant UI** : `@hello-pangea/dnd` ou `react-beautiful-dnd` pour le drag-and-drop.
- **Endpoints** :
  - `GET /api/v1/pipelines/` : Récupérer tous les pipelines et leurs statuts.
  - `PUT /api/v1/leads/{lead_id}/status` : Mettre à jour le statut du lead lors du drag-and-drop (ex: de "COLD" à "REPLIED").

## 6. Constructeur de Séquences (Sequence Builder)

L'outil le plus complexe : un éditeur visuel pour créer des séquences multicanales step-by-step.

- **Interface** : Un constructeur type "Node-based" (React Flow) ou un formulaire dynamique vertical.
- **Canaux supportés par étape** : `email`, `sms`, `instagram`.
- **Endpoints** :
  - `POST /api/v1/sequences/` : Créer la séquence.
  - `POST /api/v1/sequences/{id}/steps` : Ajouter des étapes (avec délai `delay_days`).
  - `POST /api/v1/sequences/{id}/enroll` : Inscrire des leads à cette séquence.

## 7. Configuration des Intégrations

Une page de paramètres pour connecter les comptes externes.

- **Gmail API** : Bouton "Se connecter avec Google". Redirige vers `POST /api/v1/integrations/gmail/connect`.
- **Instagram DM** : Bouton "Connecter Instagram (Facebook)". Redirige vers `POST /api/v1/integrations/instagram/connect`.
- **Apify / SMS** : Champs pour entrer la clé API Apify et la clé TextBelt, renvoyés au backend via les paramètres ou configurés via `.env` côté serveur.

## 8. Webhooks & Automatisation

Permet aux utilisateurs de configurer des webhooks sortants ("catch hooks") pour Zapier/Make.

- **Endpoints** :
  - `POST /api/v1/webhooks/` : Enregistrer un webhook de réception pour les réponses entrantes.

## 💡 Conseils Additionnels

- **A/B Testing** : Affichez deux variantes (`variant_a` et `variant_b`) pour les sujets d'emails dans l'interface de séquence et affichez les statistiques d'ouverture respectives via `GET /api/v1/analytics/ab-test-results`.
- **ICP Scoring** : Affichez la métrique "Heat/Score" (ex: 85/100) à côté de chaque lead grâce à l'appel `GET /api/v1/leads/{id}/score`. Affichez-le avec une icône de flamme (🔥) pour l'identité visuelle.
