"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    analytics,
    auth,
    google_maps_jobs,
    integrations,
    leads,
    messages,
    multi_search,
    pipelines,
    sequences,
    tracking,
    webhooks,
)

app = FastAPI(
    title="Uprising ColdOutreach API",
    description="GoHighLevel-like prospecting backend — open-source, 100% free.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(google_maps_jobs.router)
app.include_router(multi_search.router)
app.include_router(sequences.router)
app.include_router(messages.router)
app.include_router(pipelines.router)
app.include_router(tracking.router)
app.include_router(analytics.router)
app.include_router(integrations.router)
app.include_router(webhooks.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Uprising ColdOutreach", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
