# 🚀 Uprising ColdOutreach — Open-Source Prospecting Backend

**GoHighLevel-like prospecting automation** — 100% gratuit, open-source.
Google Maps scraping, email sequences, SMS (TextBelt), Instagram DMs, Gmail API, CRM pipelines, ICP/Heat scoring, A/B testing.

## ⚡ Installation (3 commandes)

```bash
# Option A: Docker (recommandé)
cp .env.example .env        # configurer vos clés
docker-compose up -d         # lance postgres + redis + api + celery + scheduler
# → http://localhost:8000/docs

# Option B: Local
pip install -r requirements.txt
# Démarrer postgres + redis séparément
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## 🏗️ Stack

| Layer | Tech |
| ----- | ---- |
| API | FastAPI + Pydantic |
| DB | PostgreSQL + SQLAlchemy + Alembic |
| Jobs | Celery + Redis |
| Scheduler | APScheduler (séquences 2min, IMAP 5min, reset midnight) |
| Scraping | Apify Google Maps (free tier) |
| Email | Gmail SMTP (500/jour) + Gmail API OAuth |
| SMS | TextBelt (open-source, gratuit) |
| Instagram | Graph API DMs (Facebook Business) |
| Auth | JWT (python-jose + bcrypt) |

## 🔌 Channels Supportés

| Channel | Service | Coût |
| ------- | ------- | ---- |
| Email (SMTP) | Gmail App Password | Gratuit (500/jour) |
| Email (API) | Gmail OAuth2 | Gratuit (meilleure délivrabilité) |
| SMS | TextBelt | Gratuit (1/jour) ou $0.005/SMS |
| Instagram DM | Graph API | Gratuit |
| IMAP Reply | Détection automatique | Gratuit |

## 🎯 Test End-to-End

```bash
# 1. Créer compte + login
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"MyCo","time_zone":"America/Montreal","email":"admin@test.com","password":"secret123","role":"admin"}'

curl -X POST http://localhost:8000/auth/login \
  -d '{"email":"admin@test.com","password":"secret123"}'
# → Copier access_token

# 2. Multi-Scraper Google Maps (batch)
curl -X POST http://localhost:8000/multi-search \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"searches":[
    {"query":"plombier","location":"Laval, QC","max_items":10},
    {"query":"électricien","location":"Montréal, QC","max_items":10}
  ]}'

# 3. Import CSV de leads
curl -X POST http://localhost:8000/leads/csv-import \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@leads.csv"

# 4. Export CSV
curl http://localhost:8000/leads/csv-export \
  -H "Authorization: Bearer <TOKEN>" -o leads_export.csv

# 5. Connecter Gmail OAuth
curl -X POST http://localhost:8000/integrations/gmail/connect \
  -H "Authorization: Bearer <TOKEN>"
# → Ouvrir l'URL retournée dans le navigateur

# 6. Connecter Instagram
curl -X POST http://localhost:8000/integrations/instagram/connect \
  -H "Authorization: Bearer <TOKEN>"
```

## 🧪 Tests

```bash
pytest tests/ -v --tb=short
```

## 📊 API Docs

Ouvrir **<http://localhost:8000/docs>** (Swagger UI) ou **/redoc**.

## 🗺️ Roadmap v3 (Fait ✅)

- [x] Multi-search batch scraping avec déduplication
- [x] SMS via TextBelt (alternative Twilio gratuite)
- [x] Gmail API OAuth (meilleure délivrabilité)
- [x] Instagram DM automation (Graph API)
- [x] Reply parsing IMAP (détection automatique)
- [x] Webhook receiver pour replies
- [x] CSV import/export leads
- [x] Rate limiting par identity (daily reset)
- [x] A/B testing subject lines

## 🤖 Intégration Apify (Actor & MCP)

### 1. Actor Playwright Customisé (`/actor`)

Le projet contient maintenant un Actor Apify pré-configuré pour scrapper avec **Playwright**.

1. Installez le CLI Apify : `npm -g install apify-cli`
2. Connectez-vous : `apify login`
3. Déployez : `cd actor && apify push`

### 2. Service MCP (Model Context Protocol)

Intégrez Apify avec les agents locaux via MCP.
Un fichier `apify-mcp.json` est inclus à la racine. Utilisez-le avec votre environnement (ex: Claude Desktop, Antigravity) pour donner accès aux outils Apify :
`https://mcp.apify.com/?tools=actors,docs,experimental,runs,storage,compass/crawler-google-places`

### 3. Guide Frontend

Un guide détaillé pour la construction du Frontend (App Router, dashboards, CRM) est disponible dans **`docs/FRONTEND_GUIDE.md`**.

## 📐 Architecture

```text
app/
├── main.py          # FastAPI app + 11 routers
├── models.py        # 12 SQLAlchemy models + A/B testing
├── schemas.py       # Pydantic request/response
├── core/            # config, security, database
├── crud/            # leads, sequences, pipelines, messages
├── services/
│   ├── apify.py     # Google Maps scraping
│   ├── email.py     # SMTP email + tracking
│   ├── gmail.py     # Gmail API OAuth
│   ├── sms.py       # TextBelt SMS
│   ├── instagram.py # Instagram DM Graph API
│   ├── imap.py      # IMAP reply detection
│   └── scoring.py   # ICP/Heat scoring
├── api/v1/
│   ├── auth.py           # register/login
│   ├── leads.py          # CRUD + CSV import/export
│   ├── google_maps_jobs.py # single scrape
│   ├── multi_search.py   # batch multi-scrape
│   ├── sequences.py      # sequence management
│   ├── messages.py       # send messages
│   ├── pipelines.py      # pipeline CRM
│   ├── tracking.py       # open/click tracking
│   ├── analytics.py      # reporting
│   ├── integrations.py   # Gmail/Instagram OAuth
│   └── webhooks.py       # inbound reply webhooks
├── jobs/            # Celery tasks
└── scheduler.py     # APScheduler (3 jobs)
```
