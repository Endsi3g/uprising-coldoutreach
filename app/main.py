"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
from app.api.v1 import mcp_skills
from app.core.database import Base, engine


import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on startup if they don't exist."""
    # Skip table creation on the main engine if we are in testing mode
    if os.getenv("TESTING") != "true":
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logging.warning(f"Could not initialize database tables: {e}")
    yield


app = FastAPI(
    title="Uprising ColdOutreach API",
    description="GoHighLevel-like prospecting backend — open-source, 100% free.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — explicit origins to comply with CORS spec (wildcard + credentials not allowed)
_CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
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
app.include_router(mcp_skills.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Uprising ColdOutreach", "version": "2.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# Serve Frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "prospectai", "dist")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # API and Docs routes are already handled by routers above
        if full_path == "" or full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
             return None # Let FastAPI handle it
        
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))
