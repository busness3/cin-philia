"""Point d'entrée FastAPI — Reveal You backend (prototype).

Principe de confidentialité appliqué dans toute l'app : aucune photo
utilisateur n'est jamais écrite sur disque, en base, ou dans les logs.
Voir docs/CLAUDE.md § Principes de confidentialité des données.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import diagnostics, health
from app.config import settings
from app.db import Base, engine
from app.models import diagnostic_result  # noqa: F401 — enregistre le modèle avant create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prototype uniquement : création directe des tables au démarrage. En
    # production, remplacer par de vraies migrations (Alembic).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Reveal You API",
    description="Backend du pilier Physique — diagnostic colorimétrie + morphologie.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(diagnostics.router, prefix="/api/v1/diagnostics", tags=["diagnostics"])
